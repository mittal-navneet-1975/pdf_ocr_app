from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import subprocess
import os
import tempfile

app = FastAPI()

# CORS - allow your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pdfocr-n7gwo6r0c-navneet-mittals-projects.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use temp directory for Vercel (ephemeral filesystem)
TEMP_DIR = tempfile.gettempdir()
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(TEMP_DIR, "output")
SPECS_DIR = os.path.join(TEMP_DIR, "specs")
KEYS_FILE = os.path.join(CURRENT_DIR, "keys.txt")

# Create directories if they don't exist
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(SPECS_DIR, exist_ok=True)

print(f"[STARTUP] CURRENT_DIR: {CURRENT_DIR}")
print(f"[STARTUP] TEMP_DIR: {TEMP_DIR}")
print(f"[STARTUP] JSON_DIR: {JSON_DIR}")
print(f"[STARTUP] KEYS_FILE: {KEYS_FILE}")

# Nanonets config
API_KEY = "dcc5b694-96c8-11f0-b983-1ad2fa14c17a"
NANONETS_URL = "https://extraction-api.nanonets.com/extract"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

@app.get("/")
def read_root():
    print("[API] GET / called")
    return {"message": "FastAPI backend is running!", "status": "ok"}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Process PDF using Nanonets API and optionally run parser.
    """
    try:
        print(f"\n[API] POST /upload-pdf/ - Received file: {file.filename}")
        print(f"[API] Content-Type: {file.content_type}")
        
        # Read file content into memory
        pdf_content = await file.read()
        print(f"[API] File size: {len(pdf_content)} bytes")
        
        # Send to Nanonets API
        files = {"file": (file.filename, pdf_content, "application/pdf")}
        data = {"output_type": "flat-json"}
        
        print(f"[API] Calling Nanonets API...")
        response = requests.post(
            NANONETS_URL, 
            headers=HEADERS, 
            files=files, 
            data=data,
            timeout=60
        )
        
        print(f"[API] Nanonets response status: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        print(f"[API] Nanonets API success")
        
        # Normalize content if needed
        if "content" in result and isinstance(result["content"], str):
            try:
                result["content"] = json.loads(result["content"])
            except json.JSONDecodeError:
                pass
        
        # Save JSON output
        name_without_ext = os.path.splitext(file.filename)[0]
        json_output_path = os.path.join(JSON_DIR, f"{name_without_ext}.json")
        
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        print(f"[API] JSON saved: {json_output_path}")
        
        # Try to run parser if it exists
        content = result.get("content", {})
        product_name = content.get("product_name") or content.get("product") or ""
        company_name = content.get("company_name") or content.get("supplier") or content.get("manufacturing_vendor_site_name") or ""
        
        product_key = extract_keywords(product_name)
        company_key = extract_keywords(company_name)
        
        print(f"[API] Dynamic keywords: Product='{product_key}', Company='{company_key}'")
        
        if product_key and company_key:
            parser_file = f"{product_key}_{company_key}.py"
            parser_path = os.path.join(CURRENT_DIR, parser_file)
            
            if os.path.exists(parser_path):
                try:
                    print(f"[API] Running parser: {parser_file}")
                    subprocess.run(
                        ["python", parser_path, json_output_path],
                        check=True,
                        cwd=CURRENT_DIR,
                        capture_output=True
                    )
                    print(f"[API] Parser executed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"[API] Parser error: {e}")
            else:
                print(f"[API] Parser not found: {parser_file}")
        
        # Check if HTML report was generated
        html_report_content = None
        html_files = [f for f in os.listdir(JSON_DIR) if f.endswith('_report.html')]
        if html_files:
            # Get the most recently created HTML file
            html_files.sort(key=lambda f: os.path.getmtime(os.path.join(JSON_DIR, f)), reverse=True)
            html_file_path = os.path.join(JSON_DIR, html_files[0])
            try:
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_report_content = f.read()
                print(f"[API] HTML report loaded: {html_files[0]}")
            except Exception as e:
                print(f"[API] Error reading HTML: {e}")
        
        # Return success with JSON data and HTML report
        print(f"[API] Returning success response")
        return {
            "success": True,
            "filename": file.filename,
            "data": result,
            "htmlReport": html_report_content
        }
        
    except requests.exceptions.RequestException as e:
        print(f"[API] Nanonets API error: {str(e)}")
        return {
            "success": False,
            "error": f"Nanonets API error: {str(e)}"
        }
    except Exception as e:
        print(f"[API] Processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Processing error: {str(e)}"
        }

def extract_keywords(name):
    """
    Extract a meaningful keyword from a product name.
    Ignores common words like 'Non', 'GMO', 'Soya', 'Whey', 'Powder', etc.
    """
    if not name:
        return None
    ignore_words = {"non", "gmo", "soya", "powder", "permeate", "milk", "optilec", "optileec"}
    words = [w for w in name.split() if w.lower() not in ignore_words]
    if not words:
        return None
    return words[0].strip()

@app.get("/health")
def health_check():
    print("[API] GET /health called")
    return {"status": "healthy", "service": "PDF OCR API"}
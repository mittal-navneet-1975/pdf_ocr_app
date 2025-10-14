from fastapi import FastAPI, UploadFile, File, Response, HTTPException
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
        "https://pdfocr-2kqm0juns-navneet-mittals-projects.vercel.app",
        "https://pdfocrapp.vercel.app",
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
OUTPUT_DIR = os.path.join(TEMP_DIR, "output")
SPECS_DIR = os.path.join(TEMP_DIR, "specs")
KEYS_FILE = os.path.join(CURRENT_DIR, "keys.txt")

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SPECS_DIR, exist_ok=True)

print(f"[BACKEND] CURRENT_DIR: {CURRENT_DIR}")
print(f"[BACKEND] TEMP_DIR: {TEMP_DIR}")
print(f"[BACKEND] OUTPUT_DIR: {OUTPUT_DIR}")
print(f"[BACKEND] KEYS_FILE: {KEYS_FILE}")

# Nanonets config
API_KEY = os.environ.get("NANONETS_API_KEY", "dcc5b694-96c8-11f0-b983-1ad2fa14c17a")
NANONETS_URL = "https://extraction-api.nanonets.com/extract"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!", "status": "ok"}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Process PDF using Nanonets API and optionally run parser.
    Save report HTML to /tmp/output and return its filename.
    """
    try:
        print(f"\n[BACKEND] Received file: {file.filename}")

        # Read file content into memory
        pdf_content = await file.read()

        # Send to Nanonets API
        files = {"file": (file.filename, pdf_content, "application/pdf")}
        data = {"output_type": "flat-json"}

        print(f"[BACKEND] Calling Nanonets API...")
        response = requests.post(
            NANONETS_URL,
            headers=HEADERS,
            files=files,
            data=data,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        # Normalize content if needed
        if "content" in result and isinstance(result["content"], str):
            try:
                result["content"] = json.loads(result["content"])
            except json.JSONDecodeError:
                pass

        # Save JSON output
        name_without_ext = os.path.splitext(file.filename)[0]
        json_output_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.json")

        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print(f"[BACKEND] JSON saved: {json_output_path}")

        # Try to run parser if it exists
        content = result.get("content", {})
        product_name = content.get("product_name") or content.get("product") or ""
        company_name = content.get("company_name") or content.get("supplier") or content.get("manufacturing_vendor_site_name") or ""

        product_key = extract_keywords(product_name)
        company_key = extract_keywords(company_name)

        print(f"[BACKEND] Dynamic keywords: Product='{product_key}', Company='{company_key}'")

        html_report_filename = None
        html_report_path = None

        if product_key and company_key:
            parser_file = f"{product_key}_{company_key}.py"
            parser_path = os.path.join(CURRENT_DIR, parser_file)

            if os.path.exists(parser_path):
                try:
                    print(f"[BACKEND] Running parser: {parser_file}")
                    subprocess.run(
                        ["python", parser_path, json_output_path],
                        check=True,
                        cwd=CURRENT_DIR
                    )
                    print(f"[BACKEND] Parser executed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"[BACKEND] Parser error: {e}")
            else:
                print(f"[BACKEND] Parser not found: {parser_file}")

        # Generate a simple HTML report (or use parser output if available)
        html_report_filename = f"{file.filename}_{get_timestamp()}_report.html"
        html_report_path = os.path.join(OUTPUT_DIR, html_report_filename)
        html_content = f"""
        <html>
        <head><title>Report for {file.filename}</title></head>
        <body>
        <h2>Report for {file.filename}</h2>
        <pre>{json.dumps(result, indent=2, ensure_ascii=False)}</pre>
        </body>
        </html>
        """
        with open(html_report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[BACKEND] Report written to: {html_report_path}")

        # Return success with JSON data and report filename
        return {
            "success": True,
            "filename": file.filename,
            "data": result,
            "outputs": [html_report_filename]
        }

    except requests.exceptions.RequestException as e:
        print(f"[BACKEND] Nanonets API error: {str(e)}")
        return {
            "success": False,
            "error": f"Nanonets API error: {str(e)}"
        }
    except Exception as e:
        print(f"[BACKEND] Processing error: {str(e)}")
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

def get_timestamp():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PDF OCR API"}

@app.get("/api/output/{filename:path}")
def get_output_file(filename: str):
    """
    Serve a generated report saved under /tmp/output/<filename>.
    NOTE: this relies on the report being present in the function's temp dir.
    """
    safe_base = os.path.normpath(OUTPUT_DIR)
    target = os.path.normpath(os.path.join(safe_base, filename))

    if not target.startswith(safe_base):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not os.path.exists(target):
        raise HTTPException(status_code=404, detail="Not found")

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    return Response(content=content, media_type="text/html")
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from mangum import Mangum

app = FastAPI()

# CORS - allow your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pdfocrapp.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nanonets config
API_KEY = "dcc5b694-96c8-11f0-b983-1ad2fa14c17a"
NANONETS_URL = "https://extraction-api.nanonets.com/extract"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!", "status": "ok"}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Process PDF directly without saving to disk.
    Calls Nanonets API and returns the result.
    """
    try:
        # Read file content into memory
        pdf_content = await file.read()
        
        # Send directly to Nanonets API
        files = {"file": (file.filename, pdf_content, "application/pdf")}
        data = {"output_type": "flat-json"}
        
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
        
        return {
            "success": True,
            "filename": file.filename,
            "data": result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Nanonets API error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing error: {str(e)}"
        }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "PDF OCR API"}

# Vercel serverless handler
handler = Mangum(app)

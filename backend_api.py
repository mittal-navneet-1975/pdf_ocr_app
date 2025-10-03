from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import subprocess
import os

app = FastAPI()

# Allow frontend to call backend (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INPUT_DIR = r"C:\Users\vibho\Downloads\Engineering\Test\docs"
OUTPUT_DIR = r"C:\Users\vibho\Downloads\Engineering\Test\output"

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded file to INPUT_DIR
    os.makedirs(INPUT_DIR, exist_ok=True)
    file_path = os.path.join(INPUT_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call nanoNets.py to process all PDFs in INPUT_DIR
    try:
        subprocess.run(["python", "nanoNets.py"], check=True)
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e)}

    # List output files
    output_files = [
        f for f in os.listdir(OUTPUT_DIR)
        if f.lower().endswith(".json") or f.lower().endswith(".html")
    ]
    return {"success": True, "outputs": output_files}

@app.get("/output/{filename}")
def get_output_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    with open(file_path, "rb") as f:
        return f.read()
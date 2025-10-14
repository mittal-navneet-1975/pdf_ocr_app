import os
import sys
import requests
import json
import subprocess
import tempfile

# Fix Windows encoding issue
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === CONFIG ===

CURRENT_DIR = os.getcwd()
INPUT_DIR = os.path.join(CURRENT_DIR, "pdf")
json_dir = os.path.join(CURRENT_DIR, "output")

# Create directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(json_dir, exist_ok=True)

print(f"[DEBUG] TEMP_DIR: {CURRENT_DIR}")
print(f"[DEBUG] INPUT_DIR: {INPUT_DIR}")
print(f"[DEBUG] json_dir: {json_dir}")

API_KEY = "dcc5b694-96c8-11f0-b983-1ad2fa14c17a"
URL = "https://extraction-api.nanonets.com/extract"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# === UTILITIES ===
def normalize_content(content):
    """Flatten JSON content to a single dict so parser works correctly."""
    flat_content = {}
    if isinstance(content, dict):
        flat_content.update(content)
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                flat_content.update(item)
    return flat_content

def extract_keywords(name):
    """
    Extract a meaningful keyword from a product name.
    Ignores common words like 'Non', 'GMO', 'Soya', 'Whey', 'Powder', etc.
    Picks the first significant word.
    """
    if not name:
        return None
    ignore_words = {"non", "gmo", "soya", "powder", "permeate", "milk", "OPTILEC", "OPTILEEC", "optileec"}
    words = [w for w in name.split() if w.lower() not in ignore_words]
    if not words:
        return None
    return words[0].strip()

# === PROCESS PDF ===
def process_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(json_dir, f"{name_without_ext}.json")

    print(f"\n[PROCESS] Processing: {filename}")
    print(f"[DEBUG] PDF path: {pdf_path}")
    print(f"[DEBUG] Output path: {output_path}")

    # Send PDF to Nanonets API
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": f}
            data = {"output_type": "flat-json"}
            response = requests.post(URL, headers=HEADERS, files=files, data=data)
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return

    try:
        response_data = response.json()
    except ValueError:
        print(f"[ERROR] Response is not valid JSON for {filename}")
        return

    # Decode content if it's a string
    if "content" in response_data and isinstance(response_data["content"], str):
        try:
            response_data["content"] = json.loads(response_data["content"])
        except json.JSONDecodeError:
            pass

    # Normalize content
    if "content" in response_data:
        response_data["content"] = normalize_content(response_data["content"])

    # Save normalized JSON
    os.makedirs(json_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=4)
    print(f"[OK] Saved JSON: {output_path}")

    # Extract product and company
    content = response_data.get("content", {})
    product_name = content.get("product_name") or content.get("product") or content.get("sample_type") or ""
    company_name = content.get("company_name") or content.get("supplier") or content.get("sample_name") or content.get("customer_sample_name") or content.get("manufacturing_vendor_site_name") or ""

    # Dynamic keywords
    product_key = extract_keywords(product_name)
    company_key = extract_keywords(company_name)
    print(f"[KEYWORDS] Dynamic keywords: Product='{product_key}', Company='{company_key}'")

    # Build parser filename and execute if exists
    if product_key and company_key:
        parser_file = f"{product_key}_{company_key}.py"
        parser_path = os.path.join(os.getcwd(), parser_file)

        if os.path.exists(parser_path):
            try:
                subprocess.run(["python", parser_path, output_path], check=True)
                print(f"[PARSER] {parser_file} executed successfully for {filename}")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Error running {parser_file} for {filename}: {e}")
        else:
            print(f"[WARN] {parser_file} not found. Skipping parser execution for {filename}.")
    else:
        print(f"[WARN] No dynamic keywords found for {filename}. Parser not executed.")

# === MAIN ===
def main():
    print(f"[DEBUG] Checking INPUT_DIR: {INPUT_DIR}")
    print(f"[DEBUG] INPUT_DIR exists: {os.path.exists(INPUT_DIR)}")
    
    os.makedirs(json_dir, exist_ok=True)
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    print(f"[DEBUG] Found PDF files: {pdf_files}")
    print(f"[DEBUG] Number of PDFs: {len(pdf_files)}")

    if not pdf_files:
        print("[WARN] No PDF files found in input directory.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        process_pdf(pdf_path)

    print("\n[OK] All PDFs processed successfully.")

if __name__ == "__main__":
    main()
import os
import requests
import json
import subprocess

# === CONFIG ===
INPUT_DIR = r"C:\Test\pdf"
OUTPUT_DIR = r"C:\Test\output"
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
    output_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.json")

    print(f"\n📄 Processing: {filename}")

    # Send PDF to Nanonets API
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {"output_type": "flat-json"}
        response = requests.post(URL, headers=HEADERS, files=files, data=data)

    try:
        response_data = response.json()
    except ValueError:
        print(f"❌ Error: Response is not valid JSON for {filename}")
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Saved JSON: {output_path}")

    # Extract product and company
    content = response_data.get("content", {})
    product_name = content.get("product_name") or content.get("product") or ""
    company_name = content.get("company_name") or content.get("supplier") or content.get("manufacturing_vendor_site_name") or ""

    # Dynamic keywords
    product_key = extract_keywords(product_name)
    company_key = extract_keywords(company_name)
    print(f"🚀 Dynamic keywords: Product='{product_key}', Company='{company_key}'")

    # Build parser filename and execute if exists
    if product_key and company_key:
        parser_file = f"{product_key}_{company_key}.py"
        parser_path = os.path.join(os.getcwd(), parser_file)

        if os.path.exists(parser_path):
            try:
                subprocess.run(["python", parser_path, output_path], check=True)
                print(f"🚀 {parser_file} executed successfully for {filename}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running {parser_file} for {filename}: {e}")
        else:
            print(f"⚠️ {parser_file} not found. Skipping parser execution for {filename}.")
    else:
        print(f"⚠️ No dynamic keywords found for {filename}. Parser not executed.")

# === MAIN ===
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in input directory.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        process_pdf(pdf_path)

    print("\n✅ All PDFs processed successfully.")

if __name__ == "__main__":
    main()

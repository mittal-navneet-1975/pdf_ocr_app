import os
import requests
import json
import subprocess

# Input/output directories
INPUT_DIR = r"C:\Test\pdf"
OUTPUT_DIR = r"C:\Test\output"
API_KEY = "dcc5b694-96c8-11f0-b983-1ad2fa14c17a"
URL = "https://extraction-api.nanonets.com/extract"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def normalize_content(content):
    """
    Flatten JSON content to a single dict of key-value pairs so parser works correctly.
    Handles cases where content is a list of dicts or nested structures.
    """
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
    Extract significant keyword from a name.
    For simplicity, take first word or remove generic words.
    """
    if not name:
        return None
    # Use the first word as the keyword
    return name.split()[0]

def process_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.json")

    print(f"\n📄 Processing: {filename}")

    # Send PDF to API
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

    # Normalize content so parser can read keys
    if "content" in response_data:
        response_data["content"] = normalize_content(response_data["content"])

    # Save normalized JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Saved JSON: {output_path}")

    # Extract product and company names
    product_name = response_data.get("content", {}).get("product_name", "")
    company_name = response_data.get("content", {}).get("company_name", "")

    # Dynamically pick keywords
    product_key = extract_keywords(product_name)
    company_key = extract_keywords(company_name)
    print(f"🚀 Dynamic keywords: Product='{product_key}', Company='{company_key}'")

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

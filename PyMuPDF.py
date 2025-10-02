import requests
import json

def ocr_space_file(filename, overlay=False, api_key='K89109351088957', language='eng'):
    """
    OCR.space API request with local file.
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response. Defaults to False.
    :param api_key: OCR.space API key.
    :param language: Language code to be used in OCR. Defaults to 'eng'.
    :return: Result in JSON format (dict).
    """
    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
    }
    
    with open(filename, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data=payload
        )
    
    result = r.content.decode()
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"Error": "Failed to parse OCR API response"}

def save_rows_to_json(ocr_result, output_file='output.json'):
    """
    Save OCR output to JSON with 1 row per PDF line.
    :param ocr_result: OCR API result dict.
    :param output_file: JSON file to save.
    """
    rows = []

    if 'ParsedResults' in ocr_result:
        for parsed in ocr_result['ParsedResults']:
            text = parsed.get('ParsedText', '')
            # Split text into lines and strip extra spaces
            for line in text.splitlines():
                line = line.strip()
                if line:  # ignore empty lines
                    rows.append(line)
    else:
        rows.append("OCR Failed or no text found.")

    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"Rows": rows}, f, ensure_ascii=False, indent=4)
    print(f"OCR rows saved to {output_file}")

# Main execution
if __name__ == "__main__":
    pdf_file = 'amol_kate.pdf'
    ocr_result = ocr_space_file(pdf_file)
    save_rows_to_json(ocr_result)

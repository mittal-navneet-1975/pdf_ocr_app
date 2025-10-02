import requests
import json

def ocr_space_file(filename, overlay=False, api_key='K89109351088957', language='eng'):
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
    
    try:
        return r.json()
    except json.JSONDecodeError:
        return {"Error": "Failed to parse OCR API response"}

def save_extracted_rows_to_json(ocr_result, output_file='output.json'):
    """
    Save OCR output to JSON with one array element per line from PDF.
    """
    rows = []

    if 'ParsedResults' in ocr_result:
        for parsed in ocr_result['ParsedResults']:
            text = parsed.get('ParsedText', '')
            # Split by all types of line breaks and strip spaces
            for line in text.replace('\r', '\n').split('\n'):
                line = line.strip()
                if line:  # skip empty lines
                    rows.append(line)
    else:
        rows.append("OCR Failed or no text found.")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"ExtractedText": rows}, f, ensure_ascii=False, indent=4)

    print(f"OCR lines saved to {output_file}")

# Main
if __name__ == "__main__":
    pdf_file = 'amol_kate.pdf'
    ocr_result = ocr_space_file(pdf_file)
    save_extracted_rows_to_json(ocr_result)

import requests
import json
import re

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

def structure_ocr_text(parsed_text):
    """
    Convert raw OCR ParsedText into structured dictionary.
    Detects 'key : value' patterns and groups remaining lines.
    """
    structured = {}
    lines = parsed_text.replace('\r', '\n').split('\n')
    remaining_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Detect key : value or key - value patterns
        match = re.match(r"(.+?)\s*[:\-]\s*(.+)", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            structured[key] = value
        else:
            remaining_lines.append(line)

    if remaining_lines:
        structured["OtherInfo"] = remaining_lines

    return structured

def save_structured_json(ocr_result, output_file='structured_output.json'):
    """
    Process OCR result and save structured JSON.
    """
    structured_list = []

    if 'ParsedResults' in ocr_result:
        for parsed in ocr_result['ParsedResults']:
            parsed_text = parsed.get('ParsedText', '')
            structured_data = structure_ocr_text(parsed_text)
            structured_list.append(structured_data)
    else:
        structured_list.append({"Error": "OCR Failed or no text found."})

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_list, f, ensure_ascii=False, indent=4)

    print(f"Structured OCR data saved to {output_file}")

# Main
if __name__ == "__main__":
    pdf_file = 'amol_kate.pdf'
    ocr_result = ocr_space_file(pdf_file)
    save_structured_json(ocr_result)

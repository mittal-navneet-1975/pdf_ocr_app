import json
import re
import os
import glob
import subprocess
import sys
from datetime import datetime

# === CONFIG ===
json_dir = r"C:\pdf_ocr\pdf_ocr_app\output"
keys_file = r"C:\pdf_ocr\pdf_ocr_app\keys.txt"
specs_file = r"C:\pdf_ocr\pdf_ocr_app\specs\LECITHIN.txt"

compliance_keys = [
    "moisture", "acetone", "peanut", "peroxide", "gardner", "hexane", "toluene",
    "enterobacteriaceae", "e_coli", "salmonella"
]

param_aliases = {
    "moisture": ["moisture"],
    "acetone": ["acetoneinsoluble"],
    "peanut": ["peanutallerg"],
    # 👇 Explicitly handle color test (so it won’t match toluene)
    "gardner": ["color10solutionintoluene", "color", "color_10_solution_in_toluene"],
    "hexane": ["hexaneinsoluble"],
    "acid_value": ["acidvalue"],
    "peroxide": ["peroxidevalue"],
    # 👇 IMPORTANT: keep toluene separate, do NOT let it match color
    "toluene": ["toluene_residue", "residual_toluene"],
    "viscosity": ["viscosity"],
    "total_plate_count": ["totalplatecount"],
    "enterobacteriaceae": ["enterobacteriaceae"],
    "e_coli": ["ecoli"],
    "salmonella": ["salmonella375g", "salmonella"],
    "yeast_and_mold": ["yeastandmoulds"],
}

# === FIND JSON FILE ===
if len(sys.argv) > 1:
    json_file = sys.argv[1]
else:
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {json_dir}")
    json_file = json_files[0]

print(f"Using JSON file: {json_file}")

# === LOAD JSON ===
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
content = data.get("content", {})

# === DETECT PRODUCT & COMPANY ===
product_name = (content.get("product_name") or content.get("product") or "").strip()
company_name = content.get("company_name") or content.get("supplier") or content.get("manufacturing_vendor_site_name") or ""
print("Detected product:", product_name)
print("Detected company:", company_name)

# === LOAD KEYS FROM FILE ===
raw_keys = []
product_keywords = ["Lecithin", "Whey", "SMP", "Permeate", "Casein"]
dynamic_product = next((kw for kw in product_keywords if kw.lower() in product_name.lower()), product_name.split()[0] if product_name else "")
dynamic_company = company_name.split()[0] if company_name else ""
product_company_key = f"{dynamic_product}_{dynamic_company}".replace(" ", "_").replace("-", "_").lower()

if os.path.exists(keys_file):
    with open(keys_file, "r", encoding="utf-8") as f:
        for line in f:
            if "- Mandatory Values -" not in line:
                continue
            product_part, keys_part = line.split("- Mandatory Values -", 1)
            product_part_norm = product_part.strip().strip('"').replace(" ", "_").replace("-", "_").lower()
            keys_match = re.search(r"\{(.*?)\}", keys_part)
            keys_list = [k.strip().strip('"').strip("'") for k in keys_match.group(1).split(",")] if keys_match else []
            if product_part_norm == product_company_key:
                raw_keys = keys_list
                break

print(f"Dynamic keywords: Product='{dynamic_product}', Company='{dynamic_company}'")
print("Keys of Interest:", raw_keys)

# === LOAD SPECS FROM LECITHIN.txt ===
specs_dict = {}
if os.path.exists(specs_file):
    with open(specs_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "|" in line:
                parts = line.split("|", 1)
                if len(parts) == 2:
                    key = re.sub(r"[^a-z0-9]", "", parts[0].strip().lower())
                    specs_dict[key] = parts[1].strip()
    print(f"Loaded {len(specs_dict)} specs from {specs_file}")

# === HELPER FUNCTIONS ===
def normalize_text(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower()) if s else ""

def parse_interval(value, is_spec=False):
    if value is None: return None
    s = str(value).lower().strip()

    if any(x in s for x in ["absent", "not detect", "nd", "negative"]):
        return {"min":0,"max":0}

    m = re.match(r'^\s*([<>]=?)\s*([\d,]*\.?\d+)', s)
    if m:
        comp, num = m.groups()
        num = float(num.replace(",", ""))
        if comp in ("<", "<="): return {"min":0,"max":num}
        if comp in (">", ">="): return {"min":num,"max":None}

    if "max" in s:
        n = re.search(r"[-+]?\d*\.?\d+", s.replace(",", ""))
        return {"min":0,"max":float(n.group(0))} if n else None
    if "min" in s:
        n = re.search(r"[-+]?\d*\.?\d+", s.replace(",", ""))
        return {"min":float(n.group(0)),"max":None} if n else None

    if "-" in s or " to " in s:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", s)
        if len(nums) >= 2:
            a, b = float(nums[0]), float(nums[1])
            return {"min":min(a,b),"max":max(a,b)}

    n = re.search(r"[-+]?\d*\.?\d+", s.replace(",", ""))
    if n:
        num = float(n.group(0))
        return {"min":0,"max":num} if is_spec else {"min":num,"max":num}

    return None

def interval_within(result_int, spec_int):
    if not result_int or not spec_int:
        return False, "Non-numeric result or missing spec"

    result_max = result_int.get("max", 0)
    spec_max = spec_int.get("max", None)

    if spec_max == 0:
        if result_max == 0:
            return True, "Within Spec"
        return False, "Exceeds Spec"

    if spec_max is not None and result_max > spec_max:
        return False, "Exceeds upper bound"
    if spec_int.get("min") is not None and result_int.get("min") < spec_int["min"]:
        return False, "Below lower bound"

    return True, "Within Spec"

def check_or_specs(result_int, spec_value):
    if " OR " not in spec_value.upper():
        spec_int = parse_interval(spec_value, is_spec=True)
        return interval_within(result_int, spec_int)
    
    or_parts = re.split(r'\s+OR\s+', spec_value, flags=re.IGNORECASE)
    for spec_part in or_parts:
        spec_int = parse_interval(spec_part.strip(), is_spec=True)
        is_compliant, reason = interval_within(result_int, spec_int)
        if is_compliant:
            return True, f"Within Spec (matched: {spec_part.strip()})"
    
    return False, f"Does not match any OR condition"

def get_result(key):
    key_norm = normalize_text(key)
    aliases = param_aliases.get(key, [key])
    
    for k in content.keys():
        k_norm = normalize_text(k)
        #print(f"  k_norm: {k_norm}")
        # 🚫 Prevent wrong match: color test should not be read as toluene
        if k_norm.startswith("color10solutionintoluene") or key_norm == "toluene":
            continue
        if k_norm.endswith("result"):
            if key_norm in k_norm or any(normalize_text(alias) in k_norm for alias in aliases):
                print(f"  Found result: {k}")
                return content[k]
    
    print(f"  Result NOT FOUND for key: {key}")
    return None

def get_spec(key):
    key_norm = normalize_text(key)
    
    if key_norm in specs_dict:
        print(f"  Spec found: {key}")
        return specs_dict[key_norm]
    
    aliases = param_aliases.get(key, [key])
    for alias in aliases:
        alias_norm = normalize_text(alias)
        if alias_norm in specs_dict:
            print(f"  Spec found via alias '{alias}'")
            return specs_dict[alias_norm]
    
    for spec_key in specs_dict.keys():
        if key_norm in spec_key or spec_key in key_norm:
            print(f"  Spec found via partial match")
            return specs_dict[spec_key]
    
    print(f"  Spec NOT FOUND for key: {key}")
    return None

def get_salmonella_sample_size(key):
    if "salmonella" not in key.lower():
        return None
    
    sample_patterns = ["15x25 g", "5x75 g", "3x125 g", "375 g", "15x25g", "5x75g", "3x125g", "375g"]
    
    for k, v in content.items():
        if "salmonella" in k.lower():
            value_str = str(v)
            for pattern in sample_patterns:
                if pattern.lower() in value_str.lower():
                    return pattern
    
    return None

# === HTML REPORT ===
# Make sure Lecithin_ADM folder exists inside output
# report_dir = os.path.join(os.path.dirname(json_file), "Lecithin_ADM")
# os.makedirs(report_dir, exist_ok=True)

# # Create report filename (same base name as JSON, but with _report.html)
# json_name = os.path.splitext(os.path.basename(json_file))[0]
# output_file = os.path.join(report_dir, f"{json_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_report.html")
output_file = os.path.splitext(json_file)[0] + f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}_report.html"
with open(output_file, "w", encoding="utf-8") as out:
    out.write("<html><body>\n")
    out.write(f"<h1>Lab Report for {product_name} ({company_name})</h1>\n")
    #out.write(f"<p>Source JSON: {os.path.basename(json_file)} | Spec source: {os.path.basename(specs_file)}</p>\n")
    out.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
    out.write("<tr><th>Parameter</th><th>Result</th><th>Spec</th><th>Status</th></tr>\n")

    non_compliant_found = False

    for key in raw_keys:
        raw_result = get_result(key)
        raw_spec = get_spec(key)

        salmonella_sample = get_salmonella_sample_size(key)
        raw_result_str = str(raw_result).strip() if raw_result is not None else "-"
        raw_result_display = f"{raw_result_str} / {salmonella_sample}" if salmonella_sample and raw_result is not None else raw_result_str
        raw_spec_str = str(raw_spec).strip() if raw_spec is not None else "-"

        print(f"Processing '{key}': Result={raw_result_str}, Spec={raw_spec_str}")

        res_int = parse_interval(raw_result, is_spec=False)

        if raw_result is None or raw_spec is None:
            status = "Missing"
            color = "red" if key in compliance_keys else "gray"
            reason = "Missing result or spec"
            is_compliant = False
        else:
            is_compliant, reason = check_or_specs(res_int, raw_spec)
            status = "Within Spec" if is_compliant else "Exceeds Spec"
            color = "green" if is_compliant else "red"

        if key in compliance_keys and not is_compliant:
            non_compliant_found = True

        out.write(f"<tr>")
        out.write(f"<td>{key}</td><td>{raw_result_display}</td><td>{raw_spec_str}</td>")
        if key in compliance_keys:
            out.write(f"<td style='color:{color}; font-weight:bold'>{status}")
        else:
            out.write(f"<td>{status}")
        if reason and status != "Within Spec":
            out.write(f"<br><small>Reason: {reason}</small>")
        out.write("</td></tr>\n")

    out.write("</table>\n")
    if non_compliant_found:
        out.write(f"<h3 style='color:red'>This report has Non-Compliance (based on selected parameters)</h3>\n")
    else:
        out.write(f"<h3 style='color:green'>This report is Fully compliant (based on selected parameters)</h3>\n")
    out.write("</body></html>\n")

print(f"\nReport written to: {output_file}")
# === RUN CLEANUP SCRIPT ===
try:
    subprocess.run(["python", "cleanup_files.py"], check=True)
    print("cleanup_files.py executed successfully.")
except Exception as e:
    print(f"Error running cleanup_files.py: {e}")
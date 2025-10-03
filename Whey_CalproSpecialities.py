import json
import re
import os
import glob
import sys
import subprocess
from datetime import datetime

# === CONFIG ===
json_dir = r"C:\Users\vibho\Downloads\Engineering\Test\output"
keys_file = r"C:\Users\vibho\Downloads\Engineering\Test\keys.txt"
specs_file = r"C:\Users\vibho\Downloads\Engineering\Test\WHEY.txt"

compliance_keys = [
    "moisture", "total_plate_count", "enterobacteriaceae", "salmonella", "yeast_and_mold"
]

param_aliases = {
    "moisture": ["moisturebymass"],
    "total_plate_count": ["standardplatecount"],
    "enterobacteriaceae": ["enterobacteriaceae"],
    "salmonella": ["salmonella"],
    "yeast_and_mold": ["yeastmould"],
    "colour_appearance": ["colourappearance"],
    "taste_flavour": ["tasteflavour"],
    "milk_solids": ["milksolids"],
    "milk_fat": ["milkfatbymass"],
    "protein": ["proteincontent"],
    "ash": ["ashcontent"],
    "ph_of_10": ["phof10wvsolutioninwater"],
    "bulk_density": ["bulkdensity"],
    "scorched_particles": ["scorchedparticlesequivalenttoadpidisc"],
    "titrable_acidity": ["titrableacidity"],
    "plate_count": ["platecount"],
    "coliform_count": ["coliformcount"],
    "e_coli": ["ecoli"],
    "shigella": ["shigella"],
    "listeria_monocytogenes": ["listeriamonocytogenes"],
    "staphylococcus_aureus": ["staphylococcusaureus"],
    "b_cereus": ["bcereus"]
}

# === FIND JSON FILE ===
json_file = sys.argv[1] if len(sys.argv) > 1 else glob.glob(os.path.join(json_dir, "*.json"))[0]
print(f"Using JSON file: {json_file}")

# === LOAD JSON ===
with open(json_file, "r", encoding="utf-8") as f:
    content = json.load(f).get("content", {})

# === DETECT PRODUCT & COMPANY ===
product_name = (content.get("product_name") or content.get("product") or "").strip()
company_name = content.get("company_name") or content.get("supplier") or content.get("manufacturing_vendor_site_name") or ""
print(f"Product: {product_name} | Company: {company_name}")

# === LOAD KEYS ===
raw_keys = []
product_keywords = ["Whey", "Lecithin", "SMP", "Permeate", "Casein"]
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

print(f"Keys: {raw_keys}")

# === LOAD SPECS ===
specs_dict = {}
if os.path.exists(specs_file):
    with open(specs_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and "|" in line:
                parts = line.strip().split("|", 1)
                if len(parts) == 2:
                    specs_dict[re.sub(r"[^a-z0-9]", "", parts[0].lower())] = parts[1].strip()
    print(f"Loaded {len(specs_dict)} specs")

# === DEBUG: Show what's in JSON ===
print("\n=== DEBUG: All JSON fields ===")
test_fields = [k for k in content.keys() if k.startswith('test_')]
print(f"Found {len(test_fields)} test fields")
for i in range(1, 6):
    p_key = f"test_parameter_{i}"
    r_key = f"observed_results_{i}"
    s_key = f"specifications_{i}"
    if p_key in content:
        print(f"  {i}. param={content[p_key]}")
        print(f"     result={content.get(r_key, 'N/A')}")
        print(f"     spec={content.get(s_key, 'N/A')}")
print("==============================\n")

# === HELPERS ===
def normalize(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower()) if s else ""

def parse_interval(value, is_spec=False):
    if value is None: return None
    s = str(value).lower().strip().replace("—", "-").replace("–", "-")

    if any(x in s for x in ["absent", "not detect", "nd", "negative"]):
        return {"min": 0, "max": 0}

    m = re.match(r'^\s*([<>]=?)\s*([\d,]*\.?\d+)', s)
    if m:
        comp, num = m.groups()
        num = float(num.replace(",", ""))
        return {"min": 0, "max": num} if comp in ("<", "<=") else {"min": num, "max": None}

    if "max" in s or "min" in s:
        n = re.search(r"[\d,]*\.?\d+", s.replace(",", ""))
        if n:
            num = float(n.group(0))
            return {"min": 0, "max": num} if "max" in s else {"min": num, "max": None}

    nums = re.findall(r"[\d,]*\.?\d+", s.replace(",", ""))
    if len(nums) >= 2:
        return {"min": float(nums[0]), "max": float(nums[1])}
    if len(nums) == 1:
        num = float(nums[0])
        return {"min": 0, "max": num} if is_spec else {"min": num, "max": num}

    return None

def check_compliance(result_int, spec_int, raw_result, raw_spec, key):
    # Textual parameters
    if key in ["colour_appearance", "taste_flavour", "scorched_particles"]:
        if raw_result and raw_spec:
            r, s = str(raw_result).lower(), str(raw_spec).lower()
            if r in s or s in r or any(w in s for w in r.split()):
                return True, "Within Spec"
        return False, "Textual mismatch"

    # Range parameters
    if key in ["ph_of_10", "bulk_density"]:
        nums_r = re.findall(r"[\d.]+", str(raw_result))
        nums_s = re.findall(r"[\d.]+", str(raw_spec))
        if nums_r and len(nums_s) >= 2:
            r, low, high = float(nums_r[0]), float(nums_s[0]), float(nums_s[1])
            if low <= r <= high: return True, "Within Spec"
            return False, "Below lower bound" if r < low else "Exceeds upper bound"
        return False, "Non-numeric or missing spec"

    # Numeric comparison
    if not result_int or not spec_int:
        return False, "Non-numeric or missing spec"

    r_max = result_int.get("max", 0)
    s_max = spec_int.get("max")
    s_min = spec_int.get("min")

    if s_max == 0:
        return (True, "Within Spec") if r_max == 0 else (False, "Exceeds Spec")
    if s_max and round(r_max, 2) > round(s_max, 2):
        return False, "Exceeds upper bound"
    if s_min and round(result_int.get("min", 0), 2) < round(s_min, 2):
        return False, "Below lower bound"

    return True, "Within Spec"

def check_or_specs(result_int, spec_value, raw_result, key):
    if " OR " not in spec_value.upper():
        spec_int = parse_interval(spec_value, is_spec=True)
        return check_compliance(result_int, spec_int, raw_result, spec_value, key)
    
    for spec_part in re.split(r'\s+OR\s+', spec_value, flags=re.IGNORECASE):
        spec_int = parse_interval(spec_part.strip(), is_spec=True)
        is_ok, _ = check_compliance(result_int, spec_int, raw_result, spec_part.strip(), key)
        if is_ok:
            return True, f"Within Spec (matched: {spec_part.strip()})"
    
    return False, "Does not match any OR condition"

def get_result(key):
    key_norm = normalize(key)
    aliases = param_aliases.get(key, [])
    
    # Search through test_parameter_X fields (correct field name pattern)
    for i in range(1, 25):
        param_key = f"test_parameter_{i}"
        result_key = f"observed_results_{i}"
        
        param_val = content.get(param_key)
        if not param_val:
            continue
        
        param_norm = normalize(param_val)
        
        # Check key match
        if key_norm == param_norm or key_norm in param_norm or param_norm in key_norm:
            result = content.get(result_key)
            if result:
                print(f"  ✓ {key}: {param_val} -> {result}")
                return result
        
        # Check alias match
        for alias in aliases:
            alias_norm = normalize(alias)
            if alias_norm == param_norm or alias_norm in param_norm or param_norm in alias_norm:
                result = content.get(result_key)
                if result:
                    print(f"  ✓ {key} (via {alias}): {param_val} -> {result}")
                    return result
    
    print(f"  ✗ {key} (normalized: {key_norm})")
    return None

def get_spec(key):
    key_norm = normalize(key)
    
    if key_norm in specs_dict:
        return specs_dict[key_norm]
    
    for alias in param_aliases.get(key, [key]):
        alias_norm = normalize(alias)
        if alias_norm in specs_dict:
            return specs_dict[alias_norm]
    
    for spec_key in specs_dict:
        if key_norm in spec_key or spec_key in key_norm:
            return specs_dict[spec_key]
    
    return None

def get_salmonella_sample():
    patterns = ["15x25 g", "5x75 g", "3x125 g", "375 g", "15x25g", "5x75g", "3x125g", "375g"]
    for i in range(1, 21):
        for prefix in ["test_", ""]:
            param_key = f"{prefix}{i}_parameter" if prefix else f"test_parameter_{i}"
            result_key = f"{prefix}{i}_observed_results" if prefix else f"observed_results_{i}"
            
            param_val = str(content.get(param_key, ""))
            if "salmonella" in param_val.lower():
                for field in [result_key, param_key]:
                    val = str(content.get(field, ""))
                    for pattern in patterns:
                        if pattern.lower() in val.lower():
                            return pattern
    return None

# === HTML REPORT ===
output_file = os.path.splitext(json_file)[0] + f"_{datetime.now().strftime('%Y%m%d')}_report.html"
with open(output_file, "w", encoding="utf-8") as out:
    out.write(f"<html><body>\n<h1>Lab Report: {product_name} ({company_name})</h1>\n")
    #out.write(f"<p>JSON: {os.path.basename(json_file)} | Specs: {os.path.basename(specs_file)}</p>\n")
    out.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
    out.write("<tr><th>Parameter</th><th>Result</th><th>Spec</th><th>Status</th></tr>\n")

    non_compliant = False

    for key in raw_keys:
        raw_result = get_result(key)
        raw_spec = get_spec(key)

        sample = get_salmonella_sample() if "salmonella" in key.lower() else None
        result_display = f"{raw_result} / {sample}" if sample and raw_result else (raw_result or "-")
        spec_display = raw_spec or "-"

        result_int = parse_interval(raw_result, is_spec=False)

        if not raw_result or not raw_spec:
            status, color, reason = "Missing", ("red" if key in compliance_keys else "gray"), "Missing result or spec"
            is_ok = False
        else:
            is_ok, reason = check_or_specs(result_int, raw_spec, raw_result, key)
            status, color = ("Within Spec", "green") if is_ok else ("Exceeds Spec", "red")

        if key in compliance_keys and not is_ok:
            non_compliant = True

        out.write(f"<tr><td>{key}</td><td>{result_display}</td><td>{spec_display}</td>")
        out.write(f"<td style='color:{color}{'; font-weight:bold' if key in compliance_keys else ''}'>{status}")
        if not is_ok:
            out.write(f"<br><small>{reason}</small>")
        out.write("</td></tr>\n")

    out.write("</table>\n")
    status_msg = "Non-Compliance" if non_compliant else "Fully compliant"
    status_color = "red" if non_compliant else "green"
    out.write(f"<h3 style='color:{status_color}'>This report has {status_msg} (based on selected parameters)</h3>\n")
    out.write("</body></html>\n")

print(f"\nReport: {output_file}")
# === RUN CLEANUP SCRIPT ===
try:
    subprocess.run(["python", "cleanup_files.py"], check=True)
    print("cleanup_files.py executed successfully.")
except Exception as e:
    print(f"Error running cleanup_files.py: {e}")
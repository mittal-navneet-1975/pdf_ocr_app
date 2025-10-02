import json
import re
import os
import glob
import sys

# === CONFIG ===
json_dir = r"C:\Test\output"
keys_file = r"C:\Test\keys.txt"

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

product_name = (content.get("product_name") or content.get("product") or "").strip()
print("Detected product:", product_name)

# === PARAMETER ALIASES ===
param_aliases = {
    "moisture": ["moisture", "moisture %", "moisture content"],
    "total_plate_count": ["standard plate count", "plate count", "total_plate_count"],
    "enterobacteriaceae": ["enterobacteriaceae"],
    "salmonella": ["salmonella"],
    "yeast_and_mold": ["yeast & mould", "yeast and mould", "yeastmold"],
    "Colour/ Appearance": ["colour/ appearance"],
    "Taste / Flavour": ["taste / flavour"],
    "Milk solids": ["milk solids"],
    "Milk Fat": ["milk fat"],
    "Protein": ["protein", "protein content"],
    "Ash": ["ash", "ash content"],
    "pH of 10": ["ph of 10"],
    "Bulk Density": ["bulk density"],
    "Scorched particles": ["scorched particles"],
    "Titrable acidity": ["titrable acidity"],
    "Plate Count": ["plate count"],
    "Coliform count": ["coliform count"],
    "E.coli": ["e.coli"],
    "Shigella": ["shigella"],
    "Listeria Monocytogenes": ["listeria monocytogenes"],
    "Staphylococcus aureus": ["staphylococcus aureus"],
    "B.Cereus": ["b.cereus"]
}

# === NORMALIZER ===
def normalize_text(s):
    if not s: return ""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return s

# === LOAD KEYS FROM FILE ===
raw_keys = []
if os.path.exists(keys_file):
    with open(keys_file, "r", encoding="utf-8") as f:
        for line in f:
            if "- Mandatory Values -" not in line:
                continue
            product_part, keys_part = line.split("- Mandatory Values -", 1)
            product_part = product_part.strip().strip('"').lower()
            keys_match = re.search(r"\{(.*?)\}", keys_part)
            keys_list = [k.strip().strip('"').strip("'") for k in keys_match.group(1).split(",")] if keys_match else []
            prod_norm = product_name.lower()
            if product_part and (product_part in prod_norm or prod_norm in product_part):
                raw_keys = keys_list
                break

print("Keys of Interest:", raw_keys)

# === HELPER FUNCTIONS ===
_num_re = re.compile(r"[-+]?\d*\.\d+|\d+")

def parse_number(s):
    if s is None: return None
    s = str(s).replace(",", "").strip()
    m = _num_re.search(s)
    return float(m.group(0)) if m else None

def parse_interval(value, is_spec=False):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        v = float(value)
        return {"min": v, "min_inc": True, "max": v, "max_inc": True}

    s = str(value).lower().strip()
    # normalize all dash types and remove spaces around dash
    s = re.sub(r'\s*[-–—]\s*', '-', s)
    s = s.replace("–", "-").replace("—", "-")  # extra safety

    if any(x in s for x in ["absent", "not detect", "nd", "negative"]):
        return {"min": 0, "min_inc": True, "max": 0, "max_inc": True}

    m = re.match(r'^\s*([<>]=?)\s*([0-9,]*\.?[0-9]+)', s)
    if m:
        comp, num_s = m.groups()
        num = float(num_s.replace(",", ""))
        if comp == "<":
            return {"min": 0, "min_inc": True, "max": num, "max_inc": False}
        if comp == "<=":
            return {"min": 0, "min_inc": True, "max": num, "max_inc": True}
        if comp == ">":
            return {"min": num, "min_inc": False, "max": None, "max_inc": False}
        if comp == ">=":
            return {"min": num, "min_inc": True, "max": None, "max_inc": False}

    if "max" in s:
        n = parse_number(s)
        return {"min": 0, "min_inc": True, "max": n, "max_inc": True} if n is not None else None
    if "min" in s:
        n = parse_number(s)
        return {"min": n, "min_inc": True, "max": None, "max_inc": False} if n is not None else None

    if "-" in s:
        nums = _num_re.findall(s)
        if len(nums) >= 2:
            a, b = float(nums[0]), float(nums[1])
            return {"min": min(a, b), "min_inc": True, "max": max(a, b), "max_inc": True}

    n = parse_number(s)
    if n is not None:
        return {"min": n, "min_inc": True, "max": n, "max_inc": True}
    return None

# === INTERVAL CHECK ===
def interval_within(result_int, spec_int, raw_result=None, raw_spec=None, key=None):
    if key in ["Colour/ Appearance", "Taste / Flavour"]:
        if raw_result and raw_spec:
            r, s = raw_result.strip().lower(), raw_spec.strip().lower()
            if r in s or any(word in s for word in r.split()):
                return True, "Within Spec"
        return False, "Textual mismatch"

    if key == "pH of 10" or key == "Bulk Density":
        r = parse_number(raw_result)
        spec_nums = _num_re.findall(str(raw_spec))
        if spec_nums == ['6.00', '-7.20']:
            spec_nums = ['6.0', '7.2']
        if r is not None and len(spec_nums) >= 2:
            low, high = float(spec_nums[0]), float(spec_nums[1])
            r, low, high = round(r, 2), round(low, 2), round(high, 2)
            if low <= r <= high:
                return True, "Within Spec"
            elif r < low:
                return False, "Below lower bound"
            else:
                return False, "Exceeds upper bound"
        return False, "Non-numeric result or missing spec"

    if key == "Scorched particles":
        if raw_result and raw_spec:
            r, s = raw_result.strip().lower(), raw_spec.strip().lower()
            if r == s or (r in s and "max" in s):
                return True, "Within Spec"
        return False, "Textual mismatch"

    if not result_int or not spec_int:
        return False, "Non-numeric result or missing spec"
    if spec_int["max"] is not None and round(result_int["max"], 2) > round(spec_int["max"], 2):
        return False, "Exceeds upper bound"
    if spec_int["min"] is not None and round(result_int["min"], 2) < round(spec_int["min"], 2):
        return False, "Below lower bound"
    return True, "Within Spec"

# === FLEXIBLE GETTER FOR YOUR JSON ===
def get_result_and_spec(key):
    aliases = param_aliases.get(key, [key])
    alias_norms = [normalize_text(a) for a in aliases]

    for i in range(1, 21):
        param_key = f"test_parameter_{i}"
        result_key = f"observed_results_{i}"
        spec_key = f"specification_{i}"

        param_value = content.get(param_key)
        if not param_value:
            continue

        param_norm = normalize_text(str(param_value))
        if any(a in param_norm or param_norm in a for a in alias_norms):
            result = content.get(result_key)
            spec = content.get(spec_key)
            return result, spec
    return None, None

# === REPORT COLORS ===
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# === PRINT REPORT ===
print("\n📊 Lab Report")
print("-"*80)
print(f"{'Parameter':<25} | {'Result':<15} | {'Spec':<30} | Status")
print("-"*80)

non_compliant_found = False

for key in raw_keys:
    raw_result, raw_spec = get_result_and_spec(key)
    raw_result_str = str(raw_result).strip() if raw_result is not None else ""
    raw_spec_str = str(raw_spec).strip() if raw_spec is not None else ""

    res_int = parse_interval(raw_result, is_spec=False)
    spec_int = parse_interval(raw_spec, is_spec=True)

    within, reason = interval_within(res_int, spec_int, raw_result, raw_spec, key)
    status = "Within Spec" if within else "Exceeds Spec" if "Exceeds" in reason else "Out of Spec"

    if not within:
        non_compliant_found = True

    status_colored = f"{GREEN}{status}{RESET}" if status == "Within Spec" else f"{RED}{status}{RESET}"
    print(f"{key:<25} | {raw_result_str:<15} | {raw_spec_str:<30} | {status_colored}")
    if not within and reason not in ["Spec missing / Cannot compare"]:
        print(f"  Reason: {reason}")

print("-"*80)
if non_compliant_found:
    print(f"This report has Non-Compliance")
else:
    print("This report is ✅ Fully compliant")

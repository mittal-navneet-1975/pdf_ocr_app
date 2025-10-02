import json
import re
import os
import glob

# === CONFIG ===
json_dir = r"C:\Test\output"   # directory where JSON files are stored
keys_file = r"C:\Test\keys.txt"

# === FIND JSON FILES ===
json_files = glob.glob(os.path.join(json_dir, "*.json"))
if not json_files:
    raise FileNotFoundError(f"No JSON files found in {json_dir}")

# If multiple JSONs, pick the first one (or loop through if you want all)
json_file = json_files[0]
print(f"Using JSON file: {json_file}")

# === LOAD JSON ===
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
content = data.get("content", {})

product_name = (content.get("product_name") or content.get("product") or "").strip()
print("Detected product:", product_name)

# === DEFINE PARAMETER ALIASES ===
param_aliases = {
    "moisture": ["moisture", "quality_standard_2_name", "test_parameter_4_name"],
    "total_plate_count": ["standard plate count", "total plate count", "total_plate_count"],
    "enterobacteriaceae": ["coliform count", "enterobacteriaceae", "quality_standard_12_name"],
    "salmonella": ["salmonella", "quality_standard_13_name"],
    "yeast_and_mold": ["yeast & mould", "yeast and mold", "yeast_and_mould", "yeast_and_mold", "yeast_mould"],
    "acetone": ["acetone_insoluble", "acetone insoluble matter", "quality_standard_1_name"],
    "peanut": ["peanut_allergen", "peanut", "quality_standard_8_name"],
    "peroxide": ["peroxide_value", "quality_standard_5_name"],
    "gardner": ["gardner", "colour_gardner"],
    "hexane": ["hexane_insoluble", "hexane insoluble matter", "quality_standard_4_name"],
    "toluene": ["toluene_insoluble", "toluene insoluble matter"],
    "e_coli": ["e_coli", "quality_standard_11_name"]
}

# === Normalizer ===
_norm_re = re.compile(r"[^a-z0-9]")
def normalize_text(s):
    return _norm_re.sub("", str(s).lower()) if s else ""

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
            if keys_match:
                keys_list = [k.strip().strip('"').strip("'") for k in keys_match.group(1).split(",") if k.strip()]
            else:
                keys_list = []
            prod_norm = product_name.lower()
            if product_part and (product_part in prod_norm or prod_norm in product_part):
                raw_keys = keys_list
                break

print("Keys of Interest (from keys.txt):", raw_keys)

# === HELPER FUNCTIONS ===
_num_re_f = re.compile(r"[-+]?\d*\.\d+|\d+")
def _first_number(s):
    if s is None: return None
    m = _num_re_f.search(str(s).replace(",", "").strip())
    return float(m.group(0)) if m else None

def parse_interval(value, is_spec=False):
    if value is None: return None
    if isinstance(value, (int, float)):
        v = float(value)
        return {"min":0,"min_inc":True,"max":v,"max_inc":True} if is_spec else {"min":v,"min_inc":True,"max":v,"max_inc":True}
    s = str(value).lower().strip()
    if any(x in s for x in ["absent", "not detect", "nd", "negative"]):
        return {"min":0,"min_inc":True,"max":0,"max_inc":True}
    m = re.match(r'^\s*([<>]=?)\s*([0-9]*\.?[0-9]+)', s)
    if m:
        comp, num_s = m.groups(); num = float(num_s)
        if comp == "<": return {"min":0,"min_inc":True,"max":num,"max_inc":False}
        if comp == "<=": return {"min":0,"min_inc":True,"max":num,"max_inc":True}
        if comp == ">": return {"min":num,"min_inc":False,"max":None,"max_inc":False}
        if comp == ">=": return {"min":num,"min_inc":True,"max":None,"max_inc":False}
    if "max" in s:
        n=_first_number(s); return {"min":0,"min_inc":True,"max":n,"max_inc":True} if n else None
    if "min" in s:
        n=_first_number(s); return {"min":n,"min_inc":True,"max":None,"max_inc":False} if n else None
    if "-" in s or " to " in s:
        nums=_num_re_f.findall(s)
        if len(nums)>=2: a,b=float(nums[0]),float(nums[1]); return {"min":min(a,b),"min_inc":True,"max":max(a,b),"max_inc":True}
    n=_first_number(s)
    if n is not None:
        return {"min":0,"min_inc":True,"max":n,"max_inc":True} if is_spec else {"min":n,"min_inc":True,"max":n,"max_inc":True}
    return None

def interval_within(result_int, spec_int):
    if not result_int or not spec_int: return False,"Non-numeric result or missing spec"
    if spec_int["max"] is not None and result_int["max"]>spec_int["max"]: return False,"Exceeds upper bound"
    if spec_int["min"] is not None and result_int["min"]<spec_int["min"]: return False,"Below lower bound"
    return True,"Within Spec"

# === GETTER WITH FUZZY SUBSTRING MATCHING ===
def get_result_and_spec(key):
    aliases = param_aliases.get(key, [key])
    alias_norms = [normalize_text(a) for a in aliases]

    found_result, found_spec = None, None

    # Look for test_parameter_x_name fields
    for k, v in content.items():
        if not k.lower().startswith("test_parameter_") or not k.lower().endswith("_name"):
            continue
        param_norm = normalize_text(v)

        # fuzzy substring match (both directions)
        if any(a in param_norm or param_norm in a or param_norm.startswith(a) or a.startswith(param_norm) for a in alias_norms):
            prefix = k[:-5]  # remove "_name"
            found_result = content.get(f"{prefix}_observed_results")
            found_spec   = content.get(f"{prefix}_specifications")
            break

    # Fallback: scan all keys for substring matches
    if not found_result or not found_spec:
        for k, v in content.items():
            k_norm = normalize_text(k)
            if any(a in k_norm or k_norm in a or k_norm.startswith(a) or a.startswith(k_norm) for a in alias_norms):
                if "result" in k_norm or "observed" in k_norm:
                    found_result = v
                if "spec" in k_norm or "limit" in k_norm:
                    found_spec = v

    return found_result, found_spec

# === Colors ===
GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

# === REPORT ===
print("\nLab Report:\n" + "-"*110)
print(f"{'Parameter':<30} | {'Result':<20} | {'Spec':<30} | Status")
print("-"*110)

non_compliant_found = False

for key in raw_keys:  # use exactly keys from keys.txt
    raw_result, raw_spec = get_result_and_spec(key)
    raw_result_str = str(raw_result).strip() if raw_result is not None else "Missing"
    raw_spec_str   = str(raw_spec).strip()   if raw_spec is not None else "Missing"

    res_int = parse_interval(raw_result, is_spec=False)
    spec_int = parse_interval(raw_spec, is_spec=True)

    if res_int and spec_int:
        within, reason = interval_within(res_int, spec_int)
        status = "Within Spec" if within else "Exceeds Spec"
    else:
        within, reason = False, "Cannot compare non-numeric value"
        status = "Spec missing / Cannot compare"

    # flag if non-compliance
    if status != "Within Spec":
        non_compliant_found = True

    # colorize status
    if status == "Within Spec":
        status_colored = f"{GREEN}{status}{RESET}"
    else:
        status_colored = f"{RED}{status}{RESET}"

    print(f"{key:<30} | {raw_result_str:<20} | {raw_spec_str:<30} | {status_colored}")
    if not within and reason not in ["Cannot compare non-numeric value"]:
        print(f"  Reason: {reason}")

print("-"*110)

# === FINAL SUMMARY ===
if non_compliant_found:
    print(f"{BOLD}{RED}This report has Non-Compliance{RESET}")
else:
    print(f"{BOLD}{GREEN}This report is Fully compliant{RESET}")

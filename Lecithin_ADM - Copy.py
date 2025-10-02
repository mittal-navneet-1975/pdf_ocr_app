import json 
import re
import os
import glob
import sys

# === CONFIG ===
json_dir = r"C:\Test\output"   # directory where JSON files are stored
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

# === DEFINE PARAMETER ALIASES ===
param_aliases = {
    "moisture": ["moisture", "moisture%", "moisture %"],
    "total_plate_count": ["totalplatecount", "standardplatecount", "spc", "platecount"],
    "enterobacteriaceae": ["enterobacteriaceae", "coliform", "coliformcount"],
    "e_coli": ["e_coli", "e.coli", "coli", "ecoli"],
    "salmonella": ["salmonella", "salmonella25g"],
    "yeast_and_mold": ["yeastmould", "yeastmold", "yeast&mould", "yeastandmold", "yeastmouldcfug"],
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
    s_clean = str(s).strip().replace(",", "")
    m = re.search(r"[-+]?\d*\.?\d+", s_clean)
    return float(m.group(0)) if m else None

def parse_interval(value, is_spec=False):
    if value is None: return None
    if isinstance(value, (int, float)):
        v = float(value)
        return {"min":0,"min_inc":True,"max":v,"max_inc":True} if is_spec else {"min":v,"min_inc":True,"max":v,"max_inc":True}
    s = str(value).lower().strip()
    if any(x in s for x in ["absent", "not detect", "nd", "negative"]):
        return {"min":0,"min_inc":True,"max":0,"max_inc":True}
    m = re.match(r'^\s*([<>]=?)\s*([\d,]*\.?\d+)', s)
    if m:
        comp, num_s = m.groups()
        num = float(num_s.replace(",", ""))
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

# === FIXED INTERVAL CHECK FOR MICROBIOLOGY ===
def interval_within(result_int, spec_int):
    if not result_int or not spec_int: 
        return False, "Non-numeric result or missing spec"

    # Case: Spec says Absent / 0
    if spec_int.get("max") == 0:
        # Result is 0 or ND/Absent
        if result_int.get("max") == 0:
            return True, "Within Spec"
        # Result is < some number
        if result_int.get("max") is not None and result_int["max"] <= 3:  # threshold for e.g. <3 mpn/g
            return True, "Within Spec"
        return False, "Exceeds upper bound"

    # General numeric comparison
    if spec_int.get("max") is not None and result_int["max"] > spec_int["max"]:
        return False, "Exceeds upper bound"
    if spec_int.get("min") is not None and result_int["min"] < spec_int["min"]:
        return False, "Below lower bound"

    return True, "Within Spec"

# === GETTER WITH FLEXIBLE SUBSTRING MATCHING ===
def get_result_and_spec(key):
    aliases = param_aliases.get(key, [key])
    alias_norms = [normalize_text(a) for a in aliases]

    found_result, found_spec = None, None

    for k, v in content.items():
        if not k.lower().startswith("test_parameter_"):
            continue
        param_norm = normalize_text(v)
        if any(a in param_norm or param_norm in a for a in alias_norms):
            base = k.rsplit("_", 1)[0] if k.endswith("_name") else k
            result_key = base.replace("test_parameter", "observed_result")
            spec_key   = base.replace("test_parameter", "specification")
            found_result = content.get(result_key) or content.get(result_key + "_1")
            found_spec   = content.get(spec_key) or content.get(spec_key + "_1")
            break

    # fallback
    if not (found_result or found_spec):
        for k, v in content.items():
            k_norm = normalize_text(k)
            if any(a in k_norm or k_norm in a for a in alias_norms):
                if not found_result and ("result" in k_norm or "observed" in k_norm):
                    found_result = v
                if not found_spec and ("spec" in k_norm or "limit" in k_norm):
                    found_spec = v

    if not found_result and not found_spec:
        return None, None

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

for key in raw_keys:
    raw_result, raw_spec = get_result_and_spec(key)
    if raw_result is None and raw_spec is None:
        continue

    raw_result_str = str(raw_result).strip() if raw_result is not None else ""
    raw_spec_str   = str(raw_spec).strip()   if raw_spec is not None else ""

    res_int = parse_interval(raw_result, is_spec=False)
    spec_int = parse_interval(raw_spec, is_spec=True)

    if res_int and spec_int:
        within, reason = interval_within(res_int, spec_int)
        status = "Within Spec" if within else "Exceeds Spec"
    else:
        within, reason = False, "Cannot compare non-numeric value"
        status = "Spec missing / Cannot compare"

    if status != "Within Spec":
        non_compliant_found = True

    status_colored = f"{GREEN}{status}{RESET}" if status == "Within Spec" else f"{RED}{status}{RESET}"
    print(f"{key:<30} | {raw_result_str:<20} | {raw_spec_str:<30} | {status_colored}")


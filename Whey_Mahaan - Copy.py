import json
import re
import os
import glob
import sys

# === CONFIG ===
json_dir = r"C:\Test\output"   # default JSON folder
keys_file = r"C:\Test\keys.txt"  # file containing keys of interest

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

# === NORMALIZER ===
def normalize_text(s):
    if not s: return ""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    return s

# === LOAD KEYS FROM FILE USING DYNAMIC KEYWORDS ===
raw_keys = []
# Use dynamic keywords (from console output)
dynamic_product = product_name.split()[0] if product_name else ""
dynamic_company = company_name.split()[0] if company_name else ""
product_company_key = f"{dynamic_product}_{dynamic_company}".lower()  # Whey_Mahaan -> whey_mahaan

if os.path.exists(keys_file):
    with open(keys_file, "r", encoding="utf-8") as f:
        for line in f:
            if "- Mandatory Values -" not in line:
                continue
            product_part, keys_part = line.split("- Mandatory Values -", 1)
            product_part_norm = product_part.strip().strip('"').lower()
            keys_match = re.search(r"\{(.*?)\}", keys_part)
            keys_list = [k.strip().strip('"').strip("'") for k in keys_match.group(1).split(",")] if keys_match else []

            # Match dynamic Product_Company key first, else fallback to product only
            if product_part_norm == product_company_key:
                raw_keys = keys_list
                break
            elif not raw_keys and product_part_norm == dynamic_product.lower():
                raw_keys = keys_list

print("Keys of Interest:", raw_keys)

# === HELPER FUNCTIONS ===
_num_re = re.compile(r"[-+]?\d*\.\d+|\d+")

def parse_number(s):
    if s is None: return None
    s = str(s).replace(",", "").strip()
    m = _num_re.search(s)
    return float(m.group(0)) if m else None

def parse_interval(value):
    """Convert a value or spec string into numeric interval."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return {"min": float(value), "max": float(value)}
    s = str(value).lower().strip()
    s = s.replace("–", "-").replace("—", "-")
    # Handle textual absent
    if any(x in s for x in ["absent", "not detect", "nd", "negative"]):
        return {"min": 0, "max": 0}
    # Handle <, <=, >, >=
    m = re.match(r'([<>]=?)\s*([\d,\.]+)', s)
    if m:
        comp, num_s = m.groups()
        num = float(num_s.replace(",", ""))
        if comp == "<":
            return {"min": 0, "max": num - 1e-6}
        if comp == "<=":
            return {"min": 0, "max": num}
        if comp == ">":
            return {"min": num + 1e-6, "max": None}
        if comp == ">=":
            return {"min": num, "max": None}
    # Handle ranges like 0-5
    if "-" in s:
        nums = _num_re.findall(s)
        if len(nums) >= 2:
            return {"min": float(nums[0]), "max": float(nums[1])}
    # Handle max/min keyword
    if "max" in s:
        n = parse_number(s)
        return {"min": 0, "max": n}
    if "min" in s:
        n = parse_number(s)
        return {"min": n, "max": None}
    # single number
    n = parse_number(s)
    if n is not None:
        return {"min": n, "max": n}
    return None

def check_within(result, spec, key=None):
    """Check if result is within spec."""
    # Treat textual compliance as Within Spec
    if isinstance(result, str):
        if result.strip().lower() in ["complies", "fine", "ok", "acceptable"]:
            return True, "Within Spec"

    # Handle textual parameters (appearance, color, taste, scorched)
    if key and key.lower() in ["colour/ appearance", "taste / flavour", "scorched particles", "appearance", "color"]:
        if result and spec:
            r, s = str(result).strip().lower(), str(spec).strip().lower()
            # If result explicitly mentions compliance or matches spec text
            if r == s or r in s or s in r or r in ["complies", "fine", "ok", "acceptable"]:
                return True, "Within Spec"
        return False, "Textual mismatch"

    # Numeric comparison
    res_int = parse_interval(result)
    spec_int = parse_interval(spec)

    if not res_int or not spec_int:
        return False, "Non-numeric result or missing spec"

    if spec_int.get("min") is not None and res_int.get("min") < spec_int.get("min"):
        return False, "Below lower bound"
    if spec_int.get("max") is not None and res_int.get("max") > spec_int.get("max"):
        return False, "Exceeds upper bound"
    return True, "Within Spec"


def get_result_and_spec(key):
    """
    Retrieve result and spec from content for a given key.
    Uses normalized text and partial matching for common lab names.
    """
    key_norm = normalize_text(key)

    # Mapping common variations
    common_map = {
        "colourappearance": ["colourappearance", "color", "appearance"],
        "tasteflavour": ["tasteflavour", "taste", "flavour", "flavor"],
        "scorchedparticles": ["scorchedparticles", "scorched"]
    }

    for base, value in content.items():
        if base.startswith("characteristic_") and base.endswith("_name"):
            name_norm = normalize_text(str(value).strip())

            # Direct match
            if name_norm == key_norm:
                prefix = base.split("_")[1]
                return content.get(f"characteristic_{prefix}_result"), content.get(f"characteristic_{prefix}_limit")

            # Check in common_map
            for std_key, variants in common_map.items():
                if key_norm in variants and name_norm in variants:
                    prefix = base.split("_")[1]
                    return content.get(f"characteristic_{prefix}_result"), content.get(f"characteristic_{prefix}_limit")

    return None, None


# === HTML REPORT ===
output_file = os.path.splitext(json_file)[0] + "_report.html"
with open(output_file, "w", encoding="utf-8") as out:
    out.write("<html><body>\n")
    out.write(f"<h1>📊 Lab Report for {product_name} ({company_name})</h1>\n")
    out.write(f"<p>Source JSON file: {os.path.basename(json_file)}</p>\n")
    out.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
    out.write("<tr><th>Parameter</th><th>Result</th><th>Spec</th><th>Status</th></tr>\n")

    non_compliant_found = False

    for key in raw_keys:
        raw_result, raw_spec = get_result_and_spec(key)
        raw_result_str = str(raw_result) if raw_result is not None else ""
        raw_spec_str = str(raw_spec) if raw_spec is not None else ""

        within, reason = check_within(raw_result, raw_spec, key)
        status = "Within Spec" if within else "Out of Spec"
        color = "green" if within else "red"

        if not within:
            non_compliant_found = True

        out.write(f"<tr>")
        out.write(f"<td>{key}</td><td>{raw_result_str}</td><td>{raw_spec_str}</td>")
        out.write(f"<td style='color:{color}'>{status}")
        if not within:
            out.write(f"<br><small>Reason: {reason}</small>")
        out.write("</td></tr>\n")

    out.write("</table>\n")
    if non_compliant_found:
        out.write(f"<h3 style='color:red'>This report has Non-Compliance</h3>\n")
    else:
        out.write(f"<h3 style='color:green'>This report is ✅ Fully compliant</h3>\n")
    out.write("</body></html>\n")

print(f"Report written to: {output_file}")

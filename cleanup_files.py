import os
import glob

def cleanup_files():
    pdf_dir = r"C:\Users\vibho\Downloads\Engineering\Test\docs"
    json_dir = r"C:\Users\vibho\Downloads\Engineering\Test\output"

    # # --- Delete all PDFs in pdf_dir ---
    # pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    # for f in pdf_files:
    #     try:
    #         os.remove(f)
    #         print(f"Deleted PDF: {f}")
    #     except Exception as e:
    #         print(f"Failed to delete {f}: {e}")

    # --- Delete only JSON files in json_dir (keep HTML) ---
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    for f in json_files:
        try:
            os.remove(f)
            print(f"Deleted JSON: {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")

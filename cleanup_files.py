import os
import glob

def cleanup_files():
    pdf_dir = r"C:\pdf_OCR_app\pdf"
    json_dir = r"C:\pdf_OCR_app\output"

    # --- Delete PDFs (deduplicated) ---
    pdf_files = set(glob.glob(os.path.join(pdf_dir, "*.pdf")) + glob.glob(os.path.join(pdf_dir, "*.PDF")))
    pdf_files = list(pdf_files)  # convert back to list if you want iteration
    print("PDF files found:", pdf_files)
    for f in pdf_files:
        try:
            os.remove(f)
            print(f"Deleted PDF: {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")

    # --- Delete JSON files (deduplicated) ---
    json_files = set(glob.glob(os.path.join(json_dir, "*.json")) + glob.glob(os.path.join(json_dir, "*.JSON")))
    json_files = list(json_files)
    print("JSON files found:", json_files)
    for f in json_files:
        try:
            os.remove(f)
            print(f"Deleted JSON: {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")


if __name__ == "__main__":
    print("Running cleanup_files() ...")
    cleanup_files()
    print("Cleanup complete.")

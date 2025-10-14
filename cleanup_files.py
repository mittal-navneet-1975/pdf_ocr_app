import os
import glob

def cleanup_files():
    CURRENT_DIR = os.getcwd()

    pdf_dir = os.path.join(CURRENT_DIR, "pdf")
    json_dir = os.path.join(CURRENT_DIR, "output")

    # Create directories if they don't exist
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

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

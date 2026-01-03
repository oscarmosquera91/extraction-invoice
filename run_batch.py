from extraction.orchestrator import process_pdf
import json
import os

PDF_DIR = "data/raw"

for file in os.listdir(PDF_DIR):
    if file.lower().endswith(".pdf"):
        path = os.path.join(PDF_DIR, file)
        result = process_pdf(path)

        print("=" * 80)
        print(file)
        print(json.dumps(result, indent=2, ensure_ascii=False))
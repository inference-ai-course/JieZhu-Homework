import os
import json
import requests
import fitz  # PyMuPDF
import re

# Folder paths
pdf_dir = "pdf_ocr"
txt_dir = "txt_ocr"

# Create directories if they don't exist
os.makedirs(pdf_dir, exist_ok=True)
os.makedirs(txt_dir, exist_ok=True)

# Sanitize filename to be valid
def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# Read the JSON file
with open("arxiv_cs_ai_search_result.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

# Process the first 5 papers
for paper in papers[:5]:
    title = paper["title"]
    pdf_url = paper["pdf_url"]
    safe_title = safe_filename(title)

    # Define PDF and TXT paths
    pdf_path = os.path.join(pdf_dir, f"{safe_title}.pdf")
    txt_path = os.path.join(txt_dir, f"{safe_title}.txt")

    # Download PDF
    try:
        print(f"⬇️ Downloading: {title}")
        response = requests.get(pdf_url)
        with open(pdf_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"❌ Failed to download {pdf_url}: {e}")
        continue

    # Extract text from PDF
    try:
        print(f"📖 Extracting text from: {pdf_path}")
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        # Save the extracted text
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        print(f"✅ Text saved: {txt_path}\n")

    except Exception as e:
        print(f"❌ Failed to extract from {pdf_path}: {e}")
        continue
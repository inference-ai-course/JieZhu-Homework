import os
import json
import re
from langdetect import detect
from datasketch import MinHash, MinHashLSH
from hashlib import sha1
import markdown
from transformers import GPT2TokenizerFast

# Initialize tokenizer
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

# Step 1: Scan folder and read all json/txt files
def scan_and_read_files(root_folder):
    content_list = []
    for dirpath, _, filenames in os.walk(root_folder):
        for file in filenames:
            if file.endswith(".json") or file.endswith(".txt") or file.endswith(".jsonl"):
                file_path = os.path.join(dirpath, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        if file.endswith(".json"):
                            data = json.load(f)
                            if isinstance(data, dict):
                                content_list.append(json.dumps(data))
                            elif isinstance(data, list):
                                for item in data:
                                    content_list.append(json.dumps(item))
                        else:
                            content_list.append(f.read())
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return content_list

# Step 2: Language detection
def filter_by_language(texts, lang="en"):
    return [t for t in texts if detect(t) == lang]

# Step 3: Remove duplicates using MinHash
def remove_duplicates(texts):
    unique_texts = []
    seen_hashes = set()
    for text in texts:
        m = MinHash(num_perm=128)
        for word in text.split():
            m.update(word.encode('utf8'))
        hash_val = sha1(m.digest()).hexdigest()
        if hash_val not in seen_hashes:
            seen_hashes.add(hash_val)
            unique_texts.append(text)
    return unique_texts

# Step 4: Remove PII
def remove_pii(text):
    text = re.sub(r'\b[\w.-]+?@\w+?\.\w{2,4}\b', '[EMAIL]', text)
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[CREDIT_CARD]', text)
    text = re.sub(r'\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b', '[PHONE]', text)
    return text

# Set input root folder
root_folder = "data"

# Process
raw_texts = scan_and_read_files(root_folder)
original_token_count = sum(len(tokenizer.encode(text)) for text in raw_texts)

lang_texts = filter_by_language(raw_texts, lang="en")
deduped_texts = remove_duplicates(lang_texts)
cleaned_texts = [remove_pii(text) for text in deduped_texts]
final_token_count = sum(len(tokenizer.encode(text)) for text in cleaned_texts)

# Write clean corpus
clean_path = "data/clean_corpus.txt"
with open(clean_path, "w", encoding="utf-8") as f:
    for text in cleaned_texts:
        f.write(text + "\n")

# Step 5: Markdown report
report = f"""
# Clean Corpus Report

- **Original Tokens**: {original_token_count}
- **Final Tokens**: {final_token_count}
- **Tokens Removed**: {original_token_count - final_token_count}
- **Removal Percentage**: {100 * (original_token_count - final_token_count) / original_token_count:.2f}%

The cleaned corpus is saved in `clean_corpus.txt`.
"""

report_path = "data/clean_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)
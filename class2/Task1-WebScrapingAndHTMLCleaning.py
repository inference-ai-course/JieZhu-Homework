import requests
from bs4 import BeautifulSoup
import json

url = "https://arxiv.org/search/?query=cs.AI&searchtype=all&abstracts=show&order=-announced_date_first&size=200"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

papers = []

for item in soup.find_all("li", class_="arxiv-result"):
    try:
        # Title
        title_tag = item.find("p", class_="title is-5 mathjax")
        title = title_tag.get_text(strip=True)

        # Abstract URL and PDF URL
        list_title = item.find("p", class_="list-title")
        abs_url = list_title.find("a")["href"]
        pdf_url = list_title.find("a", string="pdf")["href"]
        paper_url = pdf_url.replace("pdf","html")+"v1"

        # Authors
        author_links = item.find("p", class_="authors").find_all("a")
        authors = [a.get_text(strip=True) for a in author_links]

        # Full Abstract (hidden <span>)
        abstract_full_tag = item.find("span", class_="abstract-full")
        abstract = abstract_full_tag.get_text(strip=True) if abstract_full_tag else ""

        # Submission Date
        date_tag = item.find("p", class_="is-size-7")
        submitted_line = date_tag.get_text(strip=True).replace("\n", " ") if date_tag else ""

        papers.append({
            "title": title,
            "abs_url": abs_url,
            "pdf_url": pdf_url,
            "paper_url": paper_url,
            "authors": authors,
            "abstract": abstract,
            "submitted_date": submitted_line
        })

    except Exception as e:
        print("⚠️ Error parsing entry:", e)
        continue

# Save to JSON
with open("arxiv_cs_ai_search_result.json", "w", encoding="utf-8") as f:
    json.dump(papers, f, ensure_ascii=False, indent=2)

print(f"✅ Extracted {len(papers)} papers. Saved to arxiv_cs_ai_search_result.json")
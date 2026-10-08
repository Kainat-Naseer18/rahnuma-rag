import copy, json, re, unicodedata
from pathlib import Path
from bs4 import BeautifulSoup

# Put the selector(s) you found here. If English and Urdu differ, list both:
SELECTORS = ["div.MainContentArea"]

SKIP_HEADINGS = {"contents", "table of contents", "فہرست", "مشمولات"}

def is_noise(text):
    """True for table-of-contents lines we don't want in the data."""
    t = text.strip()
    if t.startswith("----"):                  # contents entries look like "---- Registration process"
        return True
    if t.lower() in SKIP_HEADINGS:            # the word "Contents" itself
        return True
    return False

def normalize(text):
    """Clean up the text so the same letter is always stored the same way."""
    text = unicodedata.normalize("NFKC", text)                   # standardise character forms
    text = text.replace("\u064a", "\u06cc")                      # Arabic yeh -> Urdu yeh
    text = text.replace("\u0643", "\u06a9")                      # Arabic kaf -> Urdu kaf
    text = re.sub(r"[\u200b\u200e\u200f\ufeff]", "", text)       # remove invisible characters
    text = re.sub(r"[ \t]+", " ", text)                          # collapse repeated spaces
    return text.strip()

def find_root(soup):
    """Try each selector until one finds the content box."""
    for sel in SELECTORS:
        root = soup.select_one(sel)
        if root is not None:
            return root
    raise ValueError("content box not found - check SELECTORS")

def list_item_text(li):
    """Text of a list item, without the text of lists nested inside it."""
    li = copy.copy(li)
    for sub in li.find_all(["ul", "ol"]):
        sub.decompose()
    return normalize(li.get_text(" ", strip=True))

def extract_sections(html):
    soup = BeautifulSoup(html, "lxml")
    root = find_root(soup)

    # Exclude the category menu repeated above FBR articles.
    for menu in root.select(".liCategoryContents"):
        menu.decompose()

    # Some pages place article prose directly inside a div.
    for node in list(root.find_all(string=True)):
        if node.parent.name == "div" and normalize(str(node)):
            node.wrap(soup.new_tag("p"))

    sections = []
    current = {"heading": "Intro", "lines": []}

    for el in root.find_all(["h1", "h2", "h3", "h4", "p", "li", "tr"]):
        # skip paragraphs inside list items (the list item already contains them)
        if el.name == "p" and el.find_parent("li"):
            continue

        if el.name == "li":
            text = list_item_text(el)
        elif el.name == "tr":                         # table row -> cells joined by " | "
            cells = [normalize(c.get_text(" ", strip=True)) for c in el.find_all(["td", "th"])]
            text = " | ".join(c for c in cells if c)
        else:
            text = normalize(el.get_text(" ", strip=True))

        if not text or is_noise(text):
            continue

        if el.name in ("h1", "h2", "h3", "h4"):      # a heading starts a new section
            if current["lines"]:
                sections.append(current)
            current = {"heading": text, "lines": []}
        else:
            prefix = "- " if el.name == "li" else ""
            current["lines"].append(prefix + text)

    if current["lines"]:
        sections.append(current)
    return sections

# ---- main program ----
log = json.load(open("data/download_log.json", encoding="utf-8"))
output = []

for r in log:
    if not r.get("ok"):
        continue
    html = Path("data/raw", r["file"]).read_text(encoding="utf-8")
    sections = extract_sections(html)
    output.append({**r, "sections": sections})
    print(r["file"], "-> sections:", len(sections))

Path("data/processed").mkdir(parents=True, exist_ok=True)
json.dump(output, open("data/processed/pages.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("saved data/processed/pages.json")

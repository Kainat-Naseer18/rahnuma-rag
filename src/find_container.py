from bs4 import BeautifulSoup

# Which saved file to inspect. Try "1_en.html" first, then "1_ur.html".
FILE = "data/raw/1_ur.html"


html = open(FILE, encoding="utf-8").read()
soup = BeautifulSoup(html, "lxml")        # turn the HTML text into a structure we can search

heading = soup.find("h3")                 # find the first <h3> heading (e.g. "Taxable Income")
print("First h3 text:", heading.get_text(strip=True))
print()

# Walk upward through the boxes that contain this heading
for box in heading.parents:
    if box.name in ("body", "html", "[document]"):
        break
    print(
        "tag:", box.name,
        "| id:", box.get("id"),
        "| class:", box.get("class"),
        "| h3 count:", len(box.find_all("h3")),
        "| text length:", len(box.get_text()),
    )
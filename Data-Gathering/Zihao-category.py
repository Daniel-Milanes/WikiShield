import xml.etree.ElementTree as ET
import requests
import csv
import time

TOP_LEVEL_CATEGORIES = {
    "Q5": "celebrity",           # human
    "Q16521": "animal",          # animal
    "Q729": "plant",             # plant
    "Q515": "place",             # city
    "Q486972": "place",          # human settlement
    "Q6256": "place",            # country
    "Q618123": "place",          # geographical object
    "Q56061": "place",           # administrative territorial entity
    "Q82794": "place",           # location
    "Q11424": "film",            # film
    "Q482994": "literature",     # written work
    "Q13442814": "sports",       # sports team
    "Q1656682": "sports",        # athlete
    "Q4830453": "business",      # businessperson
    "Q571": "literature",        # book
    "Q327333": "technology",     # software
    "Q901": "education",         # university
    "Q11707": "religion",        # religious organization
    "Q937857": "music",          # music group
    "Q215380": "music",          # musical artist
    "Q21198": "science",         # scientist
    "Q17376908": "media",        # media organization
    # Add more as needed for your use-case
}

def get_wikidata_qid(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "pageprops",
        "titles": title,
        "format": "json"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        pages = list(data["query"]["pages"].values())
        if not pages or "pageprops" not in pages[0] or "wikibase_item" not in pages[0]["pageprops"]:
            return None
        return pages[0]["pageprops"]["wikibase_item"]
    except Exception as e:
        print(f"Error getting QID for {title}: {e}")
        return None

def get_parents(qid):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        entity = data["entities"][qid]
        parents = set()
        for prop in ["P31", "P279"]:
            if prop in entity["claims"]:
                for claim in entity["claims"][prop]:
                    if "mainsnak" in claim and "datavalue" in claim["mainsnak"]:
                        parents.add(claim["mainsnak"]["datavalue"]["value"]["id"])
        return list(parents)
    except Exception as e:
        return []

def get_broad_categories(qid, max_depth=6, visited=None):
    if not qid:
        return set()
    if visited is None:
        visited = set()
    if qid in visited or max_depth < 0:
        return set()
    visited.add(qid)
    if qid in TOP_LEVEL_CATEGORIES:
        return {TOP_LEVEL_CATEGORIES[qid]}
    parents = get_parents(qid)
    categories = set()
    for parent_qid in parents:
        categories |= get_broad_categories(parent_qid, max_depth - 1, visited)
    return categories

def main():
    tree = ET.parse("truncated_edits.xml")
    root = tree.getroot()
    results = []
    seen_titles = set()
    for wpedit in root.findall("WPEdit"):
        title = wpedit.find("common/title").text if wpedit.find("common/title") is not None else ""
        if title in seen_titles:  # avoid duplicates
            continue
        seen_titles.add(title)
        qid = get_wikidata_qid(title.replace(" ", "_"))
        if not qid:
            broad_cats = {"other"}
        else:
            broad_cats = get_broad_categories(qid)
            if not broad_cats:
                broad_cats = {"other"}
        print(f"{title}: QID={qid}, broad_topics={', '.join(broad_cats)}")
        results.append({
            "title": title,
            "wikidata_qid": qid or "",
            "broad_topics": "; ".join(sorted(broad_cats))
        })
        time.sleep(0.5)  # Respectful delay for APIs

    with open("wikipedia_broad_topics.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "wikidata_qid", "broad_topics"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print("Done. Output saved as wikipedia_broad_topics.csv")

if __name__ == "__main__":
    main()

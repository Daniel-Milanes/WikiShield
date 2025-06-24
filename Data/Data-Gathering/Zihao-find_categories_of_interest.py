import pandas as pd
import requests
import time

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
    except Exception:
        return None

def get_instance_of_qid(qid):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        entity = data["entities"][qid]
        instances = set()
        if "P31" in entity["claims"]:
            for claim in entity["claims"]["P31"]:
                if "mainsnak" in claim and "datavalue" in claim["mainsnak"]:
                    instances.add(claim["mainsnak"]["datavalue"]["value"]["id"])
        return list(instances)
    except Exception:
        return []

df = pd.read_csv("truncated.csv")
vandals = df[df['isvandalism'].astype(str).str.lower() == "true"]
title_counts = vandals['title'].value_counts().head(100)
instance_counts = {}

for title in title_counts.index:
    qid = get_wikidata_qid(title.replace(" ", "_"))
    time.sleep(0.1)
    if qid:
        instance_qids = get_instance_of_qid(qid)
        for inst in instance_qids:
            instance_counts[inst] = instance_counts.get(inst, 0) + 1
        # print(f"{title} ({qid}) -> {instance_qids}")
    # else:
        # print(f"{title}: QID not found")

print("\nMost frequent instance_of QIDs for vandalized articles:")
for inst, count in sorted(instance_counts.items(), key=lambda x: -x[1]):
    print(f"{inst}: {count}")

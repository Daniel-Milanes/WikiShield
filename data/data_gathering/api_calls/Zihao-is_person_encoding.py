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
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    pages = list(data["query"]["pages"].values())
    if not pages or "pageprops" not in pages[0] or "wikibase_item" not in pages[0]["pageprops"]:
        return None
    return pages[0]["pageprops"]["wikibase_item"]

def get_parents(qid):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        entity = data["entities"].get(qid)
        if not entity:
            return []  # QID not found, return empty list!
        parents = set()
        for prop in ["P31", "P279"]:
            if prop in entity["claims"]:
                for claim in entity["claims"][prop]:
                    if "mainsnak" in claim and "datavalue" in claim["mainsnak"]:
                        parents.add(claim["mainsnak"]["datavalue"]["value"]["id"])
        return list(parents)
    except Exception:
        return []  # On any error, just return empty list


def is_person_qid(qid, parent_cache, max_depth=5, visited=None):
    if not qid:
        return 0
    if visited is None:
        visited = set()
    if qid in visited or max_depth < 0:
        return 0
    visited.add(qid)
    if qid == "Q5":
        return 1
    if qid in parent_cache:
        parents = parent_cache[qid]
    else:
        parents = get_parents(qid)
        parent_cache[qid] = parents
    for parent_qid in parents:
        if is_person_qid(parent_qid, parent_cache, max_depth - 1, visited):
            return 1
    return 0

# --- MAIN PROCESS ---

input_csv = "filtered_edits_with_edit_counts.csv"
output_csv = "filtered_edits_with_edit_counts_isperson.csv"

df = pd.read_csv(input_csv)
is_person_col = []

qid_cache = {}
parent_cache = {}

api_calls = 0

unique_titles = df['title'].drop_duplicates().tolist()

# First, build a cache of qids for each unique title
for i, title in enumerate(unique_titles):
    t = str(title).replace(" ", "_")
    if t not in qid_cache:
        try:
            qid_cache[t] = get_wikidata_qid(t)
        except Exception:
            qid_cache[t] = None
        api_calls += 1
        if api_calls % 250 == 0:
            print(f"[QID] Pausing for 1 second after {api_calls} API calls...")
            time.sleep(1)

# Now annotate each row
for i, row in df.iterrows():
    t = str(row['title']).replace(" ", "_")
    qid = qid_cache.get(t)
    val = is_person_qid(qid, parent_cache, max_depth=5) if qid else 0
    is_person_col.append(val)
    api_calls += 1  # count parent lookups too
    if api_calls % 250 == 0:
        print(f"[Parent] Pausing for 1 second after {api_calls} API calls...")
        time.sleep(1)
    if (i+1) % 50 == 0:
        print(f"{i+1}/{len(df)}: {row['title']} | QID: {qid} | is_person: {val}")

df['is_person'] = is_person_col
df.to_csv(output_csv, index=False)
print(f"Done. Output written to {output_csv}")

import xml.etree.ElementTree as ET
import csv
import difflib
import requests
import time

# ======= EDIT THESE FILE NAMES =======
input_xml = "filtered_edits_no_dup.xml"   # <--- Put input xml filename here
output_csv = "filtered_edits_no_dup.csv"     # <--- Put output csv filename here
# =====================================

COLUMNS = [
    "EditType", "EditID", "comment", "user", "user_edit_count", "user_distinct_pages",
    "user_warns", "user_reg_time", "prev_user", "common", "current", "previous", "page_made_time", "title", "namespace", "creator",
    "num_recent_edits", "num_recent_reversions", "current_minor", "current_timestamp", "added_lines", "previous_timestamp",
    "deleted_lines", "isvandalism"
]

def extract_field(wpedit, path, default=""):
    """Safely get text from nested XML tags."""
    elem = wpedit
    for part in path.split("/"):
        if elem is not None:
            elem = elem.find(part)
        else:
            return default
    return elem.text if (elem is not None and elem.text is not None) else default

def to_iso8601(ts):
    ts = str(ts)
    if ts.isdigit():
        if len(ts) == 10:
            from datetime import datetime
            return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%dT%H:%M:%SZ')
        elif len(ts) == 14:
            return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"
    return ts

def fetch_revision_ids(title, timestamp_iso):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvstart": timestamp_iso,
        "rvlimit": 2,
        "rvdir": "older",
        "rvprop": "ids|timestamp",
        "format": "json"
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    if "error" in data or "query" not in data:
        return None, None
    pages = list(data["query"]["pages"].values())
    if not pages or "revisions" not in pages[0]:
        return None, None
    revs = pages[0]["revisions"]
    if len(revs) == 2:
        return revs[1]['revid'], revs[0]['revid']
    elif len(revs) == 1:
        return revs[0]['revid'], revs[0]['revid']
    else:
        return None, None

def fetch_revision_text(revid):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "revids": revid,
        "rvslots": "main",
        "rvprop": "content",
        "formatversion": 2,
        "format": "json"
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    pages = data.get("query", {}).get("pages", [])
    if pages and 'revisions' in pages[0]:
        slot = pages[0]['revisions'][0]['slots'].get('main', {})
        return slot.get('content', "") if 'content' in slot else ""
    else:
        return ""

def get_added_deleted_lines(prev_text, curr_text):
    added, deleted = [], []
    diff = difflib.unified_diff(
        prev_text.splitlines(), curr_text.splitlines(),
        fromfile='previous', tofile='current', lineterm="", n=0)
    for line in diff:
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        elif line.startswith("-"):
            deleted.append(line[1:])
        elif line.startswith("+"):
            added.append(line[1:])
    return "\n".join(added), "\n".join(deleted)

tree = ET.parse(input_xml)
root = tree.getroot()
output_rows = []
api_calls = 0

for i, wpedit in enumerate(root.findall("WPEdit")):
    row = {col: extract_field(wpedit, col) for col in COLUMNS}

    # Now fill the extra fields from <common> and <current> children if missing:
    row["page_made_time"]          = extract_field(wpedit, "common/page_made_time")
    row["title"]                   = extract_field(wpedit, "common/title")
    row["namespace"]               = extract_field(wpedit, "common/namespace")
    row["creator"]                 = extract_field(wpedit, "common/creator")
    row["num_recent_edits"]        = extract_field(wpedit, "common/num_recent_edits")
    row["num_recent_reversions"]   = extract_field(wpedit, "common/num_recent_reversions")
    row["current_minor"]           = extract_field(wpedit, "current/minor")
    row["current_timestamp"]       = extract_field(wpedit, "current/timestamp")

    # Compute added/deleted lines if not already present or set to BAD REQUEST
    title = row["title"].replace(" ", "_")
    curr_ts = row["current_timestamp"]
    if not title or not curr_ts:
        row['added_lines'] = "BAD REQUEST"
        row['deleted_lines'] = "BAD REQUEST"
        print(f"Row {i+1}: blank title or timestamp, skipping.")
        output_rows.append(row)
        continue
    timestamp_iso = to_iso8601(curr_ts)
    prev_rev, curr_rev = fetch_revision_ids(title, timestamp_iso)
    api_calls += 1
    if prev_rev and curr_rev:
        prev_text = fetch_revision_text(prev_rev)
        curr_text = fetch_revision_text(curr_rev)
        api_calls += 2
        if not prev_text or not curr_text:
            row['added_lines'] = "BAD REQUEST"
            row['deleted_lines'] = "BAD REQUEST"
            print(f"Row {i+1}: Could not retrieve revision content for {title}")
        else:
            added, deleted = get_added_deleted_lines(prev_text, curr_text)
            row['added_lines'] = added
            row['deleted_lines'] = deleted
            print(f"Row {i+1}: Found diffs for {title}")
    else:
        row['added_lines'] = "BAD REQUEST"
        row['deleted_lines'] = "BAD REQUEST"
        print(f"Row {i+1}: Could not fetch revisions for {title}")

    output_rows.append(row)
    if api_calls % 250 == 0:
        print(f"Pausing 1 second after {api_calls} API calls...")
        time.sleep(1)

with open(output_csv, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    for row in output_rows:
        filtered_row = {k: row.get(k, "") for k in COLUMNS}
        writer.writerow(filtered_row)

print(f"Done. Output saved as {output_csv}.")
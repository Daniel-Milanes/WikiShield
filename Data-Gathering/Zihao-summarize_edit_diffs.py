import xml.etree.ElementTree as ET
import requests
import difflib
import time
from datetime import datetime
import csv

def to_iso8601(ts):
    if ts and ts.isdigit():
        if len(ts) == 10:  # unix
            return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%dT%H:%M:%SZ')
        elif len(ts) == 14:  # YYYYMMDDHHMMSS
            return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"
    return ts

def get_two_revisions(title, timestamp):
    S = requests.Session()
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvlimit": 2,
        "rvstart": timestamp,
        "rvdir": "older",
        "rvprop": "ids|timestamp|user",
        "format": "json"
    }
    for attempt in range(3):
        try:
            r = S.get("https://en.wikipedia.org/w/api.php", params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            pages = list(data['query']['pages'].values())
            if not pages or 'revisions' not in pages[0]:
                return None, None
            revs = pages[0]['revisions']
            if len(revs) == 2:
                return revs[1]['revid'], revs[0]['revid']
            elif len(revs) == 1:
                return revs[0]['revid'], revs[0]['revid']
            else:
                return None, None
        except Exception as e:
            time.sleep(1)
    return None, None

def get_revision_text(revid):
    S = requests.Session()
    params = {
        "action": "query",
        "prop": "revisions",
        "revids": revid,
        "rvslots": "main",
        "rvprop": "content",
        "formatversion": 2,
        "format": "json"
    }
    for attempt in range(3):
        try:
            r = S.get("https://en.wikipedia.org/w/api.php", params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            pages = data['query']['pages']
            if pages and 'revisions' in pages[0]:
                return pages[0]['revisions'][0]['slots']['main']['content']
            else:
                return ""
        except Exception as e:
            time.sleep(1)
    return ""

def extract_metadata(wpedit):
    def ftag(tag): return wpedit.findtext(tag) or ""
    def fcomm(tag): return wpedit.find("common/" + tag).text if wpedit.find("common/" + tag) is not None else ""
    meta = {
        "EditType": ftag("EditType"),
        "EditID": ftag("EditID"),
        "comment": ftag("comment"),
        "isvandalism": ftag("isvandalism"),
        "user": ftag("user"),
        "user_edit_count": ftag("user_edit_count"),
        "user_distinct_pages": ftag("user_distinct_pages"),
        "user_warns": ftag("user_warns"),
        "user_reg_time": ftag("user_reg_time"),
        "prev_user": ftag("prev_user"),
        "page_made_time": fcomm("page_made_time"),
        "title": fcomm("title"),
        "namespace": fcomm("namespace"),
        "creator": fcomm("creator"),
        "num_recent_edits": fcomm("num_recent_edits"),
        "num_recent_reversions": fcomm("num_recent_reversions"),
        "current_minor": wpedit.find("current/minor").text if wpedit.find("current/minor") is not None else "",
        "current_timestamp": wpedit.find("current/timestamp").text if wpedit.find("current/timestamp") is not None else "",
        "previous_timestamp": wpedit.find("previous/timestamp").text if wpedit.find("previous/timestamp") is not None else "",
    }
    return meta

def main():
    tree = ET.parse("truncated_edits.xml")
    root = tree.getroot()

    output_rows = []
    for i, wpedit in enumerate(root.findall("WPEdit")):
        meta = extract_metadata(wpedit)
        title = meta["title"]
        curr_ts = meta["current_timestamp"]
        iso_ts = to_iso8601(curr_ts)

        prev_rev, curr_rev = get_two_revisions(title, iso_ts)
        prev_text = curr_text = ""
        removed_lines = []
        added_lines = []

        if prev_rev and curr_rev:
            prev_text = get_revision_text(prev_rev)
            curr_text = get_revision_text(curr_rev)
            if prev_text != curr_text:
                diff = difflib.unified_diff(
                    prev_text.splitlines(), curr_text.splitlines(),
                    fromfile='previous', tofile='current', lineterm="", n=0)
                for line in diff:
                    if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                        continue  # skip diff headers
                    elif line.startswith("-"):
                        removed_lines.append(line[1:])
                    elif line.startswith("+"):
                        added_lines.append(line[1:])
        meta["removed_content"] = "\n".join(removed_lines)
        meta["added_content"] = "\n".join(added_lines)
        output_rows.append(meta)
        time.sleep(0.5)  # be kind to the API

    # Only keep desired columns
    fieldnames = [
        'EditType', 'EditID', 'comment', 'isvandalism', 'user', 'user_edit_count',
        'user_distinct_pages', 'user_warns', 'user_reg_time', 'prev_user', 'page_made_time',
        'title', 'namespace', 'creator', 'num_recent_edits', 'num_recent_reversions',
        'current_minor', 'current_timestamp', 'previous_timestamp',
        'removed_content', 'added_content'
    ]
    with open("edit_diffs_details.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            # Only write the specified fields
            filtered_row = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(filtered_row)

    print("Done. Output saved.")

if __name__ == "__main__":
    main()

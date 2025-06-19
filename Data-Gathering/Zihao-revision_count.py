import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timedelta
import csv
import time

def to_iso8601(ts):
    if ts and ts.isdigit():
        if len(ts) == 10:  # unix
            return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%dT%H:%M:%SZ')
        elif len(ts) == 14:  # YYYYMMDDHHMMSS
            return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"
    return ts

def to_datetime(ts):
    if ts and ts.isdigit():
        if len(ts) == 10:
            return datetime.utcfromtimestamp(int(ts))
        elif len(ts) == 14:
            return datetime.strptime(ts, "%Y%m%d%H%M%S")
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None

def revision_count(title, start, end):
    url = "https://en.wikipedia.org/w/api.php"
    total = 0
    next_rvcontinue = None
    while True:
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": title,
            "rvstart": start,
            "rvend": end,
            "rvlimit": "max",
            "rvdir": "older",
            "rvprop": "ids"
        }
        if next_rvcontinue:
            params['rvcontinue'] = next_rvcontinue
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            pages = list(data["query"]["pages"].values())
            if not pages or "revisions" not in pages[0]:
                break
            revs = pages[0]["revisions"]
            total += len(revs)
            if "continue" in data:
                next_rvcontinue = data["continue"]["rvcontinue"]
            else:
                break
        except Exception as e:
            break
    return total

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
    all_edits = root.findall("WPEdit")
    output_rows = []
    for i, wpedit in enumerate(all_edits):
        meta = extract_metadata(wpedit)
        title = meta["title"].replace(" ", "_")
        curr_ts = meta["current_timestamp"]
        iso_ts = to_iso8601(curr_ts)
        dt = to_datetime(curr_ts)
        num_before = num_after = ""
        if dt:
            before_start = (dt - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
            before_end   = iso_ts
            after_start  = iso_ts
            after_end    = (dt + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
            num_before = revision_count(title, before_end, before_start)
            num_after  = revision_count(title, after_start, after_end)
        meta["num_revisions_3d_before"] = num_before
        meta["num_revisions_3d_after"] = num_after
        output_rows.append(meta)
        print(f"Edit {i+1}/{len(all_edits)}: {title} | Before: {num_before}, After: {num_after}")
        time.sleep(0.5)  # be kind to API

    fieldnames = [
        'EditType', 'EditID', 'comment', 'isvandalism', 'user', 'user_edit_count',
        'user_distinct_pages', 'user_warns', 'user_reg_time', 'prev_user', 'page_made_time',
        'title', 'namespace', 'creator', 'num_recent_edits', 'num_recent_reversions',
        'current_minor', 'current_timestamp', 'previous_timestamp',
        'num_revisions_3d_before', 'num_revisions_3d_after'
    ]
    with open("edit_revision_freq.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            filtered_row = {k: row.get(k, "") for k in fieldnames}
            writer.writerow(filtered_row)
    print("Done. Output saved as edit_revision_freq.csv")

if __name__ == "__main__":
    main()

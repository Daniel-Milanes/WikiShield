import xml.etree.ElementTree as ET
import requests
import difflib
import time
from datetime import datetime

def to_iso8601(ts):
    # If ts is digits and 10 characters, treat as unix timestamp
    if ts and ts.isdigit():
        if len(ts) == 10:  # unix
            return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%dT%H:%M:%SZ')
        elif len(ts) == 14:  # YYYYMMDDHHMMSS
            return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"
    # Otherwise, return as is
    return ts

def get_two_revisions(title, timestamp):
    S = requests.Session()
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvlimit": 2,
        "rvstart": timestamp,
        "rvdir": "older",  # newest to oldest, so get current and previous
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
                return revs[1]['revid'], revs[0]['revid']  # prev, current
            elif len(revs) == 1:
                # Only one rev, treat as both prev and current
                return revs[0]['revid'], revs[0]['revid']
            else:
                return None, None
        except Exception as e:
            print("API error, retrying...", e)
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
            print("API error, retrying...", e)
            time.sleep(1)
    return ""

def main():
    tree = ET.parse("truncated_edits.xml")
    root = tree.getroot()

    for i, wpedit in enumerate(root.findall("WPEdit")):
        title_elem = wpedit.find("common/title")
        curr_ts_elem = wpedit.find("current/timestamp")
        if title_elem is None or curr_ts_elem is None:
            print(f"Edit {i+1}: missing title or timestamp")
            continue

        title = title_elem.text
        curr_ts = curr_ts_elem.text
        iso_ts = to_iso8601(curr_ts)

        print(f"\nEdit {i+1}: {title} at {iso_ts}")
        prev_rev, curr_rev = get_two_revisions(title, iso_ts)
        if not prev_rev or not curr_rev:
            print("  Could not retrieve two revisions.")
            continue

        prev_text = get_revision_text(prev_rev)
        curr_text = get_revision_text(curr_rev)

        if prev_text == curr_text:
            print("  No difference between previous and current.")
        else:
            print("  There is a difference between previous and current versions.")
            # Show a short diff snippet
            d = difflib.unified_diff(
                prev_text.splitlines(), curr_text.splitlines(),
                fromfile='previous', tofile='current', lineterm="", n=3)
            diff_lines = list(d)
            if diff_lines:
                print("  Diff preview:")
                for line in diff_lines[:12]:
                    print("   ", line)
                if len(diff_lines) > 12:
                    print("   ...")

        # Be nice to the API!
        time.sleep(0.5)

if __name__ == "__main__":
    main()

import pandas as pd
import requests
from datetime import datetime, timedelta
import time

def to_iso8601(ts):
    ts = str(ts)
    if ts.isdigit():
        if len(ts) == 10:  # unix
            return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%dT%H:%M:%SZ')
        elif len(ts) == 14:  # YYYYMMDDHHMMSS
            return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"
    return ts  # fallback

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
        except Exception:
            break
    return total

# --- MAIN PROCESS ---

input_csv = "filtered_edits_no_dup.csv"         # Input filename
output_csv = "filtered_edits_with_edit_counts.csv"  # Output filename

df = pd.read_csv(input_csv)
edit_counts = []

for i, row in df.iterrows():
    title = str(row['title']).replace(" ", "_")
    ts = row['current_timestamp']
    try:
        dt = to_iso8601(ts)
        edit_time = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        start = (edit_time - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (edit_time - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        count = revision_count(title, start, end)
    except Exception as e:
        print(f"Error for {title} @ {ts}: {e}")
        count = ""
    edit_counts.append(count)
    print(f"{i+1}/{len(df)} | {title} | edits in 5d before: {count}")
    if (i+1) % 250 == 0:
        print(f"Pausing for 1 second after {i+1} API calls...")
        time.sleep(1)

df['num_edits_5d_before'] = edit_counts
df.to_csv(output_csv, index=False)
print(f"Done. Output written to {output_csv}")

import xml.etree.ElementTree as ET
from datetime import datetime

def to_datetime(ts):
    if ts and ts.isdigit():
        if len(ts) == 10:  # Unix time
            return datetime.utcfromtimestamp(int(ts))
        elif len(ts) == 14:  # YYYYMMDDHHMMSS
            return datetime.strptime(ts, "%Y%m%d%H%M%S")
    return None

def find_earliest_latest(infile):
    tree = ET.parse(infile)
    root = tree.getroot()
    all_dates = []
    for wpedit in root.findall("WPEdit"):
        ts = None
        curr_ts = wpedit.find("current/timestamp")
        if curr_ts is not None and curr_ts.text:
            ts = curr_ts.text.strip()
            dt = to_datetime(ts)
            if dt is not None:
                all_dates.append(dt)
    if all_dates:
        earliest = min(all_dates)
        latest = max(all_dates)
        print(f"Earliest edit date: {earliest.isoformat()} (UTC)")
        print(f"Latest edit date:   {latest.isoformat()} (UTC)")
    else:
        print("No valid edit timestamps found.")

if __name__ == "__main__":
    infile = "train-edits.xml"  # Change to your XML filename
    find_earliest_latest(infile)

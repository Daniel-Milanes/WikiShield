import requests
import time
import csv
from urllib.parse import quote
from datetime import datetime

WIKI_API = "https://en.wikipedia.org/w/api.php"
PAGEVIEWS_API = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
    "en.wikipedia/all-access/all-agents/"
)

BATCH_SIZE = 20
TOTAL_ARTICLES = 100
SLEEP_BETWEEN_REQUESTS = 0.1
PAGEVIEWS_START = "20150701"
PAGEVIEWS_END = datetime.utcnow().strftime("%Y%m%d")
OUTPUT_CSV = "wiki_articles_full_metadata.csv"
MAX_REVISIONS_PER_ARTICLE = 1000


def get_random_titles(batch_size):
    params = {
        "action": "query",
        "list": "random",
        "rnlimit": batch_size,
        "rnnamespace": 0,
        "format": "json",
    }
    r = requests.get(WIKI_API, params=params)
    r.raise_for_status()
    return [item["title"] for item in r.json()["query"]["random"]]


def get_articles_info(titles):
    params = {
        "action": "query",
        "prop": "extracts|info|categories|extlinks|langlinks|contributors",
        "inprop": "url|talkid|watched|watchers|touched",
        "exintro": 1,
        "explaintext": 1,
        "cllimit": "max",
        "ellimit": "max",
        "lllimit": "max",
        "pclimit": "max",
        "titles": "|".join(titles),
        "format": "json",
    }
    r = requests.get(WIKI_API, params=params)
    r.raise_for_status()
    return r.json()["query"]["pages"]


def get_revisions(title, max_revs=None):
    revisions = []
    rvcontinue = None

    while True:
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvlimit": "max",
            "rvprop": "timestamp|ids",
            "rvdir": "newer",
            "format": "json",
        }
        if rvcontinue:
            params["rvcontinue"] = rvcontinue

        r = requests.get(WIKI_API, params=params)
        r.raise_for_status()
        data = r.json()
        pages = data["query"]["pages"]
        page = next(iter(pages.values()))

        revs = page.get("revisions", [])
        revisions.extend(revs)

        if max_revs and len(revisions) >= max_revs:
            revisions = revisions[:max_revs]
            break

        if "continue" in data:
            rvcontinue = data["continue"].get("rvcontinue")
            if not rvcontinue:
                break
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        else:
            break
    return revisions


def get_backlinks(title, limit=20):
    params = {
        "action": "query",
        "list": "backlinks",
        "bltitle": title,
        "bllimit": limit,
        "format": "json",
    }
    r = requests.get(WIKI_API, params=params)
    r.raise_for_status()
    data = r.json()
    return [link["title"] for link in data.get("query", {}).get("backlinks", [])]


def get_pageviews(title, start_date, end_date):
    formatted_title = quote(title.replace(" ", "_"))
    url = PAGEVIEWS_API + formatted_title + f"/daily/{start_date}/{end_date}"
    headers = {"User-Agent": "WikipediaPageviewsBot/1.0 (ehtandavitt@gmail.com)"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return sum(item["views"] for item in data.get("items", []))
    else:
        return 0


def save_to_csv(filename, rows, write_header=False):
    fieldnames = [
        "title",
        "summary",
        "page_length",
        "categories",
        "revision_count",
        "creation_date",
        "last_edit_date",
        "pageviews_since_2015",
        "last_revid",
        "touched",
        "external_links",
        "lang_links",
        "top_contributors",
        "backlinks",
    ]
    mode = "w" if write_header else "a"
    with open(filename, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for row in rows:
            row["categories"] = ";".join(row["categories"])
            row["external_links"] = ";".join(row["external_links"])
            row["lang_links"] = ";".join(row["lang_links"])
            row["top_contributors"] = ";".join(row["top_contributors"])
            row["backlinks"] = ";".join(row["backlinks"])
            writer.writerow(row)


def main():
    total_collected = 0
    write_header = True

    while total_collected < TOTAL_ARTICLES:
        try:
            titles = get_random_titles(BATCH_SIZE)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            pages = get_articles_info(titles)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            batch_data = []

            for page_id, page in pages.items():
                title = page.get("title")
                summary = page.get("extract", "")
                page_length = page.get("length", 0)
                categories = [cat["title"] for cat in page.get("categories", [])]

                last_revid = page.get("lastrevid", "")
                touched = page.get("touched", "")
                external_links = [link["*"] for link in page.get("extlinks", [])]
                lang_links = [lang["*"] for lang in page.get("langlinks", [])]
                top_contributors = [
                    contrib.get("name", "") for contrib in page.get("contributors", [])
                ]

                revisions = get_revisions(title, max_revs=MAX_REVISIONS_PER_ARTICLE)
                time.sleep(SLEEP_BETWEEN_REQUESTS)

                if revisions:
                    creation_date = revisions[0]["timestamp"]
                    last_edit_date = revisions[-1]["timestamp"]
                    revision_count = len(revisions)
                else:
                    creation_date = ""
                    last_edit_date = ""
                    revision_count = 0

                pageviews = get_pageviews(title, PAGEVIEWS_START, PAGEVIEWS_END)
                time.sleep(SLEEP_BETWEEN_REQUESTS)

                backlinks = get_backlinks(title)
                time.sleep(SLEEP_BETWEEN_REQUESTS)

                record = {
                    "title": title,
                    "summary": summary,
                    "page_length": page_length,
                    "categories": categories,
                    "revision_count": revision_count,
                    "creation_date": creation_date,
                    "last_edit_date": last_edit_date,
                    "pageviews_since_2015": pageviews,
                    "last_revid": last_revid,
                    "touched": touched,
                    "external_links": external_links,
                    "lang_links": lang_links,
                    "top_contributors": top_contributors,
                    "backlinks": backlinks,
                }
                batch_data.append(record)

            save_to_csv(OUTPUT_CSV, batch_data, write_header=write_header)
            write_header = False
            total_collected += len(batch_data)
            print(f"Collected {total_collected}/{TOTAL_ARTICLES} articles.")

        except Exception as e:
            print(f"Error: {e}. Retrying after delay.")
            time.sleep(5)

    print(f"Done! Data saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

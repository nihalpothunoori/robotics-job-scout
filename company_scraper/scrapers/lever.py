import requests

API = "https://api.lever.co/v0/postings/{slug}?mode=json"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape(company: str, slug: str) -> list[dict]:
    try:
        r = requests.get(API.format(slug=slug), headers=HEADERS, timeout=15)
        r.raise_for_status()
        postings = r.json()
    except Exception as e:
        print(f"[lever:{company}] {e}")
        return []

    jobs = []
    for p in postings:
        title = p.get("text", "")
        url = p.get("hostedUrl") or p.get("applyUrl", "")
        job_id = p.get("id", url)
        desc = (p.get("descriptionPlain") or p.get("description") or "")[:500]
        jobs.append({"id": f"lever::{slug}::{job_id}", "company": company,
                     "title": title, "url": url, "description": desc})
    return jobs

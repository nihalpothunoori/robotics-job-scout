import requests

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape(company: str, slug: str) -> list[dict]:
    try:
        r = requests.get(API.format(slug=slug), headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[greenhouse:{company}] {e}")
        return []

    jobs = []
    for p in data.get("jobs", []):
        title = p.get("title", "")
        url = p.get("absolute_url", "")
        job_id = str(p.get("id", url))
        desc = (p.get("content") or "")[:500]
        jobs.append({"id": f"greenhouse::{slug}::{job_id}", "company": company,
                     "title": title, "url": url, "description": desc})
    return jobs

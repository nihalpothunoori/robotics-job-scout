import requests
from datetime import datetime, timezone, timedelta

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_AGE_HOURS = 24


def _within_24h(updated_at: str) -> bool:
    if not updated_at:
        return True  # no date — don't discard
    try:
        dt = datetime.fromisoformat(updated_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - dt <= timedelta(hours=MAX_AGE_HOURS)
    except ValueError:
        return True


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
        if not _within_24h(p.get("updated_at", "")):
            continue
        title = p.get("title", "")
        url = p.get("absolute_url", "")
        job_id = str(p.get("id", url))
        desc = (p.get("content") or "")[:500]
        jobs.append({"id": f"greenhouse::{slug}::{job_id}", "company": company,
                     "title": title, "url": url, "description": desc,
                     "date_posted": p.get("updated_at", "")})
    return jobs

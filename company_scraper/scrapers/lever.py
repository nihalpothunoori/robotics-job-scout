import requests
from datetime import datetime, timezone, timedelta

API = "https://api.lever.co/v0/postings/{slug}?mode=json"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_AGE_HOURS = 24


def _within_24h(created_at_ms) -> bool:
    if not created_at_ms:
        return True  # no date — don't discard
    try:
        dt = datetime.fromtimestamp(int(created_at_ms) / 1000, tz=timezone.utc)
        return datetime.now(timezone.utc) - dt <= timedelta(hours=MAX_AGE_HOURS)
    except (ValueError, TypeError):
        return True


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
        if not _within_24h(p.get("createdAt")):
            continue
        title = p.get("text", "")
        url = p.get("hostedUrl") or p.get("applyUrl", "")
        job_id = p.get("id", url)
        desc = (p.get("descriptionPlain") or p.get("description") or "")[:500]
        created_ms = p.get("createdAt")
        date_str = (
            datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc).isoformat()
            if created_ms else ""
        )
        jobs.append({"id": f"lever::{slug}::{job_id}", "company": company,
                     "title": title, "url": url, "description": desc,
                     "date_posted": date_str})
    return jobs

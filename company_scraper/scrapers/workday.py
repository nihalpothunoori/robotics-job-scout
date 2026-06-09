"""Workday public REST API scraper.

Workday exposes a public JSON API for career sites that don't require auth.
Endpoint: POST https://{sub}.wd{n}.myworkdayjobs.com/wday/cxs/{sub}/{tenant}/jobs
"""
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
PAGE_SIZE = 20


def scrape(company: str, slug: str) -> list[dict]:
    """slug format: '{sub}:{n}:{tenant}'  e.g. 'nvidia:5:NVIDIAExternalCareerSite'"""
    try:
        sub, n, tenant = slug.split(":", 2)
    except ValueError:
        print(f"[workday:{company}] bad slug '{slug}' — expected 'sub:n:tenant'")
        return []

    base = f"https://{sub}.wd{n}.myworkdayjobs.com/wday/cxs/{sub}/{tenant}"
    jobs = []
    offset = 0

    while True:
        body = {"appliedFacets": {}, "limit": PAGE_SIZE, "offset": offset, "searchText": "intern"}
        try:
            r = requests.post(f"{base}/jobs", json=body, headers=HEADERS, timeout=15)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[workday:{company}] {e}")
            break

        postings = data.get("jobPostings") or []
        for p in postings:
            title = p.get("title", "")
            external_path = p.get("externalPath", "")
            job_id = p.get("bulletFields", [None])[0] or external_path
            url = f"https://{sub}.wd{n}.myworkdayjobs.com/en-US/{tenant}{external_path}"
            jobs.append({
                "id": f"workday::{sub}::{job_id}",
                "company": company,
                "title": title,
                "url": url,
                "description": "",
                "date_posted": "",
            })

        total = data.get("total", 0)
        offset += PAGE_SIZE
        if offset >= total or not postings:
            break

    return jobs

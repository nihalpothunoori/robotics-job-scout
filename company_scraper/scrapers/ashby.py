import requests

API = "https://api.ashbyhq.com/posting-public/apikey/job-board/{slug}"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape(company: str, slug: str) -> list[dict]:
    try:
        r = requests.get(API.format(slug=slug), headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[ashby:{company}] {e}")
        return []

    jobs = []
    for p in data.get("jobPostings", []):
        title = p.get("title", "")
        path = p.get("jobPostingPath", "")
        url = path if path.startswith("http") else f"https://jobs.ashbyhq.com/{slug}/{path.lstrip('/')}"
        job_id = p.get("id", url)
        desc = (p.get("descriptionPlain") or p.get("description") or "")[:500]
        jobs.append({"id": f"ashby::{slug}::{job_id}", "company": company,
                     "title": title, "url": url, "description": desc})
    return jobs

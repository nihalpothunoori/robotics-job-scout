"""
Scrape Ashby job boards that require JavaScript (private API, 401 on REST).
Uses Playwright to render jobs.ashbyhq.com/{slug} and extract job listings.
Falls back gracefully if playwright is not installed.
"""
import sys

BASE = "https://jobs.ashbyhq.com"


def scrape(company: str, slug: str) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print(f"[pw-ashby:{company}] playwright not installed, skipping", file=sys.stderr)
        return []

    url = f"{BASE}/{slug}"
    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000, wait_until="networkidle")

            # Wait for at least one job link to appear
            try:
                page.wait_for_selector(f"a[href^='/{slug}/']", timeout=8000)
            except PWTimeout:
                pass

            # Ashby job links are /{slug}/{uuid} — grab all of them
            elements = page.query_selector_all(f"a[href^='/{slug}/']")
            seen_hrefs: set[str] = set()
            for el in elements:
                href = el.get_attribute("href") or ""
                if not href or href in seen_hrefs:
                    continue
                seen_hrefs.add(href)

                # Title is the first non-empty line of the link text
                raw_text = el.inner_text().strip()
                title = raw_text.split("\n")[0].strip()
                if not title or len(title) < 3:
                    continue

                job_url = f"{BASE}{href}"
                jobs.append({
                    "id": f"ashby::{slug}::{href}",
                    "company": company,
                    "title": title,
                    "url": job_url,
                    "description": "",
                })

            browser.close()
    except Exception as e:
        print(f"[pw-ashby:{company}] {e}", file=sys.stderr)

    return jobs

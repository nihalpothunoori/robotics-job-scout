"""
Scrape Ashby job boards that require JavaScript (private API, 401 on REST).
Uses Playwright to render the page and extract job listings.
Falls back gracefully if playwright is not installed.
"""
import sys

def scrape(company: str, slug: str) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print(f"[pw-ashby:{company}] playwright not installed, skipping", file=sys.stderr)
        return []

    url = f"https://jobs.ashbyhq.com/{slug}"
    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000, wait_until="networkidle")

            # Wait for job list items to appear
            try:
                page.wait_for_selector("[data-testid='job-listing-item'], a[href*='/jobs/'], .ashby-job-posting-brief", timeout=8000)
            except PWTimeout:
                pass

            # Try multiple selector patterns Ashby uses
            selectors = [
                ("[data-testid='job-listing-item']",
                 lambda el: (el.inner_text().split("\n")[0].strip(),
                             el.get_attribute("href") or "")),
                ("a[href*='/jobs/']",
                 lambda el: (el.inner_text().strip(),
                             el.get_attribute("href") or "")),
                (".ashby-job-posting-brief-title",
                 lambda el: (el.inner_text().strip(), "")),
            ]

            for selector, extractor in selectors:
                elements = page.query_selector_all(selector)
                if not elements:
                    continue
                for el in elements:
                    try:
                        title, href = extractor(el)
                        if not title or len(title) < 3:
                            continue
                        if href and not href.startswith("http"):
                            href = f"https://jobs.ashbyhq.com{href}"
                        job_url = href or url
                        jobs.append({
                            "id": f"ashby::{slug}::{title}",
                            "company": company,
                            "title": title,
                            "url": job_url,
                            "description": "",
                        })
                    except Exception:
                        continue
                if jobs:
                    break

            browser.close()
    except Exception as e:
        print(f"[pw-ashby:{company}] {e}", file=sys.stderr)

    return jobs

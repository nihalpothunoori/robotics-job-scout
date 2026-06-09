"""Scrape Tesla careers via Playwright.

Tesla's career API (cua-api/tesla-jobs/search) requires session cookies and
returns 429/403 for unauthenticated requests. Playwright renders the SPA and
extracts job cards from the rendered DOM.
"""
import sys

BASE = "https://www.tesla.com"
SEARCH_URL = f"{BASE}/careers/search#/?query=intern&department=Engineering"


def scrape(company: str, slug: str) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print(f"[pw-tesla:{company}] playwright not installed, skipping", file=sys.stderr)
        return []

    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="en-US",
            )
            page = ctx.new_page()
            page.goto(SEARCH_URL, timeout=30000, wait_until="networkidle")

            # Wait for job cards to render
            try:
                page.wait_for_selector("a[href*='/careers/search/job/']", timeout=12000)
            except PWTimeout:
                pass

            seen: set[str] = set()
            for el in page.query_selector_all("a[href*='/careers/search/job/']"):
                href = el.get_attribute("href") or ""
                if not href or href in seen:
                    continue
                seen.add(href)

                # Extract job ID from URL slug: /careers/search/job/{slug}-{id}
                parts = href.rstrip("/").split("-")
                job_id = parts[-1] if parts[-1].isdigit() else href

                raw = el.inner_text().strip()
                title = raw.split("\n")[0].strip()
                if not title or len(title) < 3:
                    continue

                url = href if href.startswith("http") else f"{BASE}{href}"
                jobs.append({
                    "id": f"tesla::{job_id}",
                    "company": company,
                    "title": title,
                    "url": url,
                    "description": "",
                    "date_posted": "",
                })

            browser.close()
    except Exception as e:
        print(f"[pw-tesla:{company}] {e}", file=sys.stderr)

    return jobs

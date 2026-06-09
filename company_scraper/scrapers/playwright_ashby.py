"""
Scrape Ashby job boards that require JavaScript (private API, 401 on REST).
Uses async Playwright to render all companies in one shared browser instance.
"""
import asyncio
import sys

BASE = "https://jobs.ashbyhq.com"


async def _scrape_page(browser, company: str, slug: str, sem: asyncio.Semaphore) -> list[dict]:
    from playwright.async_api import TimeoutError as PWTimeout
    jobs = []
    url = f"{BASE}/{slug}"
    async with sem:
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=20000, wait_until="networkidle")
            try:
                await page.wait_for_selector(f"a[href^='/{slug}/']", timeout=8000)
            except PWTimeout:
                pass

            elements = await page.query_selector_all(f"a[href^='/{slug}/']")
            seen_hrefs: set[str] = set()
            seen_titles: set[str] = set()
            for el in elements:
                href = await el.get_attribute("href") or ""
                if not href or href in seen_hrefs:
                    continue
                seen_hrefs.add(href)
                raw = await el.inner_text()
                title = raw.strip().split("\n")[0].strip()
                if not title or len(title) < 3:
                    continue
                title_key = title.lower()
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)
                jobs.append({
                    "id": f"ashby::{slug}::{href}",
                    "company": company,
                    "title": title,
                    "url": f"{BASE}{href}",
                    "description": "",
                    "_ats": "playwright_ashby",
                    "_slug": slug,
                })
        except Exception as e:
            print(f"[pw-ashby:{company}] {e}", file=sys.stderr)
        finally:
            await page.close()
    return jobs


async def _run_batch(companies_and_slugs: list[tuple[str, str]]) -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[pw-ashby] playwright not installed, skipping", file=sys.stderr)
        return []

    # Cap concurrent pages to avoid overwhelming the runner
    sem = asyncio.Semaphore(8)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [_scrape_page(browser, c, s, sem) for c, s in companies_and_slugs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        await browser.close()

    all_jobs = []
    for r in results:
        if isinstance(r, list):
            all_jobs.extend(r)
    return all_jobs


def scrape_batch(companies_and_slugs: list[tuple[str, str]]) -> list[dict]:
    """Scrape multiple Ashby boards sharing one browser instance."""
    return asyncio.run(_run_batch(companies_and_slugs))


def scrape(company: str, slug: str) -> list[dict]:
    return scrape_batch([(company, slug)])

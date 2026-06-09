"""X/Twitter scraper via Nitter (open-source Twitter frontend, no auth needed).

Tries multiple public Nitter instances in order; skips to the next if one
is down. Fails gracefully — if all instances are unreachable, this source
contributes 0 results without breaking the rest of the scrape.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone, timedelta

import httpx
from bs4 import BeautifulSoup

from job_scout.models import Job, Location, ScrapeParams, Site
from job_scout.scrapers import BaseScraper

log = logging.getLogger("job_scout.scrapers.twitter")

# Public Nitter instances — tried in order, first working one is used.
# List sourced from https://status.d420.de (updated periodically).
_INSTANCES = [
    "https://nitter.privacyredirect.com",
    "https://nitter.poast.org",
    "https://nitter.tiekoetter.com",
    "https://nitter.space",
    "https://nitter.privacydev.net",
    "https://nitter.1d4.us",
    "https://nitter.cz",
    "https://xcancel.com",
    "https://nitter.unixfox.eu",
    "https://nitter.moomoo.me",
    "https://nitter.lunar.icu",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Deduplicate tweet IDs within a single process run
_seen_tweet_ids: set[str] = set()
# Cache which instance is working so we don't re-probe every search
_working_instance: str | None = None


class TwitterScraper(BaseScraper):
    site = Site.TWITTER

    def scrape(self, params: ScrapeParams) -> list[Job]:
        global _working_instance

        instance = _working_instance or _find_working_instance()
        if not instance:
            log.warning("Nitter: all instances unreachable — skipping Twitter source")
            return []
        _working_instance = instance

        query = _build_query(params.search_term)
        tweets = _search(instance, query, max_results=params.results_wanted)
        jobs = [j for t in tweets if (j := _parse_tweet(t, instance)) is not None]
        log.info(f"Nitter ({instance}): '{params.search_term}' → {len(jobs)} tweets")
        return jobs


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _find_working_instance() -> str | None:
    for base in _INSTANCES:
        try:
            r = httpx.get(f"{base}/search?q=test", headers=_HEADERS, timeout=8, follow_redirects=True)
            if r.status_code == 200 and "nitter" in r.text.lower():
                log.info(f"Nitter: using {base}")
                return base
        except Exception:
            pass
    return None


def _build_query(search_term: str) -> str:
    return f'({search_term}) (intern OR internship OR hiring OR "job opening") lang:en'


def _search(instance: str, query: str, max_results: int) -> list[dict]:
    url = f"{instance}/search"
    try:
        resp = httpx.get(
            url,
            params={"q": query, "f": "tweets"},
            headers=_HEADERS,
            timeout=15,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            log.warning(f"Nitter search returned {resp.status_code}")
            return []
        return _parse_html(resp.text, instance, max_results)
    except Exception as e:
        log.warning(f"Nitter search failed: {e}")
        return []


def _parse_html(html: str, instance: str, max_results: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".timeline-item")
    results = []
    for item in items[:max_results]:
        try:
            # tweet text
            content_el = item.select_one(".tweet-content")
            text = content_el.get_text(" ", strip=True) if content_el else ""
            if not text:
                continue

            # tweet URL  →  /username/status/1234567890
            link_el = item.select_one("a.tweet-link")
            path = link_el["href"] if link_el else ""
            tweet_id = path.split("/")[-1] if path else ""
            if not tweet_id or tweet_id in _seen_tweet_ids:
                continue
            _seen_tweet_ids.add(tweet_id)

            # author
            user_el = item.select_one(".username")
            screen_name = user_el.get_text(strip=True).lstrip("@") if user_el else "unknown"
            name_el = item.select_one(".fullname")
            display_name = name_el.get_text(strip=True) if name_el else screen_name

            # date  — Nitter renders e.g. title="Jun 7, 2025 · 3:42 PM UTC"
            date_el = item.select_one(".tweet-date a")
            date_posted = None
            if date_el:
                title = date_el.get("title", "")
                date_posted = _parse_nitter_date(title)

            # first external URL in tweet (may be a job link)
            expanded_url = None
            for a in item.select(".tweet-content a[href]"):
                href = a["href"]
                if href.startswith("http") and "twitter.com" not in href and "x.com" not in href:
                    expanded_url = href
                    break

            tweet_url = f"https://x.com/{screen_name}/status/{tweet_id}"

            results.append({
                "id": tweet_id,
                "text": text,
                "display_name": display_name,
                "screen_name": screen_name,
                "date_posted": date_posted,
                "job_url": expanded_url or tweet_url,
                "tweet_url": tweet_url,
            })
        except Exception:
            continue
    return results


def _parse_nitter_date(title: str) -> datetime | None:
    """Parse Nitter date title like 'Jun 7, 2025 · 3:42 PM UTC'."""
    if not title:
        return None
    # Strip the time portion after ·
    date_part = title.split("·")[0].strip()
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_part, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _parse_tweet(t: dict, instance: str) -> Job | None:
    try:
        date_posted = t.get("date_posted")

        # Apply 24-hour recency filter
        if date_posted:
            age = datetime.now(timezone.utc) - date_posted
            if age > timedelta(hours=24):
                return None

        return Job(
            source=Site.TWITTER,
            source_id=t["id"],
            url=t["job_url"],
            title=t["text"][:120].strip(),
            company=t["display_name"],
            location=Location(is_remote=True),
            description=t["text"],
            date_posted=date_posted.date() if date_posted else None,
        )
    except Exception as e:
        log.debug(f"Nitter: failed to parse tweet: {e}")
        return None

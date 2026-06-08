"""X/Twitter scraper using Twitter's guest API (no developer account needed).

Searches for job-related tweets from robotics companies and researchers.
Fails gracefully — if Twitter blocks the guest token the rest of the
scrape continues normally, this source just contributes 0 results.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

import httpx

from job_scout.models import Job, Location, ScrapeParams, Site
from job_scout.scrapers import BaseScraper

log = logging.getLogger("job_scout.scrapers.twitter")

# Twitter's own web-client bearer token (publicly documented, used by every
# unofficial Twitter library).  Provides guest-level read access only.
_BEARER = (
    "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I7BeIYXBO8E%3D"
    "IEefLbqFkeMsvMsYWhNuOtpi57R7tpISKZokirAIcYSzYILclEWF"
)

_ACTIVATE_URL = "https://api.twitter.com/1.1/guest/activate.json"
_SEARCH_URL = "https://api.twitter.com/1.1/search/tweets.json"
_TWEET_URL = "https://twitter.com/{screen_name}/status/{tweet_id}"

# Deduplicate within the same process run — avoids searching the same term
# twice when the CLI iterates over multiple locations.
_searched_terms: set[str] = set()


class TwitterScraper(BaseScraper):
    site = Site.TWITTER

    def scrape(self, params: ScrapeParams) -> list[Job]:
        # Skip duplicate search terms within a single run
        key = params.search_term.lower().strip()
        if key in _searched_terms:
            return []
        _searched_terms.add(key)

        guest_token = self._get_guest_token()
        if not guest_token:
            log.warning("Twitter: could not get guest token — skipping")
            return []

        query = self._build_query(params.search_term)
        raw = self._search(guest_token, query, count=min(params.results_wanted, 50))
        jobs = [j for t in raw if (j := self._parse_tweet(t)) is not None]
        log.info(f"Twitter: '{params.search_term}' → {len(jobs)} tweets")
        return jobs

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_guest_token(self) -> str | None:
        try:
            resp = httpx.post(
                _ACTIVATE_URL,
                headers={"Authorization": f"Bearer {_BEARER}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("guest_token")
            log.warning(f"Twitter guest activate returned {resp.status_code}")
        except Exception as e:
            log.warning(f"Twitter guest activate failed: {e}")
        return None

    def _search(self, guest_token: str, query: str, count: int) -> list[dict]:
        try:
            resp = httpx.get(
                _SEARCH_URL,
                params={
                    "q": query,
                    "count": count,
                    "tweet_mode": "extended",
                    "lang": "en",
                    "result_type": "recent",
                },
                headers={
                    "Authorization": f"Bearer {_BEARER}",
                    "x-guest-token": guest_token,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json().get("statuses", [])
            log.warning(f"Twitter search returned {resp.status_code} for: {query}")
        except Exception as e:
            log.warning(f"Twitter search failed: {e}")
        return []

    @staticmethod
    def _build_query(search_term: str) -> str:
        """Turn a generic job-board search term into a Twitter-optimised query."""
        hiring_terms = (
            "hiring OR \"we're hiring\" OR \"job opening\" OR internship OR intern"
        )
        return f'({search_term}) ({hiring_terms}) lang:en -is:retweet'

    def _parse_tweet(self, t: dict) -> Job | None:
        try:
            tweet_id = t.get("id_str", "")
            if not tweet_id or self._is_dup(tweet_id):
                return None

            user = t.get("user", {})
            screen_name = user.get("screen_name", "unknown")
            display_name = user.get("name", screen_name)

            text: str = t.get("full_text") or t.get("text") or ""

            # Use first URL in tweet as job link if present, else link to tweet
            job_url = _extract_first_url(t) or _TWEET_URL.format(
                screen_name=screen_name, tweet_id=tweet_id
            )

            # Parse creation date
            date_posted = None
            created_raw = t.get("created_at", "")
            if created_raw:
                try:
                    date_posted = datetime.strptime(
                        created_raw, "%a %b %d %H:%M:%S +0000 %Y"
                    ).replace(tzinfo=timezone.utc).date()
                except ValueError:
                    pass

            # Use first 120 chars of tweet as "title" for scoring
            title = text[:120].strip()

            return Job(
                source=Site.TWITTER,
                source_id=tweet_id,
                url=job_url,
                title=title,
                company=display_name,
                location=Location(is_remote=True),
                description=text,
                date_posted=date_posted,
            )
        except Exception as e:
            log.debug(f"Twitter: failed to parse tweet: {e}")
            return None


def _extract_first_url(tweet: dict) -> str | None:
    """Return the first expanded URL from the tweet's entities, if any."""
    entities = tweet.get("entities", {})
    urls = entities.get("urls", [])
    for u in urls:
        expanded = u.get("expanded_url", "")
        # Skip t.co self-links and twitter.com links
        if expanded and "twitter.com" not in expanded and "t.co" not in expanded:
            return expanded
    return None

#!/usr/bin/env python3
"""Scrape intern job postings directly from top robotics company career pages."""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from companies import COMPANIES
from filter import is_relevant
from notifier import send_jobs
from scrapers import ashby, greenhouse, lever

STATE_FILE = Path(__file__).parent / "state.json"
SCRAPER = {"lever": lever.scrape, "greenhouse": greenhouse.scrape, "ashby": ashby.scrape}


def load_seen() -> set:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()).get("seen", []))
    return set()


def save_seen(seen: set) -> None:
    STATE_FILE.write_text(json.dumps({"seen": sorted(seen)}, indent=2))


def fetch(company, ats, slug) -> list[dict]:
    fn = SCRAPER.get(ats)
    if not fn:
        return []
    try:
        return fn(company, slug)
    except Exception as e:
        print(f"[{company}] error: {e}", file=sys.stderr)
        return []


def main() -> None:
    seen = load_seen()
    all_jobs: list[dict] = []

    # Hit all company APIs in parallel — they're official public endpoints,
    # no rate-limit concerns, no scraping delays needed.
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(fetch, c, a, s): c for c, a, s in COMPANIES}
        for future in as_completed(futures):
            all_jobs.extend(future.result())

    new_jobs = [
        j for j in all_jobs
        if j["id"] not in seen and is_relevant(j["title"], j.get("description", ""))
    ]

    for j in new_jobs:
        seen.add(j["id"])

    save_seen(seen)

    if new_jobs:
        print(f"Sending {len(new_jobs)} new intern postings to Discord")
        send_jobs(new_jobs)
    else:
        print("No new intern postings found")


if __name__ == "__main__":
    main()

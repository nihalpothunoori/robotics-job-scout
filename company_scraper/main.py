#!/usr/bin/env python3
"""Scrape career pages of top robotics companies directly via ATS public APIs."""

import json
import sys
from pathlib import Path

from companies import COMPANIES
from filter import is_relevant
from notifier import send_jobs
from scrapers import ashby, greenhouse, lever

STATE_FILE = Path(__file__).parent / "state.json"


def load_seen() -> set:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()).get("seen", []))
    return set()


def save_seen(seen: set) -> None:
    STATE_FILE.write_text(json.dumps({"seen": sorted(seen)}, indent=2))


SCRAPER = {"lever": lever.scrape, "greenhouse": greenhouse.scrape, "ashby": ashby.scrape}


def main() -> None:
    seen = load_seen()
    new_jobs: list[dict] = []

    for company, ats, slug in COMPANIES:
        fn = SCRAPER.get(ats)
        if not fn:
            continue
        try:
            jobs = fn(company, slug)
        except Exception as e:
            print(f"[{company}] unexpected error: {e}", file=sys.stderr)
            continue

        for job in jobs:
            if job["id"] not in seen and is_relevant(job["title"], job.get("description", "")):
                new_jobs.append(job)
                seen.add(job["id"])

    save_seen(seen)

    if new_jobs:
        print(f"Sending {len(new_jobs)} new jobs to Discord")
        send_jobs(new_jobs)
    else:
        print("No new relevant jobs found")


if __name__ == "__main__":
    main()

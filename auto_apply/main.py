#!/usr/bin/env python3
"""
Auto-apply pipeline. Reads new jobs from company_scraper/state.json,
scores each with Claude, and submits applications for score >= 70.

Expects env vars:
  ANTHROPIC_API_KEY   — for Claude job analysis
  DISCORD_WEBHOOK_JOBS — for notifications
"""
import json
import sys
from pathlib import Path

# Allow importing from company_scraper directory
sys.path.insert(0, str(Path(__file__).parent.parent / "company_scraper"))

from job_analyzer import analyze_job
from applicator import apply
from notifier import notify_applied, notify_skipped

STATE_FILE    = Path(__file__).parent.parent / "company_scraper" / "state.json"
APPLIED_FILE  = Path(__file__).parent / "applied.json"
MIN_SCORE     = 70   # skip below this


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def load_applied() -> set:
    if APPLIED_FILE.exists():
        return set(json.loads(APPLIED_FILE.read_text()).get("applied", []))
    return set()


def save_applied(applied: set) -> None:
    APPLIED_FILE.write_text(json.dumps({"applied": sorted(applied)}, indent=2))


def main() -> None:
    state = load_state()
    applied = load_applied()

    # state.json has {"seen": ["id1", ...], "jobs": [{job dict}, ...]}
    # If jobs list not present, we don't have details to apply — skip
    jobs = state.get("jobs", [])
    if not jobs:
        print("No job details in state.json — nothing to process")
        print("(Company scraper must be updated to save job details alongside seen IDs)")
        return

    new_jobs = [j for j in jobs if j.get("id") not in applied]
    print(f"{len(new_jobs)} new jobs to evaluate (already applied to {len(applied)})")

    for job in new_jobs:
        jid = job.get("id", "")
        print(f"\n→ Analyzing: {job.get('company')} — {job.get('title')}")

        try:
            analysis = analyze_job(job)
        except Exception as e:
            print(f"  Claude analysis failed: {e}", file=sys.stderr)
            continue

        score = analysis.get("score", 0)
        print(f"  Score: {score}/100  Verdict: {analysis.get('verdict')}")

        if score < MIN_SCORE:
            print(f"  Skipping (score {score} < {MIN_SCORE})")
            notify_skipped(job, analysis)
            applied.add(jid)
            continue

        print(f"  Applying...")
        result = apply(job, analysis)
        print(f"  Result: {result.get('message', '')}")

        notify_applied(job, analysis, result)
        applied.add(jid)

    save_applied(applied)
    print(f"\nDone. Processed {len(new_jobs)} jobs.")


if __name__ == "__main__":
    main()

import os
import requests
from datetime import datetime, timezone

WEBHOOK = os.environ["DISCORD_WEBHOOK_JOBS"]
CHUNK = 25
EMBED_COLOR = 0x5865F2


def _fmt_date(date_str: str) -> str:
    """Convert ISO date string to readable relative time."""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - dt
        minutes = int(delta.total_seconds() / 60)
        if minutes < 60:
            return f"posted {minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"posted {hours}h ago"
        return f"posted {delta.days}d ago"
    except Exception:
        return ""


def send_jobs(jobs: list[dict]) -> None:
    for i in range(0, len(jobs), CHUNK):
        batch = jobs[i : i + CHUNK]
        fields = []
        for j in batch:
            age = _fmt_date(j.get("date_posted", ""))
            age_str = f" · {age}" if age else " · just posted"
            fields.append({
                "name": f"🏢 {j['company']}",
                "value": f"[{j['title']}]({j['url']}){age_str}",
                "inline": False,
            })

        total = len(jobs)
        n_chunks = -(-total // CHUNK)
        chunk_label = f" ({i // CHUNK + 1}/{n_chunks})" if n_chunks > 1 else ""
        payload = {
            "embeds": [{
                "title": f"🤖 {total} new intern posting{'s' if total != 1 else ''}{chunk_label}",
                "color": EMBED_COLOR,
                "fields": fields,
                "footer": {"text": "robotics-job-scout · direct career page APIs"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }]
        }
        requests.post(WEBHOOK, json=payload, timeout=10).raise_for_status()

import os
import requests
from datetime import datetime, timezone

WEBHOOK = os.environ["DISCORD_WEBHOOK_JOBS"]
CHUNK = 25  # max embed fields per Discord message
EMBED_COLOR = 0x5865F2  # Discord blurple


def send_jobs(jobs: list[dict]) -> None:
    for i in range(0, len(jobs), CHUNK):
        batch = jobs[i : i + CHUNK]
        fields = []
        for j in batch:
            fields.append({
                "name": f"🏢 {j['company']}",
                "value": f"[{j['title']}]({j['url']})",
                "inline": False,
            })

        total = len(jobs)
        n_chunks = -(-total // CHUNK)  # ceiling division
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

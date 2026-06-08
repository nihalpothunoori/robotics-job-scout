import os
import requests

WEBHOOK = os.environ["DISCORD_WEBHOOK_JOBS"]
CHUNK = 20  # max fields per Discord embed


def send_jobs(jobs: list[dict]) -> None:
    for i in range(0, len(jobs), CHUNK):
        batch = jobs[i:i + CHUNK]
        fields = [
            {"name": f"🏢 {j['company']}", "value": f"[{j['title']}]({j['url']})", "inline": False}
            for j in batch
        ]
        payload = {"embeds": [{
            "title": f"🤖 {len(jobs)} new job{'s' if len(jobs) != 1 else ''} from company career pages",
            "color": 0x57F287,
            "fields": fields,
            "footer": {"text": "Direct company scraper"},
        }]}
        requests.post(WEBHOOK, json=payload, timeout=10).raise_for_status()

"""Discord notifications for auto-apply results."""
import os
import requests
from datetime import datetime, timezone

WEBHOOK = os.environ["DISCORD_WEBHOOK_JOBS"]
EMBED_COLOR_APPLIED = 0x57F287   # green = applied
EMBED_COLOR_SKIP    = 0xFEE75C   # yellow = skipped
EMBED_COLOR_FAIL    = 0xED4245   # red = error


def _score_bar(score: int) -> str:
    filled = round(score / 10)
    return "█" * filled + "░" * (10 - filled)


def notify_applied(job: dict, analysis: dict, result: dict) -> None:
    score = analysis.get("score", 0)
    strengths = "\n".join(f"+ {s}" for s in analysis.get("strengths", [])[:3])
    gaps = "\n".join(f"- {g}" for g in analysis.get("gaps", [])[:2])
    cl_preview = (analysis.get("cover_letter") or "")[:300]

    status_line = "✅ Application submitted" if result.get("success") else f"⚠️ {result.get('message','')[:100]}"

    fields = [
        {"name": "Match Score", "value": f"`{score}/100` {_score_bar(score)}", "inline": True},
        {"name": "Status", "value": status_line, "inline": True},
    ]
    if strengths:
        fields.append({"name": "Why it fits", "value": f"```{strengths}```", "inline": False})
    if gaps:
        fields.append({"name": "Gaps", "value": f"```{gaps}```", "inline": False})
    if cl_preview:
        fields.append({"name": "Cover letter (preview)", "value": f"```{cl_preview}...```", "inline": False})

    color = EMBED_COLOR_APPLIED if result.get("success") else EMBED_COLOR_FAIL
    payload = {
        "embeds": [{
            "title": f"🤖 Applied: {job['company']} — {job['title']}",
            "url": job.get("url", ""),
            "color": color,
            "fields": fields,
            "footer": {"text": "robotics-job-scout · auto-apply"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
    }
    requests.post(WEBHOOK, json=payload, timeout=10)


def notify_skipped(job: dict, analysis: dict) -> None:
    score = analysis.get("score", 0)
    gaps = "\n".join(f"- {g}" for g in analysis.get("gaps", [])[:3])
    fields = [
        {"name": "Match Score", "value": f"`{score}/100` {_score_bar(score)}", "inline": True},
        {"name": "Decision", "value": "Skipped (score < 70)", "inline": True},
    ]
    if gaps:
        fields.append({"name": "Why skipped", "value": f"```{gaps}```", "inline": False})

    payload = {
        "embeds": [{
            "title": f"⏭️ Skipped: {job['company']} — {job['title']}",
            "url": job.get("url", ""),
            "color": EMBED_COLOR_SKIP,
            "fields": fields,
            "footer": {"text": "robotics-job-scout · auto-apply"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
    }
    requests.post(WEBHOOK, json=payload, timeout=10)

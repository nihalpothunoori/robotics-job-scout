"""
Submit applications via Greenhouse and Lever public job board APIs.
"""
import io
import re
import sys
import requests
from personal_info import PROFILE, RESUME_PDF_URL

_session = requests.Session()
_session.headers["User-Agent"] = "Mozilla/5.0"

_resume_pdf: bytes | None = None


def _get_resume_pdf() -> bytes:
    global _resume_pdf
    if _resume_pdf is None:
        r = _session.get(RESUME_PDF_URL, timeout=15)
        r.raise_for_status()
        _resume_pdf = r.content
    return _resume_pdf


# ── Greenhouse ─────────────────────────────────────────────────────────────────

def _greenhouse_job_id(url: str) -> str | None:
    """Extract numeric job ID from greenhouse URL."""
    m = re.search(r"/jobs/(\d+)", url)
    return m.group(1) if m else None


def _greenhouse_get_questions(slug: str, job_id: str) -> list[dict]:
    r = _session.get(
        f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}",
        params={"questions": "true"},
        timeout=10,
    )
    if r.status_code != 200:
        return []
    return r.json().get("questions", [])


def apply_greenhouse(job: dict, analysis: dict) -> dict:
    """Submit via Greenhouse job board API. Returns {success, message, url}."""
    url = job.get("url", "")
    slug = job.get("_slug", "")
    job_id = _greenhouse_job_id(url)
    if not job_id:
        return {"success": False, "message": f"Could not parse job ID from URL: {url}"}

    # Fetch the application form questions
    questions = _greenhouse_get_questions(slug, job_id)

    # Build multipart form
    resume_bytes = _get_resume_pdf()
    files = {
        "resume": ("Nihal_Pothunoori_Robotics.pdf", io.BytesIO(resume_bytes), "application/pdf"),
    }
    if analysis.get("cover_letter"):
        cl_text = analysis["cover_letter"]
        files["cover_letter"] = ("cover_letter.txt", io.BytesIO(cl_text.encode()), "text/plain")

    data = {
        "first_name": PROFILE["first_name"],
        "last_name": PROFILE["last_name"],
        "email": PROFILE["email"],
        "phone": PROFILE["phone"],
        "job_id": job_id,
    }

    # Add mappable fields from questions
    for q in questions:
        field = q.get("fields", [{}])[0]
        name = field.get("name", "")
        label = q.get("label", "").lower()
        if "linkedin" in label:
            data[name] = PROFILE["linkedin"]
        elif "website" in label or "portfolio" in label:
            data[name] = PROFILE["portfolio"]
        elif "github" in label:
            data[name] = PROFILE["github"]
        elif "authorized" in label or "authorization" in label:
            data[name] = "Yes"
        elif "sponsor" in label:
            data[name] = "No"
        elif "relocate" in label:
            data[name] = "Yes"

    try:
        r = _session.post(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}/applications",
            data=data,
            files=files,
            timeout=20,
        )
        if r.status_code in (200, 201):
            return {"success": True, "message": "Applied via Greenhouse API", "url": url}
        else:
            return {
                "success": False,
                "message": f"Greenhouse API returned {r.status_code}: {r.text[:300]}",
            }
    except Exception as e:
        return {"success": False, "message": f"Greenhouse request failed: {e}"}


# ── Lever ──────────────────────────────────────────────────────────────────────

def _lever_posting_id(url: str) -> str | None:
    """Extract Lever posting UUID from URL."""
    m = re.search(r"/([0-9a-f]{8}-[0-9a-f-]{27,36})", url)
    return m.group(1) if m else None


def apply_lever(job: dict, analysis: dict) -> dict:
    """Submit via Lever job posting API. Returns {success, message, url}."""
    url = job.get("url", "")
    slug = job.get("_slug", "")
    posting_id = _lever_posting_id(url)
    if not posting_id:
        return {"success": False, "message": f"Could not parse posting ID from URL: {url}"}

    resume_bytes = _get_resume_pdf()
    files = {
        "resume": ("Nihal_Pothunoori_Robotics.pdf", io.BytesIO(resume_bytes), "application/pdf"),
    }
    if analysis.get("cover_letter"):
        files["comments"] = ("", io.BytesIO(analysis["cover_letter"].encode()), "text/plain")

    data = {
        "name": f"{PROFILE['first_name']} {PROFILE['last_name']}",
        "email": PROFILE["email"],
        "phone": PROFILE["phone"],
        "org": PROFILE["university"],
        "urls[LinkedIn]": PROFILE["linkedin"],
        "urls[Portfolio]": PROFILE["portfolio"],
        "urls[GitHub]": PROFILE["github"],
    }

    try:
        r = _session.post(
            f"https://api.lever.co/v0/postings/{slug}/{posting_id}/apply",
            data=data,
            files=files,
            timeout=20,
        )
        if r.status_code in (200, 201):
            return {"success": True, "message": "Applied via Lever API", "url": url}
        else:
            return {
                "success": False,
                "message": f"Lever API returned {r.status_code}: {r.text[:300]}",
            }
    except Exception as e:
        return {"success": False, "message": f"Lever request failed: {e}"}


# ── Router ─────────────────────────────────────────────────────────────────────

def apply(job: dict, analysis: dict) -> dict:
    ats = job.get("_ats", "")
    if ats == "greenhouse":
        return apply_greenhouse(job, analysis)
    elif ats == "lever":
        return apply_lever(job, analysis)
    else:
        return {
            "success": False,
            "message": f"Auto-apply not yet supported for ATS: {ats} — apply manually at {job.get('url')}",
        }

"""
Use Claude to score a job posting and generate tailored application materials.
"""
import json
import os
import anthropic
from personal_info import PROFILE, RESUME_TEXT

_client = None


def _claude():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = f"""You are an expert job application strategist helping {PROFILE['first_name']} {PROFILE['last_name']} apply for robotics/ML internships.

Here is their resume:
<resume>
{RESUME_TEXT}
</resume>

Profile:
- Student at {PROFILE['university']}, {PROFILE['degree']}, graduating {PROFILE['graduation']}
- {PROFILE['work_authorization']}
- Looking for: {PROFILE['target_start']} internships in robotics, ML, embodied AI, autonomous systems
- Current: Rivian ML Intern (world models / VLAs), DASLABS researcher (VLA + soft robotics)

Be honest and direct. Do not exaggerate or fabricate anything. Only use what is actually in the resume."""


def analyze_job(job: dict) -> dict:
    """
    Analyze a job posting. Returns:
      {
        "score": int (0-100),
        "verdict": "APPLY" | "SKIP",
        "strengths": [str, ...],
        "gaps": [str, ...],
        "positioning": str,
        "cover_letter": str,
        "answers": {question: answer, ...}
      }
    """
    title = job.get("title", "")
    company = job.get("company", "")
    description = job.get("description", "") or ""
    url = job.get("url", "")

    prompt = f"""Analyze this internship and decide whether to apply.

Job: {title} at {company}
URL: {url}
Description:
{description[:3000] if description else "(no description available — use job title and company to infer)"}

Respond with ONLY valid JSON in this exact format:
{{
  "score": <integer 0-100>,
  "verdict": "APPLY" or "SKIP",
  "strengths": ["<why this is a strong match>", ...],
  "gaps": ["<honest gap or missing qualification>", ...],
  "positioning": "<1-2 sentences on how to position Nihal for this role>",
  "cover_letter": "<150-250 word cover letter in Nihal's direct, casual-but-sharp voice. Start with why the role, not 'I am excited'. No fluff.>",
  "notes": "<any special instructions for filling the application>"
}}

Score rubric:
90-100: Near-perfect match (VLA, world models, embodied AI, ROS2, exact tech stack match)
75-89: Strong match (robotics software, ML, relevant tech)
60-74: Decent match (adjacent ML/robotics role, some relevant skills)
< 60: Weak match (skip)

Apply if score >= 70."""

    response = _claude().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {
            "score": 0,
            "verdict": "SKIP",
            "strengths": [],
            "gaps": ["Failed to parse Claude response"],
            "positioning": "",
            "cover_letter": "",
            "notes": text[:200],
        }

    result.setdefault("score", 0)
    result.setdefault("verdict", "SKIP" if result["score"] < 70 else "APPLY")
    result.setdefault("cover_letter", "")
    result.setdefault("strengths", [])
    result.setdefault("gaps", [])
    result.setdefault("positioning", "")
    result.setdefault("notes", "")
    result.setdefault("answers", {})
    return result

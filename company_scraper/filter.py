import re

# Must have "intern" or "internship" in the title
_INTERN_RE = re.compile(r"\b(intern|internship)\b", re.I)

# Must have at least one technical keyword in title or description
_TECH_RE = re.compile(
    r"\b(robot|robotics|ros|software|machine learning|ml|ai|autonomous|"
    r"perception|reinforcement learning|computer vision|embedded|controls|"
    r"simulation|slam|manipulation|locomotion|vla|world model)\b",
    re.I,
)

# Hard exclude — never want these even as intern roles
_EXCLUDE_RE = re.compile(
    r"\b(recruiter|recruiting|sales|marketing|finance|accounting|legal|\bhr\b|"
    r"counsel|operations manager|program manager|technician trainee|"
    r"service technician|safety intern|construction)\b",
    re.I,
)


def is_relevant(title: str, description: str = "") -> bool:
    if not _INTERN_RE.search(title):
        return False
    if _EXCLUDE_RE.search(title):
        return False
    # Tech keyword must appear in the title — description is too noisy since
    # any job at a robotics company will mention robots in the description.
    return bool(_TECH_RE.search(title))

import re

# Must match at least one of these in title or description to be relevant
KEYWORDS = [
    # Core robotics
    "robot", "robotics", "ros", "embodied", "manipulation", "locomotion",
    # ML/RL for robotics
    "reinforcement learning", "robot learning", "vla", "world model",
    "imitation learning", "behavior cloning", "diffusion policy",
    # Perception / sensing
    "perception", "slam", "lidar", "point cloud", "sensor fusion",
    "motion planning", "computer vision", "autonomous",
    # Roles
    "software engineer", "ml engineer", "machine learning engineer",
    "research engineer", "research scientist", "ai engineer",
    "embedded", "controls", "simulation",
    # Intern
    "intern", "internship",
]

EXCLUDE_TITLE = re.compile(
    r"\b(manager|director|\bvp\b|president|recruiter|sales|"
    r"marketing|accountant|finance|\blegal\b|\bhr\b|counsel)\b",
    re.I,
)

_kw_re = re.compile("|".join(re.escape(k) for k in KEYWORDS), re.I)


def is_relevant(title: str, description: str = "") -> bool:
    if EXCLUDE_TITLE.search(title):
        return False
    return bool(_kw_re.search(f"{title} {description}"))

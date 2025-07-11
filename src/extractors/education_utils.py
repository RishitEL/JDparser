from typing import Dict, Any
from config.weight_loader import get_config

_DEGREE_KEYWORDS = {
    "phd": ["phd", "doctor of philosophy"],
    "masters": ["master", "m.s", "m.sc", "mtech", "ms"],
    "bachelors": ["bachelor", "b.s", "b.sc", "btech", "bs"],
    "diploma": ["diploma"],
}


def _detect_level(text: str) -> str:
    text_l = text.lower()
    for level, kws in _DEGREE_KEYWORDS.items():
        if any(k in text_l for k in kws):
            return level
    return "none"


def highest_degree(resume: Dict[str, Any]) -> str:
    levels = ["none"]
    for edu in resume.get("educations", []):
        degree = edu.get("degree", "")
        if degree:
            levels.append(_detect_level(degree))
    # choose highest by hierarchy
    hierarchy = get_config()["education_hierarchy"]
    levels.sort(key=lambda l: hierarchy.get(l, 0), reverse=True)
    return levels[0]


def required_degree(jd: Dict[str, Any]) -> str:
    # explicit structured field could be added; else search keywords
    # simple heuristic: if "master" appears in JD bullets/skills we require masters
    all_text = " ".join(str(v) for v in jd.values())
    return _detect_level(all_text)


def meets_degree_requirement(resume_level: str, jd_level: str) -> bool:
    hierarchy = get_config()["education_hierarchy"]
    return hierarchy.get(resume_level, 0) >= hierarchy.get(jd_level, 0) 
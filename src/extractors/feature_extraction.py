import re
from typing import Dict, List, Any
import json

__all__ = [
    "jd_to_embed_payload",
    "resume_to_embed_payload",
]

_percent_re = re.compile(r"\d+%?")


def _clean_text(text: str) -> str:
    """Basic cleanup: strip, de-percent, normalise spaces."""
    if not text:
        return ""
    # remove leading/trailing whitespace and redundant spaces
    text = text.strip()
    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text


def _clean_skill(skill: str) -> str:
    """Remove proficiency percents like 'Java 90%'."""
    skill = _percent_re.sub("", skill)
    return _clean_text(skill)


def jd_to_embed_payload(jd: Dict[str, Any]) -> Dict[str, List[str]]:
    """Convert parsed JD JSON to lists of strings to embed.

    Returns dict with keys:
        skill_texts: list[str]
        bullet_texts: list[str]
    """
    skill_texts: List[str] = []

    tech_skills = jd.get("technical_skills", {})
    skill_texts.extend(tech_skills.get("primary_skills", []))
    skill_texts.extend(tech_skills.get("secondary_skills", []))

    # ensure cleaning and de-duplication
    skill_texts = list({ _clean_skill(s).lower() for s in skill_texts if s })

    bullet_texts: List[str] = jd.get("key_responsibilities", [])
    bullet_texts = [_clean_text(b) for b in bullet_texts if b]

    return {
        "skill_texts": skill_texts,
        "bullet_texts": bullet_texts,
    }


def resume_to_embed_payload(resume: Dict[str, Any]) -> Dict[str, List[str]]:
    """Convert parsed resume JSON to lists of strings to embed.

    Returns dict with keys:
        skill_texts, exp_bullets, proj_bullets, summary_text
    """
    skills = resume.get("skills", {})
    skill_texts: List[str] = []
    for key in ("technical", "other"):
        skill_texts.extend(skills.get(key, []))
    skill_texts = list({ _clean_skill(s).lower() for s in skill_texts if s })
    # print(skill_texts)

    # extract bullets from experiences
    exp_bullets: List[str] = []
    for exp in resume.get("workExperiences", []):
        exp_bullets.extend(exp.get("descriptions", []))
    exp_bullets = [_clean_text(b) for b in exp_bullets if b]
    # print(exp_bullets)

    # project bullets
    proj_bullets: List[str] = []
    for proj in resume.get("projects", []):
        proj_bullets.extend(proj.get("descriptions", []))
    proj_bullets = [_clean_text(b) for b in proj_bullets if b]
    # print(proj_bullets)

    summary_texts: List[str] = []
    profile = resume.get("profile", {})
    if profile.get("summary"):
        summary_texts.append(_clean_text(profile["summary"]))
    # print(summary_texts)

    return {
        "skill_texts": skill_texts,
        "exp_bullets": exp_bullets,
        "proj_bullets": proj_bullets,
        "summary_texts": summary_texts,
    } 

# Read json from final_respose_Rishit resume.json
# with open('resumes_json/final_response_Rishit resume.pdf.json', 'r') as file:
#     resume = json.load(file)
# print(resume)
# resume_to_embed_payload(resume)
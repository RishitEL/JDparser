from __future__ import annotations

import re
from datetime import datetime
from dateutil import parser as dt_parser
from typing import Dict, Any, Optional

_MONTH_MAP = {m.lower(): i for i, m in enumerate([
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"] , 1)}

_DURATION_RE = re.compile(r"(\d+)\s*\+?\s*(?:years|yrs|year)", re.I)


# ------------------------------------------------------------
# Resume side helpers
# ------------------------------------------------------------


def _parse_date(text: str) -> Optional[datetime]:
    """Parse a date string like 'April 2025' into a datetime."""
    text = text.strip()
    if not text or text.lower() in {"present", "current"}:
        return datetime.now()
    try:
        return dt_parser.parse(text, default=datetime(1900, 1, 1))
    except (ValueError, OverflowError):
        return None


def estimate_years_experience(resume: Dict[str, Any]) -> float:
    """Approximate total professional years from workExperiences date ranges."""
    total_months = 0
    for exp in resume.get("workExperiences", []):
        date_range = exp.get("date", "")
        if not date_range:
            continue
        parts = [p.strip() for p in date_range.split("-")]
        if len(parts) != 2:
            continue
        start = _parse_date(parts[0])
        end = _parse_date(parts[1])
        if start and end and end >= start:
            months = (end.year - start.year) * 12 + (end.month - start.month)
            total_months += max(0, months)
    return round(total_months / 12.0, 1)

# ------------------------------------------------------------
# JD side helpers
# ------------------------------------------------------------

def parse_required_years(jd: Dict[str, Any]) -> int:
    """Return integer years required from JD if stated, else 0."""
    # Try structured field first
    exp_field = jd.get("basic_info", {}).get("experience_required") or jd.get("experience_requirements", {}).get("total_years", "")
    if exp_field:
        match = _DURATION_RE.search(str(exp_field))
        if match:
            return int(match.group(1))
    # fallback: search any nested string values
    def _find(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                y = _find(v)
                if y:
                    return y
        elif isinstance(obj, list):
            for v in obj:
                y = _find(v)
                if y:
                    return y
        elif isinstance(obj, str):
            m = _DURATION_RE.search(obj)
            if m:
                return int(m.group(1))
        return None
    res = _find(jd)
    return res or 0 
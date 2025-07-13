from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------
# Resume side helpers
# ------------------------------------------------------------


def estimate_years_experience(resume: Dict[str, Any]) -> float:
    """Calculate total professional years from work experiences using LLM with fallback."""
    # Extract date strings from work experiences -------------------------
    work_experiences = resume.get("workExperiences", [])
    if not work_experiences:
        return 0.0

    date_ranges: list[str] = [exp.get("date", "") for exp in work_experiences if exp.get("date")]
    if not date_ranges:
        return 0.0

    # Current date for the LLM to interpret keywords like "present"
    today_str = datetime.now().strftime("%B %Y")  # e.g., "July 2025"

    # -------------------------------- Prompt ---------------------------------
    system_prompt = (
        "You are a senior HR analytics assistant."
    )

    user_prompt = (
        "Calculate the candidate's TOTAL YEARS OF PROFESSIONAL EXPERIENCE from the date ranges provided.\n"
        "Rules:\n"
        "1. Handle overlapping periods (count once).\n"
        "2. If an end date is 'present', 'till date', 'current', etc., use today's date ({today_str}).\n"
        "3. Count internships and part-time at 0.5 weight.\n"
        "4. Return ONLY a JSON object of the form {{\n    \"total_years_experience\": <decimal up to two decimals>\n}} with no extra keys or text.\n"
        "5. Round to two decimals.\n\n"
        "Date ranges (JSON list):\n" + json.dumps(date_ranges, indent=2)
    )

    # Try querying the LLM and parsing output
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        raw_text = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw_text)
            years = float(data.get("total_years_experience"))
            return round(years, 2)
        except (ValueError, json.JSONDecodeError, TypeError):
            # If the model returns something unexpected, treat as failure
            print("⚠️ Unable to parse valid JSON from LLM response for experience calculation.")
            return 0.0
    except Exception as e:
        print(f"⚠️ Error calculating experience via LLM: {e}")
        return 0.0  # on failure, return 0.0

# ------------------------------------------------------------
# JD side helpers
# ------------------------------------------------------------

def parse_required_years(jd: Dict[str, Any]) -> int:
    """Return integer years required from JD if stated, else 0."""
    # Try structured field first
    exp_field = jd.get("basic_info", {}).get("experience_required") or jd.get("experience_requirements", {}).get("total_years", "")
    if exp_field:
        match = re.search(r"(\d+)\s*\+?\s*(?:years|yrs|year)", str(exp_field), re.I)
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
            m = re.search(r"(\d+)\s*\+?\s*(?:years|yrs|year)", obj, re.I)
            if m:
                return int(m.group(1))
        return None
    res = _find(jd)
    return res or 0 
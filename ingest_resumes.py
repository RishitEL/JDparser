"""Script to load parsed resumes into vector database."""

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from src.matchers.matcher import ResumeJDMatcher
from src.utils.db_utils import VectorDB
from src.extractors.experience_utils import estimate_years_experience


def process_resume(matcher: ResumeJDMatcher, resume: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and compute vectors for a resume."""
    # Calculate total years of experience
    
    # Extract vectors and other features
    return matcher._vectorize_resume(resume)


def main():
    parser = argparse.ArgumentParser(description="Load resumes into vector DB")
    parser.add_argument(
        "--resume_dir",
        type=str,
        required=True,
        help="Directory containing parsed resume JSONs"
    )
    args = parser.parse_args()

    # Initialize matcher and DB
    matcher = ResumeJDMatcher()
    db = VectorDB()

    # Process each resume JSON in directory
    resume_dir = Path(args.resume_dir)
    for file in resume_dir.glob("*.json"):
        print(f"Processing {file.name}...")
        
        # Load and unwrap resume data
        with open(file) as f:
            data = json.load(f)
            resume = data.get("parsed_data", data)
        
        # Extract vectors and add years_experience to metadata
        features = process_resume(matcher, resume)
        
        # Adding the years_experience to the resume metadata
        resume["years_experience"] = features["years_experience"]
        print("Printing years of experience", resume["years_experience"])
        # Store in database
        db.store_resume(
            filename=file.name,
            meta=resume,  # Now includes years_experience
            skill_vec=features["skill_vec"],
            exp_vec=features["exp_vec"],
            skill_texts=resume.get("skills", {}).get("technical", []),
            skill_vecs=features["skill_vecs"],
        )
        print(f"Stored {file.name}")

    db.close()
    print("Done!")


if __name__ == "__main__":
    main() 
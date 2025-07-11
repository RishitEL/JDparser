import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()


class JDParser:
    def __init__(self):
        # Configure Google Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        # Initialize the model with higher quota limit
        self.model = genai.GenerativeModel('gemini-1.5-flash-8b')

    def parse_jd(self, jd_text):
        """
        Parse job description text and extract key information
        """
        prompt = """You are an expert at parsing job descriptions. 
        Extract the following information in JSON format from the job description:
        {
            "basic_info": {
                "job_role": "",
                "location": "",
                "employment_type": "",
                "experience_required": "",
                "work_mode": ""
            },
            "technical_skills": {
                "primary_skills": [],
                "secondary_skills": [],
                "skill_proficiency": {
                    "skill_name": "percentage/level"
                }
            },
            "key_responsibilities": [],
            "experience_requirements": {
                "total_years": "",
                "technology_specific_experience": {}
            }
        }
        
        Return ONLY the JSON object without any additional text or explanation.
        Make sure the output is a valid JSON.
        If any field is not found in the job description, keep it empty or as an empty list.
        
        Job Description to parse:
        """

        try:
            response = self.model.generate_content(prompt + "\n" + jd_text)
            # Clean the response to ensure it's valid JSON
            json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(json_str)
            return parsed_data
        
        except Exception as e:
            print(f"Error parsing JD: {str(e)}")
            return None

def main():
    # Example usage
    parser = JDParser()
    
    
    # Read JD from file pass_jd.txt
    with open('pass_jd.txt', 'r') as file:
        sample_jd = file.read()
    
    result = parser.parse_jd(sample_jd)
    if result:
        print(json.dumps(result, indent=2))
        # save the result to a file
        with open('parsed_jd.json', 'w') as file:
            json.dump(result, file, indent=2)

if __name__ == "__main__":
    main() 
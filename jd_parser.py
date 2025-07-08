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
            "technology_stack": {
                "frontend": [],
                "backend": [],
                "mobile": [],
                "cloud": [],
                "testing": [],
                "tools": []
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
    
    # Example JD text
    sample_jd = """
    Job Role: IOS Engineer
    Job Locations: Remote
    Required Experience: 3 - 6 Years
    Skills: iOS, React Native
    \
    Share
    What will they do?
    Rapidly design, prototype, and build innovative features using iOS technologies with a focus on AR, 3D, and camera-first experiences.
    Leverage native iOS frameworks like ARKit, RealityKit, SceneKit, and Metal to create engaging and realistic immersive interactions.
    Build high-quality, reusable, and performant UI components using both SwiftUI and UIKit.
    Ensure optimal performance and responsiveness across the entire range of supported Apple devices.
    Collaborate in an agile, cross-functional team of product managers, designers, and other engineers to deliver features at a fast pace.
    Take full ownership of your work, from initial concept and technical design to testing, release, and maintenance.
    Essential Skills
    Deep expertise in  React Native, Swift and a strong understanding of the iOS SDK.
    Proven experience with modern iOS architecture patterns (e.g., MVVM) and frameworks (SwiftUI, UIKit).
    Hands-on experience or a strong passion for learning Apple's AR/3D frameworks (ARKit, RealityKit, SceneKit).
    A strong understanding of concurrency (GCD, Swift Concurrency) and memory management in iOS.
    Excellent debugging skills and proficiency with iOS performance and debugging tools like Instruments.
    A keen eye for detail and a passion for crafting fluid animations and exceptional user experiences.
    Ability to quickly learn new technologies and apply them to build functional and robust prototypes.
    """
    
    result = parser.parse_jd(sample_jd)
    if result:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 
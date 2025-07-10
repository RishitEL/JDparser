import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class JDParserFrontend:
    def __init__(self):
        # Configure Google Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash-8b')

    def parse_jd_for_frontend(self, jd_text):
        """
        Parse job description text and extract information in a frontend-friendly format
        """
        prompt = """You are an expert at analyzing and restructuring job descriptions for frontend display.
        Your task is to deeply understand the job description and reformulate the information in a clear, structured format.
        Don't just extract exact phrases - analyze the content, understand the context, and present it in a well-organized way.

        CRITICAL REQUIREMENTS:
        1. You MUST provide content for these key sections (they are required):
           - Description: A clear, concise summary of the role and its context
           - Responsibilities: A structured list of key duties, reformulated for clarity
           - Who You Are: Essential qualifications and traits, presented as clear requirements
           - Nice-to-Haves: Additional beneficial qualifications, even if not explicitly labeled as such in the JD

        2. For each section:
           - Description: Synthesize the overall role purpose and context into a coherent paragraph
           - Responsibilities: Convert duties into clear, action-oriented statements
           - Who You Are: Transform requirements into positive statements about the ideal candidate
           - Nice-to-Haves: Identify and rephrase preferred qualifications as opportunities

        Extract and format the information in this JSON structure:
        {
            "about_this_role": {
                "applied_before": "",
                "job_posted_on": "",
                "job_type": "",
                "salary_range": ""
            },
            "description": "REQUIRED - Provide a clear, engaging summary",
            "responsibilities": [
                "REQUIRED - List key duties as clear, action-oriented statements",
                "Each responsibility should be concrete and specific",
                "Rephrase for clarity while maintaining meaning"
            ],
            "who_you_are": [
                "REQUIRED - List essential qualifications and traits",
                "Focus on both technical skills and soft skills",
                "Rephrase requirements as positive attributes"
            ],
            "nice_to_haves": [
                "REQUIRED - List preferred qualifications",
                "Include implicit preferences from the JD",
                "Frame as growth opportunities"
            ],
            "categories": [
                "Identify relevant job categories",
                "Examples: Engineering, Marketing, Design, etc."
            ],
            "required_skills": [
                "Extract specific technical or professional skills",
                "List as individual items"
            ]
        }
        
        FORMATTING GUIDELINES:
        - Return ONLY the JSON object without any additional text
        - Ensure the output is valid JSON
        - Format dates as MM/DD/YYYY
        - Format salary ranges as "$XXk-$YYk USD" if available
        - Keep fields empty or as empty lists if truly not inferrable from the JD
        - Each list item should be a complete, well-formed statement
        
        Job Description to parse:
        """

        try:
            response = self.model.generate_content(prompt + "\n" + jd_text)
            # Clean the response to ensure it's valid JSON
            json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(json_str)
            
            # Add current date as job posted date if not provided
            if not parsed_data["about_this_role"]["job_posted_on"]:
                parsed_data["about_this_role"]["job_posted_on"] = datetime.now().strftime("%m/%d/%Y")
            
            # Validate required fields are not empty
            required_fields = ["description", "responsibilities", "who_you_are", "nice_to_haves"]
            for field in required_fields:
                if not parsed_data.get(field) or (isinstance(parsed_data[field], list) and not parsed_data[field]):
                    raise ValueError(f"Required field '{field}' is empty")
            
            return parsed_data
        
        except Exception as e:
            print(f"Error parsing JD for frontend: {str(e)}")
            return None

def main():
    # Example usage
    parser = JDParserFrontend()
    
    # Read JD from file
    with open('pass_jd.txt', 'r') as file:
        sample_jd = file.read()
    
    result = parser.parse_jd_for_frontend(sample_jd)
    if result:
        # Save to a new JSON file for frontend use
        with open('frontend_jd.json', 'w') as outfile:
            json.dump(result, outfile, indent=2)
        print("Parsed JD saved to frontend_jd.json")
        print("\nParsed content:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 
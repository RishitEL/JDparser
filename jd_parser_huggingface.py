import json
import re
from typing import Dict, List, Any

class JDParserLocal:
    """
    A local JD parser that doesn't require API calls
    Uses rule-based extraction for job description parsing
    """
    
    def __init__(self):
        self.skill_patterns = {
            'frontend': ['angular', 'react', 'vue', 'javascript', 'typescript', 'html', 'css', 'bootstrap', 'rxjs', 'ngrx', 'swiftui', 'uikit'],
            'backend': ['java', 'spring', 'node', 'python', 'django', 'flask', 'php', 'laravel', 'microservices', 'spring boot'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'swift', 'kotlin', 'arkit', 'realitykit', 'scenekit', 'metal'],
            'cloud': ['aws', 'gcp', 'azure', 'kubernetes', 'docker'],
            'database': ['mysql', 'postgresql', 'mongodb', 'redis'],
            'testing': ['junit', 'selenium', 'jasmine', 'karma', 'cypress', 'jest'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'instruments']
        }
    
    def extract_skills_with_proficiency(self, text: str) -> Dict[str, str]:
        """Extract skills with their proficiency levels"""
        skills = {}
        
        # Pattern to match "Skill - percentage%"
        pattern = r'([A-Za-z\s\.\+\-\(\)]+?)\s*[-–]\s*(\d+)%'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for skill, proficiency in matches:
            skill = skill.strip()
            skills[skill] = f"{proficiency}%"
        
        return skills
    
    def categorize_skills(self, text: str) -> Dict[str, List[str]]:
        """Categorize skills into technology stack"""
        categorized = {
            'frontend': [],
            'backend': [],
            'mobile': [],
            'cloud': [],
            'testing': [],
            'tools': []
        }
        
        text_lower = text.lower()
        
        for category, skill_list in self.skill_patterns.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    categorized[category].append(skill.title())
        
        return categorized
    
    def extract_primary_secondary_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract primary and secondary skills"""
        primary_skills = []
        secondary_skills = []
        
        lines = text.split('\n')
        in_primary = False
        in_secondary = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'primary skill' in line.lower():
                in_primary = True
                in_secondary = False
                continue
            elif 'secondary skill' in line.lower():
                in_secondary = True
                in_primary = False
                continue
            elif 'essential skill' in line.lower():
                in_primary = True
                in_secondary = False
                continue
            
            # Extract skills from lines
            if in_primary and ('-' in line or any(cat in line.lower() for cat_list in self.skill_patterns.values() for cat in cat_list)):
                skill = re.sub(r'\s*[-–]\s*\d+%', '', line).strip()
                if skill and len(skill.split()) <= 4:
                    primary_skills.append(skill)
            elif in_secondary and ('-' in line or any(cat in line.lower() for cat_list in self.skill_patterns.values() for cat in cat_list)):
                skill = re.sub(r'\s*[-–]\s*\d+%', '', line).strip()
                if skill and len(skill.split()) <= 4:
                    secondary_skills.append(skill)
        
        return {"primary_skills": primary_skills, "secondary_skills": secondary_skills}
    
    def extract_experience(self, text: str) -> str:
        """Extract experience requirements"""
        patterns = [
            r'(\d+[\+\-]?\s*(?:to\s+\d+)?\s*years?)',
            r'(\d+[\+\-]?\s*yrs?)',
            r'experience[:\s]*(\d+[\+\-]?\s*(?:to\s+\d+)?\s*years?)',
            r'(\d+\s*[\+\-]\s*years?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return ""
    
    def extract_technology_specific_experience(self, text: str) -> Dict[str, str]:
        """Extract technology-specific experience requirements"""
        tech_exp = {}
        
        # Pattern to match "X years of experience in Technology"
        pattern = r'(\d+[\+\-]?)\s*years?\s*(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+|working\s+)?([A-Za-z\s\.\+\-\(\)]+?)(?:\s*,|\s*\(|\s*$|\s*and)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for years, tech in matches:
            tech = tech.strip()
            if len(tech.split()) <= 3:  # Avoid long phrases
                tech_exp[tech] = f"{years} years"
        
        return tech_exp
    
    def extract_job_title(self, text: str) -> str:
        """Extract job title"""
        patterns = [
            r'job\s+role[:\s]*([^\n]+)',
            r'position[:\s]*([^\n]+)',
            r'title[:\s]*([^\n]+)',
            r'need\s+([^-\n]+)',
            r'^([A-Za-z\s]+(?:developer|engineer|analyst|manager))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                return matches[0].strip()
        
        return ""
    
    def extract_location(self, text: str) -> str:
        """Extract job location"""
        patterns = [
            r'location[s]?[:\s]*([^\n]+)',
            r'for\s+([A-Za-z\s]+)(?:\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                if not any(mode in location.lower() for mode in ['remote', 'hybrid', 'onsite']):
                    return location
        
        return ""
    
    def extract_work_mode(self, text: str) -> str:
        """Extract work mode (remote/hybrid/onsite)"""
        modes = ['remote', 'hybrid', 'onsite', 'on-site', 'work from home', 'wfh']
        
        for mode in modes:
            if mode.lower() in text.lower():
                return mode.capitalize()
        
        return ""
    
    def extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []
        
        # Look for sections that might contain responsibilities
        resp_indicators = ['what will they do', 'responsibilities', 'duties', 'role', 'you will']
        
        lines = text.split('\n')
        in_resp_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we're entering a responsibilities section
            if any(indicator in line.lower() for indicator in resp_indicators):
                in_resp_section = True
                continue
            
            # Check if we're leaving the section
            if in_resp_section and any(keyword in line.lower() for keyword in ['skills', 'requirements', 'experience', 'qualifications']):
                in_resp_section = False
                continue
            
            # Extract responsibilities
            if in_resp_section and (line.startswith('-') or line.startswith('•') or 
                                  line.startswith('*') or len(line.split()) > 5):
                responsibilities.append(line.lstrip('-•* '))
        
        return responsibilities
    
    def parse_jd(self, jd_text: str) -> Dict[str, Any]:
        """
        Parse job description text and extract key information in the new format
        """
        try:
            # Extract skills
            skills_data = self.extract_primary_secondary_skills(jd_text)
            skill_proficiency = self.extract_skills_with_proficiency(jd_text)
            technology_stack = self.categorize_skills(jd_text)
            
            result = {
                "basic_info": {
                    "job_role": self.extract_job_title(jd_text),
                    "location": self.extract_location(jd_text),
                    "employment_type": "Contract" if "contract" in jd_text.lower() else "",
                    "experience_required": self.extract_experience(jd_text),
                    "work_mode": self.extract_work_mode(jd_text)
                },
                "technical_skills": {
                    "primary_skills": skills_data["primary_skills"],
                    "secondary_skills": skills_data["secondary_skills"],
                    "skill_proficiency": skill_proficiency
                },
                "technology_stack": technology_stack,
                "key_responsibilities": self.extract_responsibilities(jd_text),
                "experience_requirements": {
                    "total_years": self.extract_experience(jd_text),
                    "technology_specific_experience": self.extract_technology_specific_experience(jd_text)
                }
            }
            
            return result
        
        except Exception as e:
            print(f"Error parsing JD: {str(e)}")
            return None

def main():
    # Example usage
    parser = JDParserLocal()
    
    # Example JD text
    sample_jd = """
    Job Role: IOS Engineer
    Job Locations: Remote
    Required Experience: 3 - 6 Years
    Skills: iOS, React Native
    
    What will they do?
    Rapidly design, prototype, and build innovative features using iOS technologies with a focus on AR, 3D, and camera-first experiences.
    Leverage native iOS frameworks like ARKit, RealityKit, SceneKit, and Metal to create engaging and realistic immersive interactions.
    Build high-quality, reusable, and performant UI components using both SwiftUI and UIKit.
    Ensure optimal performance and responsiveness across the entire range of supported Apple devices.
    Collaborate in an agile, cross-functional team of product managers, designers, and other engineers to deliver features at a fast pace.
    Take full ownership of your work, from initial concept and technical design to testing, release, and maintenance.
    
    Essential Skills
    Deep expertise in React Native, Swift and a strong understanding of the iOS SDK.
    Proven experience with modern iOS architecture patterns (e.g., MVVM) and frameworks (SwiftUI, UIKit).
    Hands-on experience or a strong passion for learning Apple's AR/3D frameworks (ARKit, RealityKit, SceneKit).
    A strong understanding of concurrency (GCD, Swift Concurrency) and memory management in iOS.
    Excellent debugging skills and proficiency with iOS performance and debugging tools like Instruments.
    A keen eye for detail and a passion for crafting fluid animations and exceptional user experiences.
    Ability to quickly learn new technologies and apply them to build functional and robust prototypes.
    """
    
    result = parser.parse_jd(sample_jd)
    if result:
        print("=== LOCAL PARSER RESULT ===")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 
import re
import io
import pdfplumber
import docx2txt
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

class SingleResumeAnalyzer:
    def __init__(self, skill_keywords=None):
        if skill_keywords is None:
            self.skill_keywords = {
                'Technical': {'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                              'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes',
                              'aws', 'azure', 'gcp', 'linux', 'git', 'html', 'css', 'react', 'angular',
                              'vue', 'node.js', 'django', 'flask', 'spring', 'tensorflow', 'pytorch',
                              'machine learning', 'data science', 'api', 'rest', 'graphql'},
                'Soft': {'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
                         'time management', 'adaptability', 'creativity', 'empathy', 'collaboration',
                         'project management', 'agile', 'scrum', 'presentation', 'negotiation'},
                'Business': {'marketing', 'sales', 'finance', 'accounting', 'strategy', 'analytics',
                             'business development', 'customer service', 'operations', 'supply chain',
                             'e-commerce', 'crm', 'erp', 'budgeting', 'forecasting'},
                'Industry': {'healthcare', 'banking', 'retail', 'manufacturing', 'education', 'consulting',
                             'automotive', 'aviation', 'construction', 'energy', 'telecom', 'media'},
            }
        else:
            self.skill_keywords = skill_keywords
            
        self.action_verbs = {
            'achieved', 'improved', 'trained', 'mentored', 'managed', 'created', 'resolved', 'volunteered',
            'influenced', 'increased', 'decreased', 'negotiated', 'launched', 'generated', 'developed',
            'led', 'designed', 'built', 'implemented', 'optimized', 'spearheaded', 'orchestrated'
        }
        
        # Pre-compile patterns
        self.compiled_skills = {}
        for category, keywords in self.skill_keywords.items():
            self.compiled_skills[category] = {}
            for kw in keywords:
                self.compiled_skills[category][kw] = re.compile(r'(?<![a-z0-9])' + re.escape(kw) + r'(?![a-z0-9])')
                
        self.compiled_action_verbs = {verb: re.compile(r'(?<![a-z0-9])' + re.escape(verb) + r'(?![a-z0-9])') for verb in self.action_verbs}
        
    def extract_text(self, file_bytes, file_name):
        """Extract text from PDF or DOCX file bytes."""
        text = ""
        try:
            if file_name.lower().endswith('.pdf'):
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            elif file_name.lower().endswith('.docx'):
                text = docx2txt.process(io.BytesIO(file_bytes))
        except Exception as e:
            text = f"Error extracting text: {e}"
        return text

    def preprocess_text(self, text):
        text = text.lower()
        # Keep letters, numbers, and basic punctuation for formatting checks
        return text

    def clean_text_for_skills(self, text):
        return re.sub(r'\s+', ' ', text.lower()).strip()

    def analyze(self, raw_text):
        """
        Analyze the raw text and return a dictionary with score, skills, suggestions, etc.
        """
        if not raw_text or raw_text.startswith("Error"):
            return None
            
        clean_text = self.clean_text_for_skills(raw_text)
        words = clean_text.split()
        word_count = len(words)
        
        # 1. Skill Extraction
        extracted_skills = {'Technical': [], 'Soft': [], 'Business': [], 'Industry': []}
        all_skills_flat = []
        for category, keywords in self.skill_keywords.items():
            for kw in keywords:
                if self.compiled_skills[category][kw].search(clean_text):
                    extracted_skills[category].append(kw)
                    all_skills_flat.append(kw)
                    
        # 2. Action Verbs Check
        found_action_verbs = [verb for verb in self.action_verbs if self.compiled_action_verbs[verb].search(clean_text)]
        
        # 3. Formatting Check (Heuristics)
        has_education = bool(re.search(r'\b(education|university|college|bachelor|master|phd|degree)\b', raw_text.lower()))
        has_experience = bool(re.search(r'\b(experience|work history|employment|career)\b', raw_text.lower()))
        has_skills_section = bool(re.search(r'\b(skills|technologies|tools)\b', raw_text.lower()))
        
        # 4. Scoring Algorithm
        score = 0
        suggestions = []
        
        # Word count score (Max 20)
        if 200 <= word_count <= 800:
            score += 20
        elif word_count < 200:
            score += 10
            suggestions.append("Your resume seems a bit short. Try expanding on your experience with detailed bullet points.")
        else:
            score += 10
            suggestions.append("Your resume might be too long. Consider condensing it to highlight only the most relevant achievements.")
            
        # Skills score (Max 40)
        total_skills_found = len(all_skills_flat)
        if total_skills_found >= 15:
            score += 40
        elif total_skills_found >= 8:
            score += 30
            suggestions.append("You have a good number of skills, but adding a few more industry-specific keywords could improve your ATS ranking.")
        else:
            score += 15
            suggestions.append("Few skills were detected. Make sure to clearly list your technical and soft skills to pass ATS filters.")
            
        # Action Verbs score (Max 20)
        if len(found_action_verbs) >= 5:
            score += 20
        elif len(found_action_verbs) >= 2:
            score += 10
            suggestions.append("You have some action verbs, but using more strong verbs (e.g., 'spearheaded', 'orchestrated') can make your impact clearer.")
        else:
            score += 5
            suggestions.append("Try starting your bullet points with action verbs like 'Developed', 'Managed', or 'Implemented'.")
            
        # Formatting score (Max 20)
        format_score = 0
        if has_education: format_score += 7
        else: suggestions.append("Consider adding a clear 'Education' section.")
        
        if has_experience: format_score += 7
        else: suggestions.append("Ensure you have a distinct 'Experience' or 'Work History' section.")
        
        if has_skills_section: format_score += 6
        else: suggestions.append("A dedicated 'Skills' section makes it much easier for recruiters and ATS to parse your capabilities.")
        
        score += format_score
        
        return {
            'overall_score': score,
            'word_count': word_count,
            'skills_extracted': extracted_skills,
            'total_skills_count': total_skills_found,
            'action_verbs_found': found_action_verbs,
            'suggestions': suggestions,
            'has_sections': {
                'education': has_education,
                'experience': has_experience,
                'skills': has_skills_section
            }
        }

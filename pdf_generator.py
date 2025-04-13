import os
import tempfile
from fpdf import FPDF
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class ResumePDF(FPDF):
    """Custom PDF class for generating improved resumes"""
    
    def header(self):
        """Add header to the PDF"""
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Improved Resume', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """Add footer to the PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def chapter_title(self, title):
        """Add a chapter title"""
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)
        
    def chapter_body(self, body):
        """Add chapter content"""
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, body)
        self.ln(5)

def generate_improved_resume(original_resume_text, improvement_suggestions):
    """
    Generate an improved version of the resume based on AI suggestions.
    
    Args:
        original_resume_text (str): Original resume text
        improvement_suggestions (list): List of improvement suggestions from AI analysis
        
    Returns:
        str: Path to the generated PDF file
    """
    # Create a prompt for Gemini API to rewrite the resume
    prompt = f"""
    You are an expert resume writer. Rewrite the following resume by implementing these specific improvements:
    
    ORIGINAL RESUME:
    {original_resume_text}
    
    IMPROVEMENTS TO IMPLEMENT:
    {improvement_suggestions}
    
    Please rewrite the entire resume with these improvements while maintaining the same core information.
    Structure the resume in standard sections: Contact Information, Summary, Experience, Education, Skills.
    Use bullet points for accomplishments and make them quantifiable where possible.
    Focus on clarity, conciseness, and professional formatting.
    Return ONLY the improved resume text with section headers, no additional explanations.
    """
    
    # Generate improved resume content using Gemini API - UPDATED MODEL NAME
    model = genai.GenerativeModel('gemini-1.5-pro')  # Updated from 'gemini-pro' to 'gemini-1.5-pro'
    response = model.generate_content(prompt)
    
    # Extract improved resume text
    improved_resume_text = ""
    if hasattr(response, 'text'):
        improved_resume_text = response.text
    else:
        improved_resume_text = str(response)
    
    # Generate PDF with improved resume
    pdf = ResumePDF()
    pdf.add_page()
    
    # Split improved resume into sections based on typical section headers
    sections = {}
    current_section = "Header"
    sections[current_section] = []
    
    section_headers = [
        "CONTACT INFORMATION", "SUMMARY", "PROFESSIONAL SUMMARY", 
        "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY",
        "EDUCATION", "SKILLS", "CERTIFICATIONS", "PROJECTS",
        "AWARDS", "LANGUAGES", "INTERESTS"
    ]
    
    # Parse the improved resume text into sections
    for line in improved_resume_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        found_header = False
        for header in section_headers:
            if line.upper().startswith(header) or line.upper() == header:
                current_section = line
                sections[current_section] = []
                found_header = True
                break
                
        if not found_header:
            sections[current_section].append(line)
    
    # Add sections to PDF
    for section, content in sections.items():
        if content:  # Only add non-empty sections
            pdf.chapter_title(section)
            pdf.chapter_body('\n'.join(content))
    
    # Save PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_filepath = tmp_file.name
        
    pdf.output(tmp_filepath)
    
    return tmp_filepath
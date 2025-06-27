import os
import tempfile
from fpdf import FPDF
import streamlit as st
import traceback
import json
import re
from groq import Groq



class UTF8ResumePDF(FPDF):
    """Custom PDF class for generating improved resumes with UTF-8 support"""
    
    def __init__(self):
        super().__init__()
        # Add a default font with UTF-8 support
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', 'DejaVuSansCondensed-Oblique.ttf', uni=True)
    
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

def sanitize_text(text):
    """
    Sanitize text for FPDF to handle special characters
    """
    # Replace common problematic characters
    replacements = {
        '\u2013': '-',  # en-dash
        '\u2014': '-',  # em-dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2022': '*',  # bullet
        '\u2026': '...',  # ellipsis
        '\u00a0': ' ',  # non-breaking space
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Replace any other non-Latin1 characters with their closest ASCII equivalent or remove them
    return re.sub(r'[^\x00-\x7F]+', '', text)

def generate_improved_resume(original_resume_text, improvement_suggestions, job_description=None):
    """
    Generate an improved version of the resume based on AI suggestions using Groq API.
    Args:
        original_resume_text (str): Original resume text
        improvement_suggestions (list): List of improvement suggestions from AI analysis
        job_description (str, optional): Job description for targeted improvements
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Format improvement suggestions for the prompt
        formatted_suggestions = ""
        if improvement_suggestions and isinstance(improvement_suggestions, list):
            for i, suggestion in enumerate(improvement_suggestions):
                category = suggestion.get("category", f"Suggestion {i+1}")
                current = suggestion.get("current", "")
                suggested = suggestion.get("suggested_improvement", "")
                formatted_suggestions += f"- {category}:\n  Current: {current}\n  Suggested: {suggested}\n\n"
        else:
            formatted_suggestions = "No specific suggestions provided. Please improve the general formatting, clarity, and professionalism of the resume."

        # Create a prompt for Groq API to rewrite the resume
        job_desc_section = f"\nJOB DESCRIPTION:\n{job_description}" if job_description else ""
        prompt = f"""
        You are an expert resume writer. Rewrite the following resume by implementing these specific improvements:
        {job_desc_section}
        ORIGINAL RESUME:
        {original_resume_text}
        IMPROVEMENTS TO IMPLEMENT:
        {formatted_suggestions}
        Please rewrite the entire resume with these improvements while maintaining the same core information.
        Structure the resume in standard sections: Contact Information, Summary, Experience, Education, Skills.
        Use bullet points for accomplishments and make them quantifiable where possible.
        Focus on clarity, conciseness, and professional formatting.
        Return ONLY the improved resume text with section headers, no additional explanations.
        Use only ASCII characters (no special quotes, dashes, etc.) to ensure compatibility with all systems.
        """

        # Get API key from Streamlit secrets
        try:
            api_key = st.secrets["GROQ_API_KEY"]
            client = Groq(api_key=api_key)
        except Exception as e:
            st.error(f"Error accessing Groq API key: {str(e)}")
            return None

        # Generate improved resume content using Groq API
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer. Always respond with only the improved resume text, no additional text or formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.3,
                max_tokens=4000,
                top_p=0.9,
                stream=False
            )
            improved_resume_text = chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error generating content with Groq API: {str(e)}")
            st.error(traceback.format_exc())
            return None

        # Sanitize the text to handle problematic characters
        try:
            improved_resume_text = sanitize_text(improved_resume_text)
        except Exception as e:
            st.error(f"Error sanitizing improved resume text: {str(e)}")
            st.error(traceback.format_exc())
            return None

        # Use simpler approach with plain text
        try:
            # Create a simple single-section PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", 'B', size=16)
            pdf.cell(0, 10, "Improved Resume", ln=True, align='C')
            pdf.ln(5)
            pdf.set_font("Arial", size=11)
            pdf_text = improved_resume_text.encode('latin-1', 'replace').decode('latin-1')
            for line in pdf_text.split('\n'):
                if line.isupper() or (line.strip().endswith(':') and len(line) < 30):
                    pdf.set_font("Arial", 'B', size=12)
                    pdf.ln(3)
                    pdf.cell(0, 6, line, ln=True)
                    pdf.set_font("Arial", size=11)
                    pdf.ln(2)
                else:
                    if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*'):
                        indent = 5
                        pdf.set_x(pdf.get_x() + indent)
                        width = pdf.w - pdf.l_margin - pdf.r_margin - indent
                        pdf.multi_cell(width, 5, line)
                    else:
                        pdf.multi_cell(0, 5, line)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_filepath = tmp_file.name
            pdf.output(tmp_filepath)
            return tmp_filepath
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.error(traceback.format_exc())
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=11)
                basic_text = re.sub(r'[^\x00-\x7F]+', '', improved_resume_text)
                chunks = [basic_text[i:i+50] for i in range(0, len(basic_text), 50)]
                for chunk in chunks:
                    try:
                        pdf.cell(0, 5, chunk, ln=True)
                    except:
                        continue
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_filepath = tmp_file.name
                pdf.output(tmp_filepath)
                st.warning("Could only generate a simplified version of the resume due to character encoding issues.")
                return tmp_filepath
            except Exception as final_e:
                st.error("Failed to generate PDF.")
                return None
    except Exception as e:
        st.error(f"Unexpected error in generate_improved_resume: {str(e)}")
        st.error(traceback.format_exc())
        return None
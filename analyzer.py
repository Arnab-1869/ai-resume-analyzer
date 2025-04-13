import os
import fitz  # PyMuPDF
import docx
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_file(file_path):
    """
    Extract text from uploaded resume file (PDF, DOCX, or TXT).
    
    Args:
        file_path (str): Path to the uploaded file
        
    Returns:
        str: Extracted text from the file
    """
    file_extension = file_path.split('.')[-1].lower()
    
    try:
        if file_extension == 'pdf':
            # Try PyMuPDF first
            try:
                text = ""
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text += page.get_text()
                return text
            except Exception as e:
                # Fall back to pdfplumber if PyMuPDF fails
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                return text
                
        elif file_extension == 'docx':
            # Use python-docx for DOCX files
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        elif file_extension == 'txt':
            # Read text file directly
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return None

def analyze_resume(resume_text):
    """
    Analyze resume using Gemini API.
    
    Args:
        resume_text (str): Text extracted from the resume
        
    Returns:
        dict: Analysis results containing strengths, weaknesses, improvement suggestions, 
              job recommendations, and skills recommendations
    """
    prompt = f"""
    You are an expert resume analyzer and career coach. Analyze the following resume 
    and provide detailed, constructive feedback:

    RESUME:
    {resume_text}

    Please provide your analysis in the following JSON format:
    {{
        "strengths": [
            {{
                "category": "string", 
                "details": "string"
            }}
        ],
        "weaknesses": [
            {{
                "category": "string", 
                "details": "string"
            }}
        ],
        "improvement_suggestions": [
            {{
                "category": "string", 
                "current": "string",
                "suggested_improvement": "string"
            }}
        ],
        "job_recommendations": [
            {{
                "title": "string",
                "match_reason": "string",
                "required_skills": ["string"]
            }}
        ],
        "skills_to_develop": [
            {{
                "skill": "string",
                "reason": "string"
            }}
        ],
        "overall_score": "number out of 10",
        "summary_feedback": "string"
    }}

    Make sure your analysis is specific, actionable, and tailored to the individual's 
    career field and experience level. Focus on both content and formatting issues.
    """
    
    # Generate content using Gemini API
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    # Parse the response text into a Python dictionary
    try:
        # Check if the response has a text attribute
        if hasattr(response, 'text'):
            response_text = response.text
        else:
            # Handle different response format if needed
            response_text = str(response)
            
        # Clean up response text to extract just the JSON part
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        response_text = response_text.strip()
        
        # Parse the JSON string into a Python dictionary using eval
        # Note: In production, you should use json.loads() with proper error handling
        import json
        analysis_result = json.loads(response_text)
        
        return analysis_result
        
    except Exception as e:
        print(f"Error parsing API response: {str(e)}")
        # Return a error-indicating result
        return {
            "error": True,
            "message": "Failed to parse analysis results. Please try again.",
            "details": str(e)
        }
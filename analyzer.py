import os
import fitz  # PyMuPDF
import docx
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

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
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                return file.read()
                
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return None

def extract_json_from_text(text):
    """
    Extract JSON from text which might contain other non-JSON content.
    
    Args:
        text (str): Text that may contain JSON
        
    Returns:
        dict: Parsed JSON as a Python dictionary, or None if parsing fails
    """
    # First, try to parse the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON using regex pattern matching
    try:
        # Look for text that appears to be JSON (starts with { and ends with })
        json_pattern = r'({[\s\S]*?})'
        matches = re.findall(json_pattern, text)
        
        # Try each potential JSON match
        for potential_json in matches:
            try:
                return json.loads(potential_json)
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    
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
    # Improve the prompt to ensure structured output
    prompt = f"""
    You are an expert resume analyzer and career coach. Analyze the following resume 
    and provide detailed, constructive feedback.
    
    Important: Your response MUST be valid JSON following the exact format below.

    RESUME:
    {resume_text}

    Provide your analysis in this exact JSON structure:
    {{
        "strengths": [
            {{
                "category": "Category name", 
                "details": "Detailed explanation"
            }}
        ],
        "weaknesses": [
            {{
                "category": "Category name", 
                "details": "Detailed explanation"
            }}
        ],
        "improvement_suggestions": [
            {{
                "category": "Category name", 
                "current": "Current content or approach",
                "suggested_improvement": "Specific suggested improvement"
            }}
        ],
        "job_recommendations": [
            {{
                "title": "Job title",
                "match_reason": "Why this job matches the resume",
                "required_skills": ["Skill 1", "Skill 2", "Skill 3"]
            }}
        ],
        "skills_to_develop": [
            {{
                "skill": "Skill name",
                "reason": "Why this skill would be valuable"
            }}
        ],
        "overall_score": "7 out of 10",
        "summary_feedback": "Overall summary of the resume analysis"
    }}

    Make your analysis specific, actionable, and tailored to the individual's 
    career field and experience level. Focus on both content and formatting issues.
    Ensure your response is ONLY valid JSON with no markdown formatting, code blocks, or explanatory text.
    """
    
    # Set safety settings to allow more content through, as resume analysis is generally safe
    safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_ONLY_HIGH",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_ONLY_HIGH",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_ONLY_HIGH",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_ONLY_HIGH",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_ONLY_HIGH",
        },
    ]
    
    try:
        # Generate content using Gemini API with updated model name
        model = genai.GenerativeModel('gemini-1.5-pro', safety_settings=safety_settings)
        
        # Try with a higher temperature for more creative responses
        generation_config = {
            "temperature": 0.2,  # Lower temperature for more structured outputs
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        response = model.generate_content(
            prompt, 
            generation_config=generation_config
        )
        
        # Extract response text
        if hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = str(response)
        
        # Clean up response text to extract just the JSON part
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse the JSON with our robust function
        analysis_result = extract_json_from_text(response_text)
        
        if analysis_result is None:
            # If we still can't parse JSON, try a second request with a simpler prompt
            simple_prompt = f"""
            Analyze this resume and return a simple JSON structure with just these fields:
            
            RESUME:
            {resume_text}
            
            Return only this JSON structure, with no explanation or additional text:
            {{
                "strengths": ["Strength 1", "Strength 2"],
                "weaknesses": ["Weakness 1", "Weakness 2"],
                "overall_score": "7 out of 10",
                "summary_feedback": "Brief overall summary"
            }}
            """
            
            print("Trying simplified prompt due to JSON parsing issues...")
            response = model.generate_content(simple_prompt, generation_config=generation_config)
            
            if hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)
            
            # Clean up response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Try to parse the simplified JSON
            analysis_result = extract_json_from_text(response_text)
            
            if analysis_result is None:
                raise Exception("Failed to parse JSON from both attempts")
            
            # Add empty fields for the missing sections in our simplified approach
            analysis_result["improvement_suggestions"] = []
            analysis_result["job_recommendations"] = []
            analysis_result["skills_to_develop"] = []
            
            # Convert simple strengths and weaknesses to the expected format
            analysis_result["strengths"] = [{"category": "Strength", "details": s} for s in analysis_result["strengths"]]
            analysis_result["weaknesses"] = [{"category": "Weakness", "details": w} for w in analysis_result["weaknesses"]]
        
        return analysis_result
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        # Return an error-indicating result
        return {
            "error": True,
            "message": "Failed to parse analysis results. Please try again.",
            "details": str(e)
        }
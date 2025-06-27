import os
import fitz  # PyMuPDF
import docx
import pdfplumber
import json
import re
import time
import hashlib
import streamlit as st
from datetime import datetime, timedelta
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SmartAnalyzer: Handles API communication, rate limiting, caching
class SmartAnalyzer:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)  # ✅ Correct instantiation
        self.requests_per_minute = 30
        self.request_times = []
        self.cache = {}

    def _get_cache_key(self, resume_text, job_description=""):
        combined_text = f"{resume_text[:500]}{job_description[:200]}"
        return hashlib.md5(combined_text.encode()).hexdigest()

    def _can_make_request(self):
        now = datetime.now()
        self.request_times = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        return len(self.request_times) < self.requests_per_minute

    def _wait_for_rate_limit(self):
        if not self._can_make_request():
            wait_time = 60 - (datetime.now() - min(self.request_times)).seconds
            if wait_time > 0:
                st.info(f"Rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time + 1)

    def _make_groq_request(self, prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert resume analyzer and career coach. Always respond with valid JSON only, no additional text or formatting."
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
                self.request_times.append(datetime.now())
                return chat_completion.choices[0].message.content
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "quota" in error_msg:
                    wait_time = 2 ** attempt
                    st.warning(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                elif attempt == max_retries - 1:
                    st.error(f"Final retry failed: {str(e)}")
                    raise e
                else:
                    time.sleep(1)

# Global analyzer instance
analyzer = None

def initialize_analyzer(api_key):
    global analyzer
    analyzer = SmartAnalyzer(api_key)

def extract_text_from_file(file_path):
    file_extension = file_path.split('.')[-1].lower()
    try:
        if file_extension == 'pdf':
            try:
                text = ""
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text += page.get_text()
                return text
            except:
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                return text
        elif file_extension == 'docx':
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"Text extraction error: {str(e)}")
        return None

def extract_json_from_text(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        matches = re.findall(r'({[\s\S]*?})', text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    except:
        pass
    return None

def analyze_resume(resume_text, job_description=""):
    cache_key = analyzer._get_cache_key(resume_text, job_description)
    if cache_key in analyzer.cache:
        st.info("Using cached analysis results")
        return analyzer.cache[cache_key]

    if job_description.strip():
        prompt = f"""
        You are an expert resume analyzer and career coach. Analyze the following resume against the provided job description and provide detailed, constructive feedback.

        RESUME:
        {resume_text[:3000]}

        JOB DESCRIPTION:
        {job_description[:2000]}

        Provide your analysis in this exact JSON structure:
        {{
            "job_match_score": "8 out of 10",
            "job_match_summary": "Brief explanation",
            "strengths": [{{"category": "Category", "details": "Details"}}],
            "weaknesses": [{{"category": "Category", "details": "Details"}}],
            "improvement_suggestions": [{{"category": "Category", "current": "Current", "suggested_improvement": "Improvement"}}],
            "missing_keywords": [{{"keyword": "Keyword", "importance": "Why it's important"}}],
            "skills_to_develop": [{{"skill": "Skill", "reason": "Why develop it"}}],
            "overall_score": "7 out of 10",
            "summary_feedback": "Summary"
        }}

        Only return valid JSON.
        """
    else:
        prompt = f"""
        You are an expert resume analyzer and career coach. Analyze the following resume and provide detailed, constructive feedback.

        RESUME:
        {resume_text[:4000]}

        Provide your analysis in this exact JSON structure:
        {{
            "strengths": [{{"category": "Category", "details": "Details"}}],
            "weaknesses": [{{"category": "Category", "details": "Details"}}],
            "improvement_suggestions": [{{"category": "Category", "current": "Current", "suggested_improvement": "Improvement"}}],
            "job_recommendations": [{{"title": "Job", "match_reason": "Reason", "required_skills": ["Skill1", "Skill2"]}}],
            "skills_to_develop": [{{"skill": "Skill", "reason": "Why"}}],
            "overall_score": "7 out of 10",
            "summary_feedback": "Summary"
        }}

        Only return valid JSON.
        """

    try:
        response_text = analyzer._make_groq_request(prompt)
        if not response_text:
            return {"error": True, "message": "No response from Groq"}

        result = extract_json_from_text(response_text)
        if not result:
            return {
                "error": True,
                "message": "Could not parse JSON",
                "details": f"Raw response: {response_text[:500]}"
            }

        # Add required defaults
        defaults = {
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": [],
            "skills_to_develop": [],
            "overall_score": "5 out of 10",
            "summary_feedback": "Analysis complete"
        }
        for k, v in defaults.items():
            result.setdefault(k, v)

        if not job_description.strip() and "job_recommendations" not in result:
            result["job_recommendations"] = [{
                "title": "Consider various relevant roles",
                "match_reason": "Skills and experience suggest good fit",
                "required_skills": ["Communication", "Teamwork", "Problem Solving"]
            }]

        analyzer.cache[cache_key] = result
        return result

    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return {"error": True, "message": str(e)}

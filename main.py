import streamlit as st
import os
import tempfile
from analyzer import extract_text_from_file, analyze_resume
from pdf_generator import generate_improved_resume
from utils import setup_page, display_analysis_results, display_job_recommendations
import google.generativeai as genai
import traceback
import json

# Configure Gemini API with Streamlit secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    st.session_state["api_key_configured"] = True
except Exception as e:
    st.session_state["api_key_configured"] = False
    st.session_state["api_key_error"] = str(e)

def main():
    # Setup page configuration
    setup_page()
    
    # Check API key configuration
    if not st.session_state.get("api_key_configured", False):
        st.error(f"API key configuration error: {st.session_state.get('api_key_error', 'Unknown error')}")
        return
    
    st.title("AI Resume Analyzer")
    st.write("Upload your resume to get personalized feedback and job recommendations")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        # Create a temporary file to store the uploaded resume
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_filepath = tmp_file.name
        except Exception as e:
            st.error(f"Error saving uploaded file: {str(e)}")
            st.error(traceback.format_exc())
            return
        
        with st.spinner("Extracting text from your resume..."):
            try:
                resume_text = extract_text_from_file(tmp_filepath)
            except Exception as e:
                st.error(f"Error extracting text: {str(e)}")
                st.error(traceback.format_exc())
                resume_text = None
            
        if not resume_text:
            st.error("Failed to extract text from the uploaded file. Please try another file.")
            try:
                os.unlink(tmp_filepath)
            except:
                pass
            return
        
        # Show a preview of the extracted text
        with st.expander("Resume Text Preview"):
            st.text(resume_text[:1000] + ("..." if len(resume_text) > 1000 else ""))
        
        # Use a form to ensure proper state management with the button
        with st.form(key="analysis_form"):
            submit_button = st.form_submit_button(label="Analyze Resume")
            
        # Analyze the resume with Gemini API when button is clicked
        if submit_button:
            with st.spinner("Analyzing your resume with AI..."):
                try:
                    analysis_result = analyze_resume(resume_text)
                    
                    # Save analysis result in session state
                    st.session_state["analysis_result"] = analysis_result
                    st.session_state["resume_text"] = resume_text
                    
                    # Display analysis results
                    display_analysis_results(analysis_result)
                    
                    # Display job recommendations
                    if "job_recommendations" in analysis_result:
                        display_job_recommendations(analysis_result["job_recommendations"])
                    
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
                    st.error(traceback.format_exc())
        
        # Option to generate improved resume (outside form)
        if st.session_state.get("analysis_result") is not None:
            st.subheader("Generate Improved Resume")
            st.write("Click below to generate an improved version of your resume based on the feedback")
            
            if st.button("Generate Improved Resume"):
                with st.spinner("Generating improved resume..."):
                    try:
                        # Get analysis result and resume text from session state
                        analysis_result = st.session_state["analysis_result"]
                        resume_text = st.session_state["resume_text"]
                        
                        # Check improvement suggestions
                        if "improvement_suggestions" in analysis_result:
                            suggestions = analysis_result["improvement_suggestions"]
                        else:
                            suggestions = []
                            
                        # Generate improved resume
                        improved_resume_path = generate_improved_resume(
                            resume_text, 
                            suggestions
                        )
                        
                        if improved_resume_path:
                            st.success("Improved resume generated successfully!")
                            with open(improved_resume_path, "rb") as file:
                                pdf_data = file.read()
                                
                            st.download_button(
                                label="Download Improved Resume",
                                data=pdf_data,
                                file_name="improved_resume.pdf",
                                mime="application/pdf"
                            )
                            
                            # Clean up temporary file
                            try:
                                os.unlink(improved_resume_path)
                            except Exception:
                                pass
                        else:
                            st.error("Failed to generate improved resume.")
                    except Exception as e:
                        st.error(f"An error occurred while generating the improved resume: {str(e)}")
                        st.error(traceback.format_exc())
        
        # Clean up temporary file
        try:
            os.unlink(tmp_filepath)
        except:
            pass

if __name__ == "__main__":
    main()
import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
from analyzer import extract_text_from_file, analyze_resume
from pdf_generator import generate_improved_resume
from utils import setup_page, display_analysis_results, display_job_recommendations

# Load environment variables
load_dotenv()

def main():
    # Setup page configuration
    setup_page()
    
    st.title("AI Resume Analyzer")
    st.write("Upload your resume to get personalized feedback and job recommendations")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        # Create a temporary file to store the uploaded resume
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_filepath = tmp_file.name
        
        with st.spinner("Extracting text from your resume..."):
            resume_text = extract_text_from_file(tmp_filepath)
            
        if not resume_text:
            st.error("Failed to extract text from the uploaded file. Please try another file.")
            os.unlink(tmp_filepath)
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
                    # Clear any previous output
                    st.empty()
                    
                    analysis_result = analyze_resume(resume_text)
                    
                    # Display analysis results
                    display_analysis_results(analysis_result)
                    
                    # Display job recommendations
                    if "job_recommendations" in analysis_result:
                        display_job_recommendations(analysis_result["job_recommendations"])
                    
                    # Option to generate improved resume
                    if st.button("Generate Improved Resume"):
                        with st.spinner("Generating improved resume..."):
                            improved_resume_path = generate_improved_resume(
                                resume_text, 
                                analysis_result["improvement_suggestions"]
                            )
                            
                            with open(improved_resume_path, "rb") as file:
                                st.download_button(
                                    label="Download Improved Resume",
                                    data=file,
                                    file_name="improved_resume.pdf",
                                    mime="application/pdf"
                                )
                            
                            # Clean up temporary file
                            os.unlink(improved_resume_path)
                
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
        
        # Clean up temporary file
        os.unlink(tmp_filepath)

if __name__ == "__main__":
    main()

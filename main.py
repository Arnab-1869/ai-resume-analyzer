import streamlit as st
import os
import tempfile
from analyzer import extract_text_from_file, analyze_resume, initialize_analyzer
from pdf_generator import generate_improved_resume
from utils import setup_page, display_analysis_results, display_job_recommendations, display_job_match_results
import traceback
import json

# Configure Groq API with Streamlit secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
    initialize_analyzer(api_key)
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
        st.info("Please check your secrets.toml file and ensure GROQ_API_KEY is properly set.")
        return
    
    st.title("🤖 AI Resume Analyzer")
    st.write("Upload your resume and optionally add a job description for targeted analysis")
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
    
    with col2:
        st.subheader("💼 Job Description (Optional)")
        job_description = st.text_area(
            "Paste the job description here for targeted analysis",
            height=200,
            placeholder="Copy and paste the job description you want to match your resume against..."
        )
        
        # Show character count
        if job_description:
            char_count = len(job_description)
            st.caption(f"Characters: {char_count}/2000 {'⚠️ (truncated)' if char_count > 2000 else '✅'}")
    
    # Analysis type selection
    analysis_type = st.radio(
        "Choose analysis type:",
        ["General Resume Analysis", "Job-Specific Analysis (with job description)"],
        help="Job-specific analysis provides targeted feedback when you include a job description"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Create a temporary file to store the uploaded resume
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_filepath = tmp_file.name
        except Exception as e:
            st.error(f"Error saving uploaded file: {str(e)}")
            return
        
        with st.spinner("📖 Extracting text from your resume..."):
            try:
                resume_text = extract_text_from_file(tmp_filepath)
            except Exception as e:
                st.error(f"Error extracting text: {str(e)}")
                st.error(traceback.format_exc())
                resume_text = None
            
        if not resume_text:
            st.error("❌ Failed to extract text from the uploaded file. Please try another file.")
            try:
                os.unlink(tmp_filepath)
            except:
                pass
            return
        
        # Show a preview of the extracted text
        with st.expander("👀 Resume Text Preview"):
            st.text(resume_text[:1000] + ("..." if len(resume_text) > 1000 else ""))
            st.caption(f"Total characters extracted: {len(resume_text)}")
        
        # Validate job description if job-specific analysis is selected
        if analysis_type == "Job-Specific Analysis (with job description)":
            if not job_description.strip():
                st.warning("⚠️ Please add a job description for job-specific analysis, or switch to general analysis.")
                return
        
        # Use a form to ensure proper state management with the button
        with st.form(key="analysis_form"):
            submit_button = st.form_submit_button(
                label="🔍 Analyze Resume" if analysis_type == "General Resume Analysis" else "🎯 Analyze Resume for Job Match",
                use_container_width=True
            )
            
        # Analyze the resume when button is clicked
        if submit_button:
            # Determine which analysis to run
            job_desc_for_analysis = job_description if analysis_type == "Job-Specific Analysis (with job description)" else ""
            
            with st.spinner("🤖 Analyzing your resume with AI... This may take a moment."):
                try:
                    analysis_result = analyze_resume(resume_text, job_desc_for_analysis)
                    
                    # Save analysis result in session state
                    st.session_state["analysis_result"] = analysis_result
                    st.session_state["resume_text"] = resume_text
                    st.session_state["job_description"] = job_desc_for_analysis
                    st.session_state["analysis_type"] = analysis_type
                    
                    # Display results based on analysis type
                    if job_desc_for_analysis:
                        # Display job-specific results
                        display_job_match_results(analysis_result)
                    else:
                        # Display general analysis results
                        display_analysis_results(analysis_result)
                        
                        # Display job recommendations for general analysis
                        if "job_recommendations" in analysis_result:
                            display_job_recommendations(analysis_result["job_recommendations"])
                    
                except Exception as e:
                    st.error(f"❌ An error occurred during analysis: {str(e)}")
                    st.error("**Debug Info:**")
                    st.code(traceback.format_exc())
                    
                    # Show helpful tips
                    st.info("""
                    **Troubleshooting Tips:**
                    - Try with a smaller resume file
                    - Ensure your internet connection is stable
                    - If the error persists, try again in a few minutes
                    """)
        
        # Option to generate improved resume (outside form)
        if st.session_state.get("analysis_result") is not None:
            st.divider()
            st.subheader("📝 Generate Improved Resume")
            
            # Show different options based on analysis type
            if st.session_state.get("analysis_type") == "Job-Specific Analysis (with job description)":
                st.write("Generate an improved resume tailored specifically for the job you're targeting")
            else:
                st.write("Generate an improved version of your resume based on general best practices")
            
            if st.button("✨ Generate Improved Resume", use_container_width=True):
                with st.spinner("📝 Generating improved resume..."):
                    try:
                        # Get analysis result and resume text from session state
                        analysis_result = st.session_state["analysis_result"]
                        resume_text = st.session_state["resume_text"]
                        job_description = st.session_state.get("job_description", "")
                        
                        # Check improvement suggestions
                        suggestions = analysis_result.get("improvement_suggestions", [])
                        
                        # Generate improved resume
                        improved_resume_path = generate_improved_resume(
                            resume_text, 
                            suggestions,
                            job_description  # Pass job description for targeted improvements
                        )
                        
                        if improved_resume_path:
                            st.success("✅ Improved resume generated successfully!")
                            with open(improved_resume_path, "rb") as file:
                                pdf_data = file.read()
                                
                            # Create filename based on analysis type
                            filename = "improved_resume_job_targeted.pdf" if job_description else "improved_resume.pdf"
                            
                            st.download_button(
                                label="📥 Download Improved Resume",
                                data=pdf_data,
                                file_name=filename,
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            # Clean up temporary file
                            try:
                                os.unlink(improved_resume_path)
                            except Exception:
                                pass
                        else:
                            st.error("❌ Failed to generate improved resume.")
                    except Exception as e:
                        st.error(f"❌ An error occurred while generating the improved resume: {str(e)}")
                        st.error(traceback.format_exc())
        
        # Clean up temporary file
        try:
            os.unlink(tmp_filepath)
        except:
            pass
    
    else:
        # Show helpful instructions when no file is uploaded
        st.info("""
        **How to use:**
        1. 📤 Upload your resume (PDF, DOCX, or TXT format)
        2. 💼 Optionally add a job description for targeted analysis
        3. 🎯 Choose between general analysis or job-specific matching
        4. 🔍 Click analyze to get AI-powered feedback
        5. 📝 Generate an improved resume based on the suggestions
        """)
        
        # Show sample job description
        with st.expander("💡 Sample Job Description"):
            st.text("""
Software Engineer - Full Stack Developer

We are looking for a skilled Full Stack Developer to join our team. 
The ideal candidate will have experience with:

• Frontend: React, JavaScript, HTML, CSS
• Backend: Node.js, Python, REST APIs
• Database: MongoDB, PostgreSQL
• Cloud: AWS, Docker, Kubernetes
• Version Control: Git, GitHub
• Agile methodologies and team collaboration

Requirements:
- 3+ years of software development experience
- Strong problem-solving skills
- Bachelor's degree in Computer Science or related field
- Experience with CI/CD pipelines
- Excellent communication skills
            """)

if __name__ == "__main__":
    main()
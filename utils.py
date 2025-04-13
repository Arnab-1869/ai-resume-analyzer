import streamlit as st
import os
import base64

def setup_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply simpler custom CSS that works more reliably
    st.markdown("""
    <style>
        .main {
            padding: 2rem 2rem;
        }
        h1 {
            color: #2e6e9e;
        }
    </style>
    """, unsafe_allow_html=True)

def display_analysis_results(analysis):
    """
    Display analysis results using standard Streamlit components.
    
    Args:
        analysis (dict): Analysis results from the Gemini API
    """
    if "error" in analysis:
        st.error(analysis["message"])
        st.error(f"Details: {analysis['details']}")
        return
    
    # Display overall score and summary using standard Streamlit components
    st.header("Resume Analysis Results")
    
    # Get the score as a number for coloring
    try:
        score_text = analysis.get("overall_score", "0 out of 10")
        score_value = float(score_text.split()[0])
        
        # Create a color based on the score
        if score_value >= 7:
            score_color = "green"
        elif score_value >= 5:
            score_color = "orange"
        else:
            score_color = "red"
            
        st.markdown(f"<h3 style='text-align: center; color: {score_color};'>Overall Score: {score_text}</h3>", 
                   unsafe_allow_html=True)
    except:
        st.subheader(f"Overall Score: {analysis.get('overall_score', 'N/A')}")
    
    # Summary feedback
    st.subheader("Summary Feedback")
    st.info(analysis.get("summary_feedback", "No summary available"))
    
    # Display strengths using Streamlit expander and success elements
    st.subheader("Strengths")
    strengths = analysis.get("strengths", [])
    if strengths:
        for strength in strengths:
            category = strength.get("category", "")
            details = strength.get("details", "")
            with st.expander(f"✅ {category}"):
                st.success(details)
    else:
        st.write("No strengths identified.")
    
    # Display weaknesses using Streamlit expander and warning elements
    st.subheader("Areas for Improvement")
    weaknesses = analysis.get("weaknesses", [])
    if weaknesses:
        for weakness in weaknesses:
            category = weakness.get("category", "")
            details = weakness.get("details", "")
            with st.expander(f"⚠️ {category}"):
                st.warning(details)
    else:
        st.write("No areas for improvement identified.")
    
    # Display improvement suggestions using Streamlit expander and info elements
    st.subheader("Specific Suggestions")
    improvements = analysis.get("improvement_suggestions", [])
    if improvements:
        for improvement in improvements:
            category = improvement.get("category", "")
            current = improvement.get("current", "")
            suggested = improvement.get("suggested_improvement", "")
            
            with st.expander(f"💡 {category}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Current:**")
                    st.write(current)
                with col2:
                    st.markdown("**Suggested:**")
                    st.write(suggested)
    else:
        st.write("No specific suggestions available.")
    
    # Display skills to develop
    st.subheader("Skills to Develop")
    skills = analysis.get("skills_to_develop", [])
    if skills:
        for skill in skills:
            skill_name = skill.get("skill", "")
            reason = skill.get("reason", "")
            
            with st.expander(f"🔍 {skill_name}"):
                st.info(reason)
    else:
        st.write("No skill recommendations available.")

def display_job_recommendations(job_recommendations):
    """
    Display job recommendations using standard Streamlit components.
    
    Args:
        job_recommendations (list): List of job recommendations from the analysis
    """
    st.subheader("Job Recommendations")
    
    if not job_recommendations:
        st.write("No job recommendations available.")
        return
    
    for job in job_recommendations:
        title = job.get("title", "")
        match_reason = job.get("match_reason", "")
        required_skills = job.get("required_skills", [])
        
        with st.expander(f"💼 {title}"):
            st.markdown("**Why this might be a good fit:**")
            st.write(match_reason)
            
            st.markdown("**Required skills:**")
            if required_skills:
                for skill in required_skills:
                    st.markdown(f"- {skill}")
            else:
                st.write("No specific skills listed.")

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """
    Generate HTML code for a file download link
    
    Args:
        bin_file (str): Path to the binary file
        file_label (str): Label for the download button
        
    Returns:
        str: HTML code for the download link
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href
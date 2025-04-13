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
    
    # Apply custom CSS
    st.markdown("""
    <style>
        .main {
            padding: 2rem 2rem;
        }
        h1 {
            color: #2e6e9e;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .section-header {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .strength {
            background-color: #e6ffec;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        .weakness {
            background-color: #ffebe6;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        .improvement {
            background-color: #e6f3ff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        .job {
            background-color: #f2e6ff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

def display_analysis_results(analysis):
    """
    Display analysis results in a well-formatted way.
    
    Args:
        analysis (dict): Analysis results from the Gemini API
    """
    if "error" in analysis:
        st.error(analysis["message"])
        st.error(f"Details: {analysis['details']}")
        return
    
    # Display overall score and summary
    score_color = "green" if float(analysis.get("overall_score", "0").split()[0]) >= 7 else "orange"
    st.markdown(f"""
    <h2 style='text-align: center;'>Resume Analysis Results</h2>
    <h3 style='text-align: center; color: {score_color};'>
        Overall Score: {analysis.get("overall_score", "N/A")}
    </h3>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### Summary Feedback")
    st.info(analysis.get("summary_feedback", "No summary available"))
    
    # Display strengths
    st.markdown("<div class='section-header'><h3>Strengths</h3></div>", unsafe_allow_html=True)
    strengths = analysis.get("strengths", [])
    if strengths:
        for strength in strengths:
            st.markdown(f"""
            <div class='strength'>
                <b>{strength.get("category", "")}</b>: {strength.get("details", "")}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No strengths identified.")
    
    # Display weaknesses
    st.markdown("<div class='section-header'><h3>Areas for Improvement</h3></div>", unsafe_allow_html=True)
    weaknesses = analysis.get("weaknesses", [])
    if weaknesses:
        for weakness in weaknesses:
            st.markdown(f"""
            <div class='weakness'>
                <b>{weakness.get("category", "")}</b>: {weakness.get("details", "")}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No areas for improvement identified.")
    
    # Display improvement suggestions
    st.markdown("<div class='section-header'><h3>Specific Suggestions</h3></div>", unsafe_allow_html=True)
    improvements = analysis.get("improvement_suggestions", [])
    if improvements:
        for improvement in improvements:
            st.markdown(f"""
            <div class='improvement'>
                <b>{improvement.get("category", "")}</b>:<br>
                <b>Current</b>: {improvement.get("current", "")}<br>
                <b>Suggested</b>: {improvement.get("suggested_improvement", "")}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No specific suggestions available.")
    
    # Display skills to develop
    st.markdown("<div class='section-header'><h3>Skills to Develop</h3></div>", unsafe_allow_html=True)
    skills = analysis.get("skills_to_develop", [])
    if skills:
        for skill in skills:
            st.markdown(f"""
            <div class='improvement'>
                <b>{skill.get("skill", "")}</b>: {skill.get("reason", "")}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No skill recommendations available.")

def display_job_recommendations(job_recommendations):
    """
    Display job recommendations in a well-formatted way.
    
    Args:
        job_recommendations (list): List of job recommendations from the analysis
    """
    st.markdown("<div class='section-header'><h3>Job Recommendations</h3></div>", unsafe_allow_html=True)
    
    if not job_recommendations:
        st.write("No job recommendations available.")
        return
    
    for job in job_recommendations:
        st.markdown(f"""
        <div class='job'>
            <h4>{job.get("title", "")}</h4>
            <b>Why this might be a good fit</b>: {job.get("match_reason", "")}<br>
            <b>Required skills</b>: {", ".join(job.get("required_skills", []))}
        </div>
        """, unsafe_allow_html=True)

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
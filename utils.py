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
    
    # Apply custom CSS for better styling
    st.markdown("""
    <style>
        .main {
            padding: 2rem 2rem;
        }
        h1 {
            color: #2e6e9e;
        }
        .job-match-score {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .high-match {
            background-color: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }
        .medium-match {
            background-color: #fff3cd;
            color: #856404;
            border: 2px solid #ffeaa7;
        }
        .low-match {
            background-color: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
        }
        .keyword-tag {
            background-color: #e3f2fd;
            color: #1565c0;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 12px;
            margin: 2px;
            display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)

def display_job_match_results(analysis):
    """
    Display job-specific analysis results with match scoring.
    
    Args:
        analysis (dict): Analysis results from the AI with job matching
    """
    if "error" in analysis:
        st.error(analysis["message"])
        st.error(f"Details: {analysis['details']}")
        return
    
    # Display job match score prominently
    st.header("🎯 Job Match Analysis Results")
    
    # Get job match score and style accordingly
    job_match_score = analysis.get("job_match_score", "0 out of 10")
    job_match_summary = analysis.get("job_match_summary", "No match summary available")
    
    try:
        score_value = float(job_match_score.split()[0])
        if score_value >= 7:
            match_class = "high-match"
            match_emoji = "🎉"
        elif score_value >= 5:
            match_class = "medium-match"
            match_emoji = "👍"
        else:
            match_class = "low-match"
            match_emoji = "📈"
    except:
        match_class = "medium-match"
        match_emoji = "📊"
    
    st.markdown(f"""
    <div class="job-match-score {match_class}">
        {match_emoji} Job Match Score: {job_match_score}
    </div>
    """, unsafe_allow_html=True)
    
    # Job match summary
    st.subheader("📋 Match Summary")
    st.info(job_match_summary)
    
    # Missing keywords section
    st.subheader("🔍 Missing Keywords")
    missing_keywords = analysis.get("missing_keywords", [])
    if missing_keywords:
        st.warning("Consider adding these important keywords from the job description:")
        
        # Display keywords as tags
        keywords_html = ""
        for keyword_info in missing_keywords:
            keyword = keyword_info.get("keyword", "")
            importance = keyword_info.get("importance", "")
            keywords_html += f'<span class="keyword-tag" title="{importance}">{keyword}</span>'
        
        st.markdown(keywords_html, unsafe_allow_html=True)
        
        # Detailed keyword explanations
        with st.expander("📝 Why these keywords matter"):
            for keyword_info in missing_keywords:
                keyword = keyword_info.get("keyword", "")
                importance = keyword_info.get("importance", "")
                st.markdown(f"**{keyword}:** {importance}")
    else:
        st.success("✅ Your resume includes most relevant keywords from the job description!")
    
    # Display regular analysis sections
    display_analysis_results(analysis, show_header=False)

def display_analysis_results(analysis, show_header=True):
    """
    Display analysis results using standard Streamlit components.
    
    Args:
        analysis (dict): Analysis results from the AI
        show_header (bool): Whether to show the main header
    """
    if "error" in analysis:
        st.error(analysis["message"])
        st.error(f"Details: {analysis['details']}")
        return
    
    # Display overall score and summary
    if show_header:
        st.header("📊 Resume Analysis Results")
    
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
            
        st.markdown(f"<h3 style='text-align: center; color: {score_color};'>Overall Resume Score: {score_text}</h3>", 
                   unsafe_allow_html=True)
    except:
        st.subheader(f"Overall Score: {analysis.get('overall_score', 'N/A')}")
    
    # Summary feedback
    st.subheader("📝 Summary Feedback")
    st.info(analysis.get("summary_feedback", "No summary available"))
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["✅ Strengths", "⚠️ Areas to Improve", "💡 Suggestions", "🚀 Skills to Develop"])
    
    with tab1:
        # Display strengths
        strengths = analysis.get("strengths", [])
        if strengths:
            for i, strength in enumerate(strengths):
                category = strength.get("category", f"Strength {i+1}")
                details = strength.get("details", "")
                with st.expander(f"✅ {category}", expanded=i==0):
                    st.success(details)
        else:
            st.write("No specific strengths identified.")
    
    with tab2:
        # Display weaknesses
        weaknesses = analysis.get("weaknesses", [])
        if weaknesses:
            for i, weakness in enumerate(weaknesses):
                category = weakness.get("category", f"Area {i+1}")
                details = weakness.get("details", "")
                with st.expander(f"⚠️ {category}", expanded=i==0):
                    st.warning(details)
        else:
            st.write("No major areas for improvement identified.")
    
    with tab3:
        # Display improvement suggestions
        improvements = analysis.get("improvement_suggestions", [])
        if improvements:
            for i, improvement in enumerate(improvements):
                category = improvement.get("category", f"Suggestion {i+1}")
                current = improvement.get("current", "")
                suggested = improvement.get("suggested_improvement", "")
                
                with st.expander(f"💡 {category}", expanded=i==0):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Current:**")
                        st.write(current if current else "Not specified")
                    with col2:
                        st.markdown("**💡 Suggested:**")
                        st.write(suggested)
        else:
            st.write("No specific suggestions available.")
    
    with tab4:
        # Display skills to develop
        skills = analysis.get("skills_to_develop", [])
        if skills:
            for i, skill in enumerate(skills):
                skill_name = skill.get("skill", f"Skill {i+1}")
                reason = skill.get("reason", "")
                
                with st.expander(f"🚀 {skill_name}", expanded=i==0):
                    st.info(reason)
        else:
            st.write("No specific skill recommendations available.")

def display_job_recommendations(job_recommendations):
    """
    Display job recommendations using standard Streamlit components.
    
    Args:
        job_recommendations (list): List of job recommendations from the analysis
    """
    st.subheader("💼 Job Recommendations")
    
    if not job_recommendations:
        st.write("No job recommendations available.")
        return
    
    for i, job in enumerate(job_recommendations):
        title = job.get("title", f"Job {i+1}")
        match_reason = job.get("match_reason", "")
        required_skills = job.get("required_skills", [])
        
        with st.expander(f"💼 {title}", expanded=i==0):
            st.markdown("**Why this might be a good fit:**")
            st.write(match_reason)
            
            if required_skills:
                st.markdown("**Required skills:**")
                # Display skills as badges
                skills_html = ""
                for skill in required_skills:
                    skills_html += f'<span class="keyword-tag">{skill}</span>'
                st.markdown(skills_html, unsafe_allow_html=True)

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
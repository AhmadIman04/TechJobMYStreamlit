import streamlit as st
import google.generativeai as genai
import time
from Functions import linkedin_job_searcher
from Functions import jobstreet_job_searcher
from Functions import maukerja_job_searcher
from Functions import glassdoor_job_searcher

# Main Title
st.markdown(
    """
    <h1 style="text-align: center; color: #0d6abf; font-weight: bold; font-size: 70px;">
        TechJobMY
    </h1>
    """,
    unsafe_allow_html=True
)

# Inject Custom CSS for styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #171717;
        text-align: center;
        margin-top: 20px;
    }
    .sub-title {
        font-size: 1.3em;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .col-header {
        font-size: 1.1em;
        font-weight: 500;
        color: #333;
        margin-bottom: 5px;
    }
    .button-style {
        background-color: #4CAF50;
        color: white;
        font-size: 1.1em;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Page Title and Subtitle
#st.markdown('<div class="main-title">Job Search Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Customize your search preferences and get instant job listings</div>', unsafe_allow_html=True)
st.markdown("---")
# Container for form inputs
with st.container():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # 1. Job Preferences Input (using text_area for long input)
    st.markdown('<div class="col-header">Job Preferences *</div>', unsafe_allow_html=True)
    job_preference = st.text_area(
        "Enter your job preferences:", 
        placeholder="E.g., Looking for a role in software engineering with a focus on AI/ML...", 
        height=150
    )
    
    # 2. Two columns: Job Count and Job Portal
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="col-header">Job Count *</div>', unsafe_allow_html=True)
        job_count = st.number_input(
            "How many jobs do you want to see?", 
            min_value=1, 
            step=1, 
            value=1
        )
    with col2:
        st.markdown('<div class="col-header">Job Portal *</div>', unsafe_allow_html=True)
        job_portal = st.selectbox(
            "Select a job portal:", 
            ["Linkedin", "MauKerja","Glassdoor"]
        )
    
    # 3. Optional Resume Uploader
    st.markdown('<div class="col-header">Resume (Optional)</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader(
        "Upload your resume (Must be in PDF)", 
        type=["pdf"]
    )
    if resume_file is not None:
        st.success("Resume uploaded successfully!")
    
    # 4. Submit Button
    if st.button("Submit"):
        if job_preference.strip() == "":
            st.error("Please fill in your Job Preferences (this field is mandatory)!")
        else:
            # Store inputs to session_state if needed
            st.session_state.job_preference = job_preference
            st.session_state.job_count = job_count
            st.session_state.job_portal = job_portal
            st.session_state.resume = resume_file

            # Trigger job search based on selected portal
            if job_portal == "Linkedin":
                start=time.time()
                linkedin_job_searcher(job_preference, job_count,resume_file)
                end = time.time()

                st.write(f"Time taken : {round((end-start)/60,2)} minutes")

            elif job_portal == "Jobstreet":
                start=time.time()
                jobstreet_job_searcher(job_preference,job_count,resume_file)
                end = time.time()
                st.write(f"Time taken : {round((end-start)/60,2)} minutes")

            elif job_portal == "MauKerja": 
                start=time.time()
                maukerja_job_searcher(job_preference,job_count,resume_file)
                end = time.time()
                st.write(f"Time taken : {round((end-start)/60,2)} minutes")

            elif job_portal == "Glassdoor":
                start=time.time()
                glassdoor_job_searcher(job_preference,job_count,resume_file)
                end = time.time()
                st.write(f"Time taken : {round((end-start)/60,2)} minutes")
            else:
                st.info(f"Job search for {job_portal} is not implemented yet.")
    
    st.markdown('</div>', unsafe_allow_html=True)

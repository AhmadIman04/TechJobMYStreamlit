
import streamlit as st
import pandas as pd
from Functions import get_average_salary
from Functions import salary_distribution
import gspread
from google.oauth2.service_account import Credentials

st.markdown(
    """
    <h1 style="text-align: center; color: #0d6abf; font-weight: bold; font-size: 70px;">
        TechJobMY
    </h1>
    """,
    unsafe_allow_html=True
)

# Function to read data from Google Sheets into a pandas DataFrame
def read_sheet_to_df(sheet_id, sheet_name="Sheet1"):
    # Open the Google Sheet by its ID
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(sheet_name)
    
    # Get all values from the sheet
    data = worksheet.get_all_values()
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])  # Use the first row as headers
    return df

if "hasPulledData" not in st.session_state:
    with st.spinner("🔄 Loading data... Please wait a moment!"): 
        # Google Sheets API authorization
        st.session_state.hasPulledData = True
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        #creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)

        # Sheet IDs
        alljobs_df_9_id = "1UPcLy1xpT6dcxrIUDFwpHt-SmAcb5XeUlw74MAG2pns"
        skill_dim_id = "1XsmTeWNN7e5ebyd6rOUhR1LCxjEbKCcpbOqFmsFHSTM"
        skills_table3_id = "1st_vm0tSGVGFMOp7893h6cFYFq8DgbYtPoC5i4S3fVk"

        # Read data from sheets into DataFrames
        st.session_state.alljobsdf = read_sheet_to_df(alljobs_df_9_id)
        st.session_state.skill_dim = read_sheet_to_df(skill_dim_id)
        st.session_state.job_skills = read_sheet_to_df(skills_table3_id)

        # Convert empty strings to NaN
        st.session_state.alljobsdf = st.session_state.alljobsdf.replace('', pd.NA)
        st.session_state.alljobsdf.drop(columns=["Unnamed: 0"],inplace=True)
        st.session_state.skill_dim.drop(columns=["Unnamed: 0"],inplace=True)
        st.session_state.job_skills.drop(columns=["Unnamed: 0"],inplace=True)
        st.session_state.skill_dim.rename(columns={"Skill":"Skills"},inplace=True)




#alljobsdf.drop(columns=["Unnamed: 0"],inplace=True)
#skill_dim.drop(columns=["Unnamed: 0"],inplace=True)
#job_skills.drop(columns=["Unnamed: 0"],inplace=True)
#skill_dim.rename(columns={"Skill":"Skills"},inplace=True)

merged_table_skills = pd.merge(st.session_state.job_skills,st.session_state.skill_dim,how="right",on="Skills")

merged_all_table = pd.merge(st.session_state.alljobsdf,merged_table_skills,how="left",on="Job ID")

col1,col2 = st.columns(2)


with col1:
    st.session_state.Job=st.selectbox(
        "Choose Jobs",
        ['Full Stack Developer', 'Business Analyst', 'Data Scientist',
       'Backend Developer', 'Data Engineer', 'Cloud Engineer',
       'Data Analyst', 'Frontend Developer']
    )

    st.session_state.State = st.selectbox(
        "Choose State",
        ["All State","Kuala Lumpur","Selangor","Penang"]
    )

with col2:
    st.session_state.jobs_analyzed=get_average_salary(st.session_state.Job,alljobsdf=st.session_state.alljobsdf,FilterState=st.session_state.State)

st.write(" ")
st.write(" ")
st.markdown(f"<p style='text-align: center; font-size: 1.25rem;'>{st.session_state.jobs_analyzed} Jobs Analyzed</p>", unsafe_allow_html=True)
salary_distribution(st.session_state.Job,alljobsdf=st.session_state.alljobsdf,FilterState=st.session_state.State)
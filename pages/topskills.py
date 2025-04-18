import streamlit as st
import pandas as pd
from Functions import page1_vis
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components

GA_MEASUREMENT_ID = "G-BM5FK4E0W7"

ga_script = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>
"""

# Inject once
if "ga_injected" not in st.session_state:
    components.html(ga_script, height=0)
    st.session_state.ga_injected = True

st.markdown(
    """
    <h1 style="text-align: center; color: #0d6abf; font-weight: bold; font-size: 70px;">
        TechJobMY
    </h1>
    """,
    unsafe_allow_html=True
)


#alljobsdf= pd.read_csv("alljobs_df_9.csv")
#skill_dim = pd.read_csv("skill_dim.csv")
#job_skills=pd.read_csv("skills_table3.csv")




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
    success = False
    while not success:
        try:
            with st.spinner("🔄 Loading data... Please wait a moment!"):
                # Google Sheets API authorization
                scopes = ["https://www.googleapis.com/auth/spreadsheets"]
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
                st.session_state.alljobsdf.drop(columns=["Unnamed: 0"], inplace=True)
                st.session_state.skill_dim.drop(columns=["Unnamed: 0"], inplace=True)
                st.session_state.job_skills.drop(columns=["Unnamed: 0"], inplace=True)
                st.session_state.skill_dim.rename(columns={"Skill": "Skills"}, inplace=True)

                # Mark data as successfully pulled
                st.session_state.hasPulledData = True
                success = True
                

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.warning("Retrying...")

col1,col2 = st.columns(2)

with col1:
    st.session_state.Job=st.selectbox(
        "Choose Jobs",
        ['Full Stack Developer', 'Business Analyst', 'Data Scientist',
       'Backend Developer', 'Data Engineer', 'Cloud Engineer',
       'Data Analyst', 'Frontend Developer']
    )

with col2:
    st.session_state.skill_type=st.selectbox(
        "Choose Skill Type",
        ['All Skills', 'Other tools', 'Frameworks and Libraries',
        'Database', 'Cloud Service Providers','Programming Language']
    )

#alljobsdf.drop(columns=["Unnamed: 0"],inplace=True)
#skill_dim.drop(columns=["Unnamed: 0"],inplace=True)
#job_skills.drop(columns=["Unnamed: 0"],inplace=True)
#skill_dim.rename(columns={"Skill":"Skills"},inplace=True)

merged_table_skills = pd.merge(st.session_state.job_skills,st.session_state.skill_dim,how="right",on="Skills")

merged_all_table = pd.merge(st.session_state.alljobsdf,merged_table_skills,how="left",on="Job ID")

page1_vis(st.session_state.Job,st.session_state.skill_type,"All State",merged_all_table=merged_all_table)
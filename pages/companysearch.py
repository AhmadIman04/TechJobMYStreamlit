import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from Functions import company_search_vis

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




merged_table_skills = pd.merge(st.session_state.job_skills,st.session_state.skill_dim,how="right",on="Skills")

merged_all_table = pd.merge(st.session_state.alljobsdf,merged_table_skills,how="left",on="Job ID")

st.session_state.company = st.text_input("Enter company name : ")

company_search_vis(df=merged_all_table.copy(),company=st.session_state.company)
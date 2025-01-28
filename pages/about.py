import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


st.header("📚 What is TechJobMY?")

st.subheader("Empowering Malaysians in the Tech Industry")
st.write(
    "TechJobMY is a platform designed to equip Malaysians with the most relevant and up-to-date insights about the tech job market. By analyzing job postings from leading sites like Indeed, Glassdoor, and Jobstreet, we help job seekers make informed decisions on which skills to learn and avoid wasting time on outdated or underpaid roles."
)

st.header("🎯 Objective")
st.write(
    "Our mission is simple: **to guide Malaysian job seekers in the tech industry**. This web app provides crucial information about current job market trends, ensuring you don’t spend time acquiring irrelevant skills or accepting underpaid positions. Whether you're just starting or looking to level up your career, we’ve got the insights you need to succeed."
)

st.header("⚙️ Methodology")
st.write(
    "Powered by cutting-edge web scraping techniques, this app extracts job posting data from top job boards like Indeed, Glassdoor, and Jobstreet using **Selenium** and **BeautifulSoup**. We then transfer this data to **Google Sheets** via API to create insightful, easy-to-understand visualizations that provide you with clear, actionable information on the state of the tech job market."
)

st.header("🤝 How Can You Help?")
st.write(
    "Your feedback is invaluable in shaping the future of TechJobMY! **Help us improve by providing your thoughts**—just click the button below and share your insights. Together, we can make this platform even better for job seekers across Malaysia."
)




# Create the feedback form using st.form
with st.form("feedback_form"):
    feedback = st.text_area("Please enter your feedback below:")
    st.markdown(
        """
        <style>
        /* Style for the form submit button */
        .stButton > button {
            background-color: white; /* Set button background color to white */
            color: black; /* Set text color */
            border: 1px solid black; /* Optional: Add a border */
            padding: 0.5em 1em; /* Optional: Adjust padding */
            border-radius: 5px; /* Optional: Add rounded corners */
            cursor: pointer;
        }

        /* Hover effect for the button */
        .stButton > button:hover {
            background-color: #f0f0f0; /* Light grey on hover */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    submit_button = st.form_submit_button("Submit Feedback")
    if submit_button and feedback:
        # Process the feedback
        st.success("Thank you for your feedback!")
        
        # Authenticate with Google Sheets API
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)
        
        # Define the sheet ID and open the sheet
        sheet_id = "1p3943LWUSpueWqZN0tfAZg2aCem3Uyv0b0iXkDFtnUs"
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)  # Assuming the first worksheet is where feedback will be stored
        
        # Append the feedback to the sheet
        worksheet.append_row([feedback])  # Append feedback as a new row
    
    elif submit_button and not feedback:
        st.error("Please enter your feedback before submitting.")


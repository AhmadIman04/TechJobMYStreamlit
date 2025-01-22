import streamlit as st


# --- PAGE SETUP ---
Top_skills = st.Page(
    "pages/topskills.py",
    title="Top Skills",
    icon="💡",
    default=True,
)

Salary_Dashboard = st.Page(
    "pages/salarydashboard.py",
    title="Salary Demographic",
    icon="💵",
)

Skill_Search = st.Page(
    "pages/skillsearch.py",
    title="Skill Search",
    icon="🔎"
)

About_Page =st.Page(
    "pages/about.py",
    title="About",
    icon="📚"
)



#--- NAVIGATION SETUP [WITHOUT SECTIONS] ---
pg = st.navigation(pages=[Top_skills, Salary_Dashboard,Skill_Search,About_Page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
#pg = st.navigation(
 #   {
  #      "Info": [about_page],
   #     "Projects": [project_1_page, project_2_page],
    #}
#)

st.markdown(
    """
    <style>
    /* Change sidebar background color */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-top-right-radius: 15px; /* Rounded top-right corner */
        border-bottom-right-radius: 15px; /* Rounded bottom-right corner */
    }
    
    /* Change font color to white in the sidebar */
    [data-testid="stSidebar"] * {
        color: white;
    }
    
    /* Change the color of the line in the sidebar */
    [data-testid="stSidebarUserContent"]::before {
        content: '';
        display: block;
        height: 1px;
        background-color: white;  /* Set the line color to white */
        margin-bottom: 10px;  /* Optional: Adjust spacing */
    }
    </style>
    """,
    unsafe_allow_html=True
)
# --- SHARED ON ALL PAGES ---
st.sidebar.markdown("Made by [Ahmad Iman](https://www.linkedin.com/in/ahmad-iman-3b172633b/)")


# --- RUN NAVIGATION ---
pg.run()
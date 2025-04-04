import streamlit as st
import streamlit.components.v1 as components

GA_JS = """
<script>
(function() {
    var gtagScript = document.createElement('script');
    gtagScript.src = 'https://www.googletagmanager.com/gtag/js?id=G-BM5FK4E0W7';
    gtagScript.async = true;
    document.head.appendChild(gtagScript);

    var inlineScript = document.createElement('script');
    inlineScript.innerHTML = `
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-BM5FK4E0W7');
    `;
    document.head.appendChild(inlineScript);
})();
</script>
"""
if "ga_injected" not in st.session_state:
    st.markdown(GA_JS, unsafe_allow_html=True)
    st.session_state.ga_injected = True

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

Company_Search = st.Page(
    "pages/companysearch.py",
    title="Company Search",
    icon="🏢"
)

Job_Search_Assistant=st.Page(
    "pages/jobsearch_assistant.py",
    title="Job Search Assistant",
    icon="🤖"
)

About_Page =st.Page(
    "pages/about.py",
    title="About",
    icon="📚"
)



#--- NAVIGATION SETUP [WITHOUT SECTIONS] ---
pg = st.navigation(pages=[Top_skills, Salary_Dashboard,Skill_Search,Company_Search,Job_Search_Assistant,About_Page])

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
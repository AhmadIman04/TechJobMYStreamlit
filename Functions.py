import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_card import card
import re
from bs4 import BeautifulSoup
import math
import ast
import time
import re
import google.generativeai as genai
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
import requests
import random
from pypdf import PdfReader
import traceback
from scrapfly import ScrapflyClient, ScrapeConfig, ScrapeApiResponse
import json

def float_to_compact_string(value):
    # Check if the value is in thousands
    if value >= 1000:
        compact_value = value / 1000  # Convert to thousands
        # Format with up to 2 decimal places
        return f"   {compact_value:.2f}k"
    else:
        # If the value is less than 1000, return as is with 2 decimal places
        return f"   {value:.2f}"

#def get_average_salary(FilterJob,alljobsdf):
 #   df=alljobsdf.copy()
  #  df=df[df["Short Job Title"]==FilterJob]
   # df=df[df["Job Type"]!="Internship"]
    #df = df.dropna(subset=["Actual Salary"])  # Drop rows where 'Salary' is NaN, keeping other columns intact
    #jobs_analyzed = len(df)
    #avg_salary = df["Actual Salary"].mean()
    #st.write(avg_salary)
    #return jobs_analyzed

def get_skill_percentage(FilterJob, FilterSkill, merged_all_table):
    df=merged_all_table.copy()
    df=df[df["Short Job Title"]==FilterJob]
    number_of_jobs=len(df["Job ID"].unique())
    df=df[df["Skills"]==FilterSkill]
    number_of_skills_mentioned = len(df)    
    skill_mentioned_percentage = (number_of_skills_mentioned/number_of_jobs) * 100
    return round(skill_mentioned_percentage,2),number_of_jobs

def get_average_salary(FilterJob, alljobsdf,FilterState):
    df = alljobsdf.copy()
    if(FilterState != "All State"):
        df=df[df["State"]==FilterState]
    df = df[df["Short Job Title"] == FilterJob]
    df = df[df["Job Type"] != "Internship"]
    df = df[~df["Job Title"].str.contains("trainee", case=False, na=False)]
    df = df.dropna(subset=["Actual Salary"])  # Drop rows where 'Salary' is NaN, keeping other columns intact
    df["Actual Salary"] = pd.to_numeric(df["Actual Salary"], errors='coerce')
    jobs_analyzed = len(df)
    avg_salary = df["Actual Salary"].mean()

    st.markdown(
    f"""
    <div style="
        background-color: #333333;
        border-radius: 30px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        width: 300px;
        margin-left: 40px;
        text-align: center;">
        <h2 style="color: #007bff; font-size: 45px; margin: 0;">{float_to_compact_string(avg_salary)}</h2>
        <p style="color: #ffffff; font-size: 16px; margin: 0;">Average Monthly Salary</p>
    </div>
    """,
    unsafe_allow_html=True,
    )
    return jobs_analyzed



def salary_distribution(FilterJob,alljobsdf,FilterState):
    df=alljobsdf.copy()
    if(FilterState != "All State"):
        df=df[df["State"]==FilterState]
    df = df[df["Short Job Title"] == FilterJob]
    df = df[df["Job Type"] != "Internship"]
    df = df.dropna(subset=["Actual Salary"])
    df["Actual Salary"] = pd.to_numeric(df["Actual Salary"], errors='coerce')
    target_array=df["Actual Salary"]
    # Create the histogram
    fig = px.histogram(
        target_array,
        x=target_array,
        nbins=int((target_array.max() - target_array.min()) / 500),  # Set bin size to 500
        labels={"x": "Salary"},  # Label for the x-axis
        title="Histogram of Actual Salaries",
        histnorm="percent"
    )

    # Update the bar color
    fig.update_traces(marker_color="#0d6abf", marker_line_color="#0d6abf")

    # Update layout for better visuals
    fig.update_layout(
        title=dict(
            text='Salary Distribution',
            x=0.5,  # Center the title
            xanchor='center',  # Anchor the title in the center
            font=dict(size=17)  # Adjust title font size
        ),
        yaxis=dict(
            tickfont=dict(size=12),
            tickformat='.0f',
            title=None,
            showticklabels=False  # Hide x-axis labels
        ),
        bargap=0.1,  # Gap between bars
        template="simple_white",  # Light theme
    )

    # Display the histogram in Streamlit
    st.plotly_chart(
        fig, 
        config={
            'staticPlot': True,       # Disables all interactivity
            'displayModeBar': False,  # Hides the mode bar at the top of the chart
        }
        ,use_container_width=True
    )


def page1_vis(FilterJob, FilterSkill, FilterState, merged_all_table):
    df = merged_all_table.copy()
    df = df[df["Short Job Title"] == FilterJob]
    number_of_jobs = len(df["Job ID"].unique())
    
    if FilterState != "All State":
        df = df[df["State"] == FilterState]
    if FilterSkill != "All Skills":
        df = df[df["Skill Type"] == FilterSkill]
    
    
    skills_count = (
        df.groupby('Skills')
        .size()
        .reset_index(name='Skill Count')
    )
    
    skill_percentage = []
    for i in range(len(skills_count)):
        skill_percentage.append(skills_count["Skill Count"].iloc[i] / number_of_jobs)
    
    skills_count["Skill Percentage"] = skill_percentage
    skills_count_sorted = skills_count.sort_values(by='Skill Count', ascending=False)

    # Select the top 20 rows
    top_20_skills = skills_count_sorted.head(20)

    st.write(" ")
    st.markdown(f"<p style='text-align: center; font-size: 1.25rem;'>{number_of_jobs} Jobs Analyzed</p>", unsafe_allow_html=True)
    
    # Create a horizontal bar chart with Plotly Express
    fig = px.bar(
        top_20_skills,
        x='Skill Percentage',
        y='Skills',
        orientation='h',
        title=f'{number_of_jobs} Jobs Analyzed',
        text='Skill Percentage',
        labels={'Skill Percentage': 'Skill Mentioned Percentage','Skills':" "},
        color='Skill Percentage',  # Use 'Skill Count' to control the bar color
        color_continuous_scale=["#deefff","#0d6abf"]
    )

    # Format the text as percentage
    fig.update_traces(texttemplate='%{text:.2%}', textposition='outside', textfont=dict(size=12),marker=dict(showscale=False))

    # Customize the layout for the y-axis font size
    fig.update_layout(
        title=dict(
            text=f'Top Skills For {FilterJob}',
            x=0.5,  # Center the title
            xanchor='center',  # Anchor the title in the center
            font=dict(size=17)  # Adjust title font size
        ),
        coloraxis_showscale=False,
        xaxis=dict(
            tickfont=dict(size=12),
            showticklabels=False  # Hide x-axis labels
        ),  # X-axis tick font size
        yaxis=dict(
            categoryorder='total ascending'  # Sort the y-axis in descending order based on count
        ),
        font=dict(size=12),
        height=600
    )

    st.plotly_chart(
        fig, 
        config={
            'staticPlot': True,       # Disables all interactivity
            'displayModeBar': False,  # Hides the mode bar at the top of the chart
        }
    )
def print_arr(arr):
    arr_str = ""
    for i in arr:
        arr_str = f"{arr_str}{i},"  # Append the element followed by a comma
    return arr_str.rstrip(',')  # Remove the trailing comma

def company_search_vis(df,company):
    if(company==""):
        return
    word =company
    word=word.lower()
    df_A= df[(df["Company Name"].str.contains(f"{word}", case=False, na=False)) | (df["Company Name"].str.lower()==word)]
    companies = df["Company Name"]
    companies_withspace = []
    for i in companies :
        new_word = f" {i}"
        new_word = re.sub(r'[^a-zA-Z0-9\s]', ' ', new_word)
        companies_withspace.append(new_word)
    df["Company Name"]=companies_withspace
    word = f" {word}"
    word=word.lower()
    df_B = df[(df["Company Name"].str.contains(f"{word} ", case=False, na=False)) | (df["Company Name"].str.lower()==word)]
    if(len(df_B)==0):
        with st.container(border=True):
            st.warning("Company is not available in the database")
            return
    df_B.dropna(subset=["Skills"],inplace=True)
    list_company = print_arr(pd.Series(df_B['Company Name'].str.lower().unique()).str.title())

    # Create HTML string where only the company names are bold
    html_str = f"""
    <style>
        .bold {{
            font-weight: bold;
        }}
    </style>
    <p>Showing results for <span class="bold">{list_company}</span></p>
    """
    st.markdown(html_str, unsafe_allow_html=True)
    with st.container(border=True):
        
        # Group jobs and their skills
        jobs = df_B["Short Job Title"].unique()
        for i in jobs:
            # Filter the DataFrame for the current job title
            df_temp = df_B[df_B["Short Job Title"] == i]
            list_of_jobs = df_temp["Skills"].unique()
            
            # Convert the list of skills into a comma-separated string
            skills_str = ", ".join(list_of_jobs)
            
            # Display the job title
            st.markdown(f"### 🛠️ **{i}**")
            
            # Display the skills in a visually appealing way
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; padding: 10px; border-radius: 10px; margin-bottom: 10px; color: #333; font-size: 16px;">
                    <strong>Skills mentioned for this role:</strong><br>
                    <span style="color: #007BFF;">{skills_str}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.divider()  # Add a horizontal line for better separation
    st.write(" ")
    st.markdown('**Raw Data** (to look at the data by yourself, you can download this csv file)')
    df_B = df_B[['Job Title', 'Company Name', 'Location', 'Job Requirements']]
    # Eliminate duplicate rows based on the selected columns
    df_B = df_B.drop_duplicates()

    st.dataframe(df_B)
        

def is_code_safe(code: str) -> bool:
    FORBIDDEN_NAMES = {"os", "sys", "subprocess", "shutil", "__import__"}
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print("Syntax error in code:", e)
        return False

    for node in ast.walk(tree):
        # Check for dangerous imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            if any(name.split('.')[0] in FORBIDDEN_NAMES for name in names):
                print(f"Found forbidden import in code: {names}")
                return False

        # Check for dangerous function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "__import__"}:
                print(f"Found dangerous function call: {node.func.id}")
                return False

    return True

#################################### Linkedin Scraping #######################################

def build_public_url(keywords, experience=None, company=None, location=None, job_type=None, originalSubdomain="my"):
    """
    Build a public LinkedIn jobs URL with filters for keywords, experience, company, location, and job type.

    Args:
        keywords (str): Job keywords.
        experience (str or list, optional): Experience filter (e.g. "2" or ["2", "3"]).
        company (str or list, optional): Company filter (e.g. company ID or name; depends on LinkedIn’s parameter).
        location (str, optional): Location filter.
        job_type (str or list, optional): Job type filter; this will be added as f_WT.
        originalSubdomain (str): The subdomain (e.g. "my" for Malaysia).

    Returns:
        str: The public URL with query parameters.
    """
    base_url = "https://www.linkedin.com/jobs/search/"
    params = {
        "keywords": keywords,
        "origin": "JOB_SEARCH_PAGE_JOB_FILTER",
        "originalSubdomain": originalSubdomain
    }
    if location:
        params["location"] = location
    if experience:
        # f_E is the parameter for experience level; it can be a list or a single value.
        params["f_E"] = experience
    if company:
        # f_C is the parameter for company filter.
        params["f_C"] = company
    if job_type:
        # f_WT is the parameter for job type filter.
        params["f_WT"] = job_type

    query_string = urllib.parse.urlencode(params, doseq=True)
    public_url = f"{base_url}?{query_string}"
    return public_url

def convert_public_to_api(public_url, start=0):
    """
    Convert a public LinkedIn jobs URL (with filters) into an API endpoint URL.

    This function now extracts filtering parameters (like f_E, f_C, and f_WT) from the public URL
    and appends them to the API URL.

    Args:
        public_url (str): The public-facing LinkedIn jobs URL.
        start (int): The starting index for pagination.

    Returns:
        str: Constructed API endpoint URL with filters.
    """
    # Parse the public URL and query string
    parsed_url = urllib.parse.urlparse(public_url)
    qs = urllib.parse.parse_qs(parsed_url.query)

    # Use the "keywords" query parameter (fallback if path doesn't have a "-jobs" segment)
    keyword = qs.get("keywords", [""])[0]

    # Extract filtering parameters if present
    experience = qs.get("f_E", None)  # experience filter (could be a list)
    company = qs.get("f_C", None)     # company filter (could be a list)
    job_type = qs.get("f_WT", None)     # job type filter (could be a list)

    # Use "location" if present in query parameters
    location = qs.get("location", [None])[0]
    if not location:
        # Fallback: use originalSubdomain mapping if location is not provided
        original_subdomain = qs.get('originalSubdomain', [None])[0]
        subdomain_to_location = {
            'my': 'Malaysia',
            # Add more mappings as needed.
        }
        location = subdomain_to_location.get(original_subdomain, '')

    # Extract currentJobId (if available)
    current_job_id = qs.get('currentJobId', [None])[0]

    # Set geoId to a placeholder (adjust if you have a mapping)
    geo_id = 0

    # Construct the API endpoint URL.
    base_api_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
    params = {
        'keywords': keyword,
        'location': location,
        'geoId': geo_id,
        'currentJobId': current_job_id,
        'start': start
    }
    # Append filtering parameters if they exist.
    if experience:
        params['f_E'] = experience
    if company:
        params['f_C'] = company
    if job_type:
        params['f_WT'] = job_type

    api_url = f"{base_api_url}?{urllib.parse.urlencode(params, doseq=True)}"
    return api_url


def linkedin_job_searcher(job_description,total_jobs, resume = None):
    try:
        with st.spinner("🔄Searching jobs based on your prescriptions, please wait...."):
            key = st.secrets["api_keys"]["gemini_1"]
            if resume == None :
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description: {job_description}
                '''
                )
            else:
                reader = PdfReader(resume)
                text = ""
                # Loop through all pages and extract text
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description(summarize it): {job_description}

                From the resume texts, summarise all skills and necessary experience that this candidate have
                resume texts :{text}

                your output should be like this:

                Resume information:
                .....

                Job Preferences:
                .......


                '''
                )
            #
            print(candidate_preferences.text)
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response2 = model.generate_content(
            f'''
            ok now based on the job preferences (not the resume details) right here
            Job description : {job_description},
            i want you to fill out this python code right here, here the job description should be an input from the user, if you think that the user is currently trolling by entering ridiculous inputs, just throw an exception
            python code :
            keywords = #Here put out the job title like "data analytics" or "Cybersecurity" DO NOT include experience like "sofware engineer intern" or "Data science intern",only put one job title dont put more than one, if the request has more than one job just choose one
            experience =   # for internship put "1" for entry level put "2" for Associate level put "3" for Mid-senior level put "4", for director put 5 for executive put 6, if no experience is mentioned put "0"
            company = None    # If the text specify a company name, put it here, if not put None
            location = "Malaysia"  # If the text specify a location, put it here, if not put Malaysia
            job_type = #for job type, put "1" for on-site jobs, put "2" for Remote jobs, , and put "3" for hybrid jobs, if it didnt specify just put "1"

            if the job description is ridiculuos, execute this python code :
            raise Exception("This is an error message")

            after filling out this python code, i want you to just return the code and NOTHING ELSE
            '''
            )

            print(response2.text)

            code = response2.text
            # Remove code block markers
            code = re.sub(r'```python', '', code)
            code = re.sub(r'```', '', code)

            # Remove any leading/trailing whitespace (including newlines)
            exec_globals = {}
            code = code.strip()
            if is_code_safe(code):
                exec(code, exec_globals)
                keywords   = exec_globals.get('keywords')
                experience = exec_globals.get('experience')
                company    = exec_globals.get('company')
                location   = exec_globals.get('location')
                job_type   = exec_globals.get('job_type')
            else:
                print("The code contains potentially dangerous operations and will not be executed.")
            # -------------------------------
            # Example usage:
            # -------------------------------

            # Define your filter parameters
            #keywords = "data scientist"
            #experience = "2"  # For example, "2" might denote a specific experience level.
            #company = None    # Replace with a company ID or list if needed.
            #location = "Malaysia"  # You can also try "Kuala Lumpur" or any valid location.
            #job_type = "F"  # For example, "F" might represent Full-Time jobs; adjust based on LinkedIn's parameters.
            original_subdomain = "my"  # 'my' corresponds to Malaysia

            # Build the public URL using your filters
            public_url = build_public_url(keywords, experience=experience, company=company, location=location, job_type=job_type, originalSubdomain=original_subdomain)
            print("Using Public URL:", public_url)

            # Convert the public URL to an API URL (for the first page, start=0)
            target_url = convert_public_to_api(public_url, start=0)
            print("Using API URL:", target_url)

            # Initialize lists to store job data
            jobs_list = []  # To store job IDs and their posting links
            jobs_data = []  # To store detailed job info
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
            }

            # Replace total_jobs with the actual number of jobs you expect.
            # You can also implement logic to detect when no more jobs are returned.
            # Example value; replace with actual job count

            # Loop through pages (here we assume 10 jobs per page; adjust if needed)
            for i in range(0, math.ceil(total_jobs / 10)):
                time.sleep(1.5)
                # Update the API URL for pagination by replacing the "start" parameter
                page_url = target_url.replace("start=0", f"start={i}")
                res = requests.get(page_url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                alljobs_on_this_page = soup.find_all("li")
                print(f"Page {i}: Found {len(alljobs_on_this_page)} jobs")

                # Extract job IDs and the public link for each job listing
                for job_li in alljobs_on_this_page:
                    try:
                        # Extract job ID from the data-entity-urn attribute
                        div_card = job_li.find("div", {"class": "base-card"})
                        job_id = div_card.get('data-entity-urn').split(":")[3]
                        # Extract the job posting link from the <a> tag
                        job_link = job_li.find("a", {"class": "base-card__full-link"}).get("href")
                        jobs_list.append({"job_id": job_id, "link": job_link})
                    except Exception as e:
                        print("Error extracting job info:", e)

            # Now, for each job, fetch detailed job information using the API endpoint
            # and scrape the full job description from the public link.
            job_detail_api = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'
            for job in jobs_list:
                job_id = job["job_id"]
                # Fetch job details from the API endpoint
                resp = requests.get(job_detail_api.format(job_id), headers=headers)
                soup = BeautifulSoup(resp.text, 'html.parser')
                job_info = {}

                try:
                    job_info["company"] = soup.find("div", {"class": "top-card-layout__card"}).find("a").find("img").get('alt')
                except:
                    job_info["company"] = None

                try:
                    job_info["job-title"] = soup.find("div", {"class": "top-card-layout__entity-info"}).find("a").text.strip()
                except:
                    job_info["job-title"] = None

                try:
                    job_info["level"] = soup.find("ul", {"class": "description__job-criteria-list"}).find("li").text.replace("Seniority level", "").strip()
                except:
                    job_info["level"] = None

                # Add the public job posting link to the job info
                job_info["link"] = job["link"]

                # Make a request to the public job posting page to scrape the job description
                try:
                    time.sleep(1.5)
                    public_resp = requests.get(job["link"], headers=headers)
                    public_soup = BeautifulSoup(public_resp.text, 'html.parser')
                    # Locate the section containing the job description
                    description_section = public_soup.find("section", class_="show-more-less-html")
                    if description_section:
                        markup_div = description_section.find("div", class_="show-more-less-html__markup")
                        if markup_div:
                            job_description = markup_div.get_text(separator="\n").strip()
                        else:
                            job_description = None
                    else:
                        job_description = None
                except Exception as e:
                    print("Error extracting job description for job_id", job_id, e)
                    job_description = None

                job_info["job_description"] = job_description

                jobs_data.append(job_info)

            # Save the results to a CSV file
            df = pd.DataFrame(jobs_data)

            df = df.head(total_jobs)
            # df.to_csv('linkedinjobs.csv', index=False, encoding='utf-8')
            print("Scraped job data:")
            st.subheader("Scraped Jobs :")
            st.dataframe(df)
            # Configure the Gemini API

        with st.spinner("⌛ Filtering jobs that are compatible for you, please wait...."):
            key1=st.secrets["api_keys"]["gemini_1"]
            key2=st.secrets["api_keys"]["gemini_2"]
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            # Assume df and candidate_preferences have already been defined/loaded.
            # For example:
            # df = pd.read_csv('linkedinjobs.csv')
            # candidate_preferences = "..."  # your candidate profile string
            compatible_jobs = []   # List to store rows deemed compatible
            incompatible_jobs = [] # List to store rows deemed not compatible

            # Iterate through each job entry in the DataFrame
            for idx, row in df.iterrows():

                
                if idx%2 == 0:
                    key=key1
                else:
                    key=key2
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                #time.sleep(1.5)
                job_desc = row.get("job_description", "")
                
                # Skip jobs with missing or empty descriptions
                if pd.isna(job_desc) or not job_desc.strip():
                    row = row.copy()
                    row["reason"] = "Job description missing."
                    incompatible_jobs.append(row)
                    continue

                # Adjusted prompt: include an example for clarity.
                prompt = f"""
            Candidate Profile:
            {candidate_preferences.text}

            Job Description:
            {job_desc}

            Based on the above, is this job compatible with the candidate's preferences? 
            Please answer with either "yes" or "no" followed by a brief explanation.
            For example: "yes, because the role matches the candidate's skills in data analytics."
            """
                # Call the Gemini API with the prompt
                response = model.generate_content(prompt)
                answer = response.text.strip()
                answer_lower = answer.lower()
                
                # Extract the explanation if available (assumes response in format "yes, because ..." or "no, because ...")
                if "," in answer:
                    reason = answer.split(",", 1)[1].strip()
                else:
                    reason = "No explanation provided."

                row = row.copy()
                row["reason"] = reason

                if answer_lower.startswith("yes"):
                    compatible_jobs.append(row)
                else:
                    incompatible_jobs.append(row)

            # Create DataFrames for the compatible and incompatible jobs
            df_compatible = pd.DataFrame(compatible_jobs)
            df_incompatible = pd.DataFrame(incompatible_jobs)
            st.markdown("---")

            st.subheader("Compatible jobs:")
            st.dataframe(df_compatible)

            st.subheader("Incompatible jobs:")
            st.dataframe(df_incompatible)
    except:
        st.error("Failed to fetch jobs, please try again")


#########################################JobStreet Scraping####################################################
def scrape_job_links(job_title, target_count,salary, location=None):
    """
    Scrape job links from JobStreet for the specified job title until target_count links are collected.
    
    Parameters:
        job_title (str): The job title to search for (e.g. "data science"). Spaces will be replaced with hyphens.
        target_count (int): The total number of job links to scrape.
        location (str, optional): The location filter (e.g. "Kuala Lumpur"). Spaces will be replaced with hyphens.
        
    Returns:
        List[str]: A list of job link URLs.
    """
    job_links = []
    page_num = 1
    base_url = "https://my.jobstreet.com"
    
    # Prepare job title for URL: lowercase and replace spaces with hyphens
    job_title_url = job_title.strip().lower().replace(" ", "-")
    
    # If location is provided, prepare it for the URL as well
    if location:
        location_url = location.strip().replace(" ", "-")
    
    # Loop until we have enough links or no more pages are found
    while len(job_links) < target_count:
        time.sleep(1)
        # Build URL based on whether a location filter is applied
        if location:
            url = f"{base_url}/{job_title_url}-jobs/in-{location_url}?page={page_num}&salaryrange={salary}&salarytype=monthly"
        else:
            url = f"{base_url}/{job_title_url}-jobs?page={page_num}&salaryrange={salary}&salarytype=monthly"
            
        #print(f"Scraping page {page_num}: {url}")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_num}. Status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all divs with the specified class pattern
        div_elements = soup.select("div.gepq850.eihuid4z.eihuid4x")
        
        # If no job listings are found, exit the loop
        if not div_elements:
            print(f"No more job listings found on page {page_num}.")
            break
        
        for div in div_elements:
            a_tag = div.find('a')
            if a_tag and a_tag.has_attr('href'):
                link = a_tag['href']
                # Prepend base_url if the link is relative
                if link.startswith('/'):
                    link = base_url + link
                # Avoid duplicates
                if link not in job_links:
                    job_links.append(link)
                    if len(job_links) >= target_count:
                        break
        
        page_num += 1
        # Optional: delay between page requests to be polite
        time.sleep(random.uniform(1, 2))
    
    return job_links

def scrape_job_details(link):
    """
    Scrape job details from a job link, extracting the job title, company name, location, and job description.
    
    Parameters:
        link (str): The URL of the job detail page.
        
    Returns:
        tuple: (job_title, company_name, location, job_description) or (None, None, None, None) if extraction fails.
    """
    response = requests.get(link)
    if response.status_code != 200:
        print(f"Failed to retrieve job details from {link}")
        return None, None, None, None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract job title
    title_elem = soup.find("h1", {"data-automation": "job-detail-title"})
    job_title = title_elem.get_text(strip=True) if title_elem else None
    
    # Extract company name
    company_elem = soup.find("span", {"data-automation": "advertiser-name"})
    company_name = company_elem.get_text(strip=True) if company_elem else None
    
    # Extract location
    #location_elem = soup.select_one("a._1ilznw00")
    #location = location_elem.get_text(strip=True) if location_elem else None
    location_span = soup.find('span', {'data-automation': 'job-detail-location'})
    if location_span:
        a_tag = location_span.find('a')
        if a_tag:
            location_text = a_tag.get_text(strip=True)
        else:
            # No <a> tag, so use the span's text directly
            location_text = location_span.get_text(strip=True)
        location = location_text.split(',')[0].strip()
    else:
        location = ""

    
    # Extract job description using the container with data-automation attribute
    description_elem = soup.select_one('div[data-automation="jobAdDetails"] div.gepq850._1iptfqa0')
    if description_elem:
        job_description = description_elem.get_text(separator=" ", strip=True)
    else:
        job_description = None
    
    return job_title, company_name, location, job_description


def jobstreet_job_searcher(job_description,number_of_jobs,resume=None):
    try:
        with st.spinner("🔄Searching jobs based on your prescriptions, please wait...."):
            key = st.secrets["api_keys"]["gemini_1"]
            if resume == None :
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description: {job_description}
                '''
                )
            else:
                reader = PdfReader(resume)
                text = ""
                # Loop through all pages and extract text
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description(summarize it): {job_description}

                From the resume texts, summarise all skills and necessary experience that this candidate have
                resume texts :{text}

                your output should be like this:

                Resume information:
                .....

                Job Preferences:
                .......


                '''
                )
                
            print(candidate_preferences.text)
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response2 = model.generate_content(
            f'''
            ok now based on the job preferences (not the resume details) right here
            {job_description},
            i want you to fill out this python code right here
            python code :
            job_title_input = #Here put out the job title like data analytics, only put one job title dont put more than one, if the request has more than one job just choose one
            location = "Malaysia"  # If the text specify a location, put it here, if not put Malaysia
            salary =  #if the text specify a monthly salary, put it here, if not just put 0
            after filling out this python code, i want you to just return the code and NOTHING ELSE
                        '''
            )

            print(response2.text)

            code = response2.text
            # Remove code block markers
            code = re.sub(r'```python', '', code)
            code = re.sub(r'```', '', code)

            # Remove any leading/trailing whitespace (including newlines)
            exec_globals = {}
            code = code.strip()
            if is_code_safe(code):
                exec(code, exec_globals)
                job_title_input = exec_globals.get('job_title_input')
                location   = exec_globals.get('location')
                salary   = exec_globals.get('salary')
            else:
                print("The code contains potentially dangerous operations and will not be executed.")

              # Step 1: Scrape job links for the given job title and target count

            links = scrape_job_links(job_title_input, number_of_jobs,salary, location)

            # Create a DataFrame from the collected links
            df_links = pd.DataFrame(links, columns=["link"])
            #print("\nCollected job links:")
            #print(df_links.head())

            # Step 2: Iterate through the links and scrape job details
            job_details = []
            for link in df_links["link"]:
                #print(f"Scraping details from {link}")
                title, company, location, description = scrape_job_details(link)
                job_details.append({
                    "job_title": title,
                    "company_name": company,
                    "location": location,
                    "link": link,
                    "job_description": description
                })
                # Optional: delay between job detail requests to avoid overwhelming the server
                time.sleep(1)

            # Create a DataFrame with the job details
            df_jobs = pd.DataFrame(job_details)
            df_jobs = df_jobs[["company_name","job_title", "location", "link", "job_description"]]
            df_jobs = df_jobs.head(number_of_jobs)
            st.subheader("Scraped Jobs : ")
            st.dataframe(df_jobs)
        
        with st.spinner("⌛ Filtering jobs that are compatible for you, please wait...."):
            key1=st.secrets["api_keys"]["gemini_1"]
            key2=st.secrets["api_keys"]["gemini_2"]
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            # Assume df and candidate_preferences have already been defined/loaded.
            # For example:
            # df = pd.read_csv('linkedinjobs.csv')
            # candidate_preferences = "..."  # your candidate profile string
            compatible_jobs = []   # List to store rows deemed compatible
            incompatible_jobs = [] # List to store rows deemed not compatible

            # Iterate through each job entry in the DataFrame
            for idx, row in df_jobs.iterrows():
                if idx%2 == 0:
                    key=key1
                else:
                    key=key2
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                #time.sleep(1.5)
                job_desc = row.get("job_description", "")
                
                # Skip jobs with missing or empty descriptions
                if pd.isna(job_desc) or not job_desc.strip():
                    row = row.copy()
                    row["reason"] = "Job description missing."
                    incompatible_jobs.append(row)
                    continue

                # Adjusted prompt: include an example for clarity.
                prompt = f"""
                Candidate Profile:
                {candidate_preferences.text}

                Job Description:
                {job_desc}

                Based on the above, is this job compatible with the candidate's preferences? 
                Please answer with either "yes" or "no" followed by a brief explanation.
                For example: "yes, because the role matches the candidate's skills in data analytics."
                """
                # Call the Gemini API with the prompt
                response = model.generate_content(prompt)
                answer = response.text.strip()
                answer_lower = answer.lower()
                
                # Extract the explanation if available (assumes response in format "yes, because ..." or "no, because ...")
                if "," in answer:
                    reason = answer.split(",", 1)[1].strip()
                else:
                    reason = "No explanation provided."

                row = row.copy()
                row["reason"] = reason

                if answer_lower.startswith("yes"):
                    compatible_jobs.append(row)
                else:
                    incompatible_jobs.append(row)

            # Create DataFrames for the compatible and incompatible jobs
            df_compatible = pd.DataFrame(compatible_jobs)
            df_incompatible = pd.DataFrame(incompatible_jobs)
            st.markdown("---")

            st.subheader("Compatible jobs:")
            st.dataframe(df_compatible)

            st.subheader("Incompatible jobs:")
            st.dataframe(df_incompatible)
    except:
        error_trace = traceback.format_exc()  # Get the full traceback as a string
        st.error("Failed to fetch jobs, please try again")
        print(f"Error details:\n{error_trace}")


################################### MauKerja Scraping #####################################################
def scrape_job_links_maukerja(job_name, location, limit, salary=None, jtype=None):
    """
    Scrape job posting links from Maukerja for the specified job name and location,
    paginating if needed until the number of collected links meets the limit.
    
    Parameters:
        job_name (str): The job name to search for (e.g., "data scientist").
        location (str): The location for the job search (e.g., "Kuala Lumpur").
        limit (int): The maximum number of job links to scrape.
        salary (int, optional): The minimum salary filter value. If provided, the URL will include
                                a salary filter (with currency fixed as MYR).
        jtype (str, optional): The job type filter (e.g., "1-Internship"). If provided, the URL
                               will include the job type filter.
        
    Returns:
        list: A list of job posting links.
    """
    # Convert inputs to URL-friendly format
    job_name_url = job_name.strip().lower().replace(" ", "-")
    location_url = location.strip().lower().replace(" ", "-")
    
    # Build the base URL for the search results
    base_url = f"https://www.maukerja.my/jobsearch/{job_name_url}-jobs-in-{location_url}"
    
    # Construct query parameters based on optional filters
    query_params = []
    if salary:
        query_params.append(f"sal={salary}")
        query_params.append("currency=MYR")
    if jtype:
        query_params.append(f"jtype={jtype}")
    query_params.append("sortBy=relevance")
    
    query_string = "?" + "&".join(query_params)
    full_url = base_url + query_string
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    
    job_links = []
    page_num = 1
    prev_anchors = None

    while len(job_links) < limit:
        # For page 1, use the full URL; for subsequent pages, append &page=
        page_url = full_url if page_num == 1 else f"{full_url}&page={page_num}"
        print("Scraping page:", page_url)
        response = requests.get(page_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_num}.")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract all <a> tags that have the attribute data-v-2776546c
        anchors = soup.find_all("a", attrs={"data-v-2776546c": True})
        
        # Break if no anchors or if the current anchors are identical to the previous page's anchors
        if not anchors or (prev_anchors is not None and anchors == prev_anchors):
            print(f"No more job postings found on page {page_num}. Ending pagination.")
            break
        
        prev_anchors = anchors
        
        for a in anchors:
            href = a.get("href")
            if href and href.startswith('/'):
                href = "https://www.maukerja.my" + href
                if href not in job_links:
                    job_links.append(href)
                    if len(job_links) >= limit:
                        break

        page_num += 1
        time.sleep(random.uniform(1, 2))
    
    return job_links

def extract_job_details(job_links):
    """
    Extract job details (title, company, location, and description) from each job posting link.
    
    Parameters:
        job_links (list): List of job posting URLs.
        
    Returns:
        pd.DataFrame: DataFrame containing job details with columns for job title, company, location,
                      job description, and link.
    """
    job_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    for link in job_links:
        response = requests.get(link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve job posting: {link}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract Job Title from an <h2> with class "font-bold is-6"
        title_element = soup.find("h2", class_="font-bold is-6")
        job_title = title_element.get_text(strip=True) if title_element else "N/A"

        # Extract Company Name from an <h2> whose id starts with "companyName-id"
        company_element = soup.select_one("h2[id^='companyName-id']")
        company_name = company_element.get_text(strip=True) if company_element else "N/A"

        # Extract Location from the <div> with class "job-location"
        location_element = soup.find("div", class_="job-location")
        job_location = location_element.get_text(separator=" ", strip=True) if location_element else "N/A"

        # Extract Job Description from the <div> with class "responsibilities"
        description_element = soup.find("div", class_="responsibilities")
        job_description = description_element.get_text(separator=" ", strip=True) if description_element else "N/A"

        job_data.append({
            "Job Title": job_title,
            "Company": company_name,
            "Location": job_location,
            "Job Description": job_description,
            "Link": link
        })

        time.sleep(random.uniform(1, 2))
    
    return pd.DataFrame(job_data)

def maukerja_job_searcher(job_description, limit, resume=None):
    try:
        with st.spinner("🔄Searching jobs based on your prescriptions, please wait...."):
            key = st.secrets["api_keys"]["gemini_1"]
            if resume == None :
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description: {job_description}
                '''
                )
            else:
                reader = PdfReader(resume)
                text = ""
                # Loop through all pages and extract text
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description(summarize it): {job_description}

                From the resume texts, summarise all skills and necessary experience that this candidate have
                resume texts :{text}

                your output should be like this:

                Resume information:
                .....

                Job Preferences:
                .......


                '''
                )
                
            print(candidate_preferences.text)
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response2 = model.generate_content(
            f'''
            ok now based on the job preferences (not the resume details) right here
            {job_description},
            i want you to fill out this python code right here
            python code :
            job_name = #Here put out the job title like "data analytics" or "Cybersecurity" DO NOT include experience like "sofware engineer intern" or "Data science intern"
            jtype =   # This variable is for job type ,for internship put "1-Internship" for Full Time put "1-Full-Time" for Part time put "1-Part-Time", if they didnt specify just put None
            salary = None    # If the text specify a salary(just put a value like 5000 and dont put a range), put it here, if not put None
            location =    # If the text specify a location, put it here, if not put Kuala Lumpur
            after filling out this python code, i want you to just return the code and NOTHING ELSE
                        '''
            )

            print(response2.text)

            code = response2.text
            # Remove code block markers
            code = re.sub(r'```python', '', code)
            code = re.sub(r'```', '', code)

            # Remove any leading/trailing whitespace (including newlines)
            exec_globals = {}
            code = code.strip()
            if is_code_safe(code):
                exec(code, exec_globals)
                job_name = exec_globals.get('job_name')
                jtype = exec_globals.get('jtype')
                location   = exec_globals.get('location')
                salary   = exec_globals.get('salary')
            else:
                print("The code contains potentially dangerous operations and will not be executed.")

            # Step 1: Scrape the job posting links based on job name, location, and optional filters.
            job_links = scrape_job_links_maukerja(job_name, location, limit, salary=salary, jtype=jtype)

            # Step 2: Iterate through the links to extract job details and store them in a DataFrame.
            job_df = extract_job_details(job_links)
            job_df = job_df.head(limit)
            st.subheader("Scraped Job Data:")
            st.dataframe(job_df)

            with st.spinner("⌛ Filtering jobs that are compatible for you, please wait...."):
                key1=st.secrets["api_keys"]["gemini_1"]
                key2=st.secrets["api_keys"]["gemini_2"]
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                # Assume df and candidate_preferences have already been defined/loaded.
                # For example:
                # df = pd.read_csv('linkedinjobs.csv')
                # candidate_preferences = "..."  # your candidate profile string
                compatible_jobs = []   # List to store rows deemed compatible
                incompatible_jobs = [] # List to store rows deemed not compatible

                # Iterate through each job entry in the DataFrame
                for idx, row in job_df.iterrows():

                    
                    if idx%2 == 0:
                        key=key1
                    else:
                        key=key2
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                    #time.sleep(1.5)
                    job_desc = row.get("Job Description", "")
                    
                    # Skip jobs with missing or empty descriptions
                    if pd.isna(job_desc) or not job_desc.strip():
                        row = row.copy()
                        row["reason"] = "Job description missing."
                        incompatible_jobs.append(row)
                        continue

                    # Adjusted prompt: include an example for clarity.
                    prompt = f"""
                    Candidate Profile:
                    {candidate_preferences.text}

                    Job Description:
                    {job_desc}

                    Based on the above, is this job compatible with the candidate's preferences? 
                    Please answer with either "yes" or "no" followed by a brief explanation.
                    For example: "yes, because the role matches the candidate's skills in data analytics."
                    """
                    # Call the Gemini API with the prompt
                    response = model.generate_content(prompt)
                    answer = response.text.strip()
                    answer_lower = answer.lower()
                    
                    # Extract the explanation if available (assumes response in format "yes, because ..." or "no, because ...")
                    if "," in answer:
                        reason = answer.split(",", 1)[1].strip()
                    else:
                        reason = "No explanation provided."

                    row = row.copy()
                    row["reason"] = reason

                    if answer_lower.startswith("yes"):
                        compatible_jobs.append(row)
                    else:
                        incompatible_jobs.append(row)

                # Create DataFrames for the compatible and incompatible jobs
                df_compatible = pd.DataFrame(compatible_jobs)
                df_incompatible = pd.DataFrame(incompatible_jobs)
                st.markdown("---")

                st.subheader("Compatible jobs:")
                st.dataframe(df_compatible)

                st.subheader("Incompatible jobs:")
                st.dataframe(df_incompatible)
    except:
        error_trace = traceback.format_exc()  # Get the full traceback as a string
        st.error("Failed to fetch jobs, please try again")
        print(f"Error details:\n{error_trace}")
            
############################### glassdoor scraping ######################################3

def get_loc_id(location):
    scrapfly = ScrapflyClient(key=st.secrets["api_keys"]["SCRAPFLY_API_KEY"])
    result = ScrapeApiResponse = scrapfly.scrape(ScrapeConfig(
            tags=[
            "player","project:default"
            ],
            asp=True,
            render_js=True,
            url=f"https://www.glassdoor.com/autocomplete/location?locationTypeFilters=CITY,STATE,COUNTRY&caller=jobs&term={location}"
    ))

    content = result.scrape_result['content']
    return json.loads(content)[0]['id'], json.loads(content)[0]['locationType']

def url_maker(location, job):
    loc_id, loc_type = get_loc_id(location)
    loc_idx = len(location)
    job_idx = len(job) + loc_idx + 1

    location = location.replace(' ', '-')
    job = job.replace(' ', '-')

    url = f"https://www.glassdoor.com/Job/{location}-{job}-jobs-SRCH_IL.0,{loc_idx}_I{loc_type}{loc_id}_KO{loc_idx+1},{job_idx}.htm"

    part = re.search(r"IL\.\d+,\d+_I{}\d+_KO\d+,\d+\.htm".format(loc_type), url).group()

    return url

def url_info(url):
    if "IN" in url:
        loc_type = "N"
    elif "IS" in url:
        loc_type = "S"
    elif "IC" in url:
        loc_type = "C"

    part = re.search(r"IL\.\d+,\d+_I{}\d+_KO\d+,\d+\.htm".format(loc_type), url).group()
    loc_id = re.search(r"I{}(\d+)".format(loc_type), url).group(1)

    return part, int(loc_id)

def get_job(numjob, url, job):
    backurl, locId = url_info(url)

    # Define the target URL
    url = "https://www.glassdoor.com/graph"

    # Headers (Extracted from the browser)
    headers = {
        "authority": "www.glassdoor.com",
        "method": "POST",
        "path": "/graph",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "apollographql-client-name": "job-search-next",
        "apollographql-client-version": "7.159.3",
        "content-type": "application/json",
        "origin": "https://www.glassdoor.com",
        "referer": "https://www.glassdoor.com/",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "gd-csrf-token": "9JSlDvTDYjTwUHEm6r0b1g:5vOHgzELRw11YvSwM8iK9lUBFiwzH6yIelVHKxEIPwRNwO1OUr6RP2PSs_mr40K3fmxnvrs_Z11W_VxgHKeG3A:2bUz66GUh_JMK-oOdjv16HvUeriVeHjsuuoQVpPU1ng",  # Replace with actual CSRF token
        "cookie": """gdId=a9d66fe3-4026-405b-b1b2-4f150f5964fa; uc=8013A8318C98C5175B5209E39BEB897033A6F39CF905396DFA6C0D67603116045BCAD68167A547E9D552F54B144EBBDAB4051A49A8EBFD08A5D2F1AA304EFBB64F84D7E256A6AEE4ED93AB4C0359A60E83C789298567AFD4C2BA77723657FD663275AA03A438C0A101B644163A07A0FED3E9620C6F000B1274E748E8E324899464E4C07081B40D78F4E1EBFF4D01B6C2; _cfuvid=8Wekpq9V21ZlhB5y0DGIYz5Oh.uyukeJpmEdW9cDT68-1742309862799-0.0.1.1-604800000; rl_page_init_referrer=RudderEncrypt%3AU2FsdGVkX18dBuCS0Hh%2Bq6SNhAuB%2BdnHK1IcSPHULFlWgSBjeGgmqJeyq8sPF77b; rl_page_init_referring_domain=RudderEncrypt%3AU2FsdGVkX18JNKs7rb2DFUD3%2Fg5QVPY%2Frg%2FRr72grdA%3D; _optionalConsent=true; _gcl_au=1.1.329908789.1742309858; indeedCtk=1imks5ktlm224801; GSESSIONID=0C49AAA2AD37AB7270A9968309D3CE26; cass=0; g_state={"i_l":0}; AFSID=OWM3N2NiYTgtN2U3YS00NDkzLWFlNTMtZmUwNjZiZjcwNmZl; muxData==undefined&mux_viewer_id=e11177d7-770b-4206-b68c-f064b7e08dde&msn=0.6205497782095284&sid=a9efa1f4-b286-465d-942f-69f9b7e08de4&sst=1742546701796&sex=1742548209899; asst=1742553339.0; __cf_bm=GhLAPjm2V8rAf6DOydPa_eLvB3._jNgoeRvFmQ.5zmM-1742553341-1.0.1.1-ym8xiNNHXkEdufjJ.qazlXHPb2NljWDGuRe.9vgcYN8rS.sl4VP1jD_8zkcbGkp6RUmp3SAJUD7nSGcNFDjVZpSqNPFcTYVOUAfmF4KBTEDyKVxcLQtM0mi8vjSiZGS3; JSESSIONID=02B7FD20B302E053589B87EE4A6FCB32; bs=onj3QTqgLO2biarUTJ8ZLw:rgBcwwkDiQ8v2vRinszp0h9ekoq3bDnbaFdO0ZPOQgAQzMmc_D7TvPzkTjgdXiq15o0CBmCGjj0T0luWGQyXn5Guhh97oNiCtuzLMlhVjPs:zzcx5NEpA-kQiMxf7WX2MNpRmZACzq7EYRUk7OgEi2w; gdsid=1742532153613:1742554406589:C0BD15273ED926AD39DD86EFC07F7196; at=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmZjJmNThkZi1lZjI5LTQ2YjItOTNjNi03ZmQ4ZGU3ZTYzODkiLCJ1IjoibXVoZGl6emhhbmhha2ltaUBnbWFpbC5jb20iLCJ1aWQiOjI4NzQwOTQ4MywicmZzaCI6MTc0MjU1NTAwNjU4NSwicm1iX2lhdCI6MTc0MjU0NjY4ODk3Miwicm1iX2V4cCI6MTc3NDA4MjY4ODk3MiwiYXR0IjoiZzF0IiwiYXV0aG9yaXRpZXMiOls0NSw0N10sImN1aWQiOiI2NjFkODY3ZjI5ZDUzYWM2NDkwNDJhODgifQ.XMQhyrJYy_5l3ZsS2gCXAFg_an3n1RYAhzdj5bzdssVsTk5DyRlaNpBUXXUx-sTxed7dd3Wkpy0KhAtKM4ESbM35H0-LUuzsGm8_O58ODQ4Qvv_G1CnpeyWbTlskgzdZqCPFuquTWz6oRrjTunuAxovZjHeG82FtY52-zqy_apdRH5G7Qs9BCET6Q5kOa22w8bO-lfmFGy32i1jz72RW67YjszAFPahXnrWkI0Pph2-rYkKfduIUr5s2DgiDL5wxhOPIVKDozqmBoPgAAdJKIStKwIuGqgVGXe_GT_7CgMjE8iT3RRYpS5G8hKoEbYLj1dSJwLY3uUzzfAd2ZMKiew; rl_user_id=RudderEncrypt%3AU2FsdGVkX1%2BQW6w6st%2F5bDdlbKGXMLeFe4%2FgML%2Boq%2BY%3D; rl_trait=RudderEncrypt%3AU2FsdGVkX1%2Fwb1kjwvkXARmh01xZDycZ%2Bkj5Dfw1E6DLkeZubz4wX5UPkN3bC1h5FtAEvyXFMB5pHqJ0dFtZRj1STLVhhoENxQHEcFGn4DRVytFH0XqlJyEjVPWskl1FDcSTNymwmfgxYIwVJlmzCsAySQcap5r2VY%2Bbd8DpSdqNKFMsASvNSMxuJqZWawHIB3UUgauRAH%2B8UqAuAMjA1tEbMRDxCZd6qUiSvALm%2FRD1Ir3Xf1wrmhVt1gvSChBksiuEoZ01o4KN2DQeinfH36L9g%2B0T21IxcfCy7qUrhJE%3D; rl_group_id=RudderEncrypt%3AU2FsdGVkX18ZbTU8S3luPs1yq7wk%2BILGQvTRCXmV5qc%3D; rl_group_trait=RudderEncrypt%3AU2FsdGVkX1949b%2FC5bLlarq5NRjmnAXM0OpJ2o5S4eU%3D; cf_clearance=J3Sx0dsyedQaPSr3doquF7UxM01QwSyuYmMKZFjfm0w-1742554412-1.2.1.1-1qPpzhDqY.tMcIEfM02VHIIuAk_Pcb41_Jv.pNd5nMbYNK36mdO4rKRDJMo9iLGN24Vby8AUiTqG0rq4jAJDuPAbEeTOWEhstJDMfA8LXKyY6Tif.qzp3CjwF.vu.o9xieoCbRJIYz_dAV3dYZ2kjNgcLfsHE4CkV3svMSH25wn8aZ6tlzSJ1FLtQ4a70IyllY5amaxBn4dHhnD00ocoyB0GanT3Akjvq.jxTNVV7CWMhAhxshJh8oyQMzpfIwYq22sjg8qKTpu3gac2MYt3t24HGu19ha99_JbgAHvDkoVGjG1FYmGMvQFI8b5ipEhT5Mehg5d0UjUa5aKDvnI_Vkf93CHvHgJtyBVeC_wEUgY; rsSessionId=1742554407249; rl_anonymous_id=RudderEncrypt%3AU2FsdGVkX18nWRpf1iQeUCV5UKkmB9Qg9kZJTwBK6Lq%2BpH1MCepHgl4InheyLSXPWGzKjq0ChqAyHgbZkf4Z2w%3D%3D; AWSALB=AE+33bbSpqllDmZ3g7b1oDBxqoflexB9ykU3hk4y9JA3F3G2f21Fa/8LW5KOHzwI2qzVyPGVsPkO5ZqfGEdV3w5jJ7fUU22jXR65b3pkA3nGxchDU+JTTinfTt3O; AWSALBCORS=AE+33bbSpqllDmZ3g7b1oDBxqoflexB9ykU3hk4y9JA3F3G2f21Fa/8LW5KOHzwI2qzVyPGVsPkO5ZqfGEdV3w5jJ7fUU22jXR65b3pkA3nGxchDU+JTTinfTt3O; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Mar+21+2025+18%3A53%3A34+GMT%2B0800+(Malaysia+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=313ef960-b913-44cf-9c69-8a647cb0d6b9&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A0%2CC0017%3A1&isAnonUser=1&AwaitingReconsent=false; rsReferrerData=%7B%22currentPageRollup%22%3A%22%2Fjob%2Fjobs-srch%22%2C%22previousPageRollup%22%3A%22%2Fjob%2Fjobs-srch%22%2C%22currentPageAbstract%22%3A%22%2FJob%2F%5BLOC%5D-%5BOCC%5D-jobs-SRCH_%5BPRM%5D.htm%22%2C%22previousPageAbstract%22%3A%22%2FJob%2F%5BLOC%5D-%5BOCC%5D-jobs-SRCH_%5BPRM%5D.htm%22%2C%22currentPageFull%22%3A%22https%3A%2F%2Fwww.glassdoor.com%2FJob%2Fkuala-lumpur-malaysia-data-jobs-SRCH_IL.0%2C21_IC2986682_KO22%2C26.htm%22%2C%22previousPageFull%22%3A%22https%3A%2F%2Fwww.glassdoor.com%2FJob%2Fkuala-lumpur-malaysia-data-jobs-SRCH_IL.0%2C21_IC2986682_KO22%2C26.htm%22%7D; rl_session=RudderEncrypt%3AU2FsdGVkX19M6mKNfsagIaLYWGot5NNXkEqMXNWKrItgAS6OvJAwZX6%2FZkKXMJk3qykPPHPEyjVGGRGToCDH67nG0qpyz3p2STI%2FpFxXMa%2FjJCsP9bxu3D0J97p97Q5v7LQ43Ufkw3rMlMkfoH3nDg%3D%3D; _dd_s=rum=0&expire=1742555331479; cdArr=218"""
    }

    # Payload (Extracted from Network tab)
    payload = {
        "operationName": "JobSearchResultsQuery",
        "query": """
        query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String,
        $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String,
        $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String,
        $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean, $includeIndeedJobAttributes: Boolean) {
            jobListings(
                contextHolder: {queryString: $queryString, pageTypeEnum: $pageType,
                searchParams: {excludeJobListingIds: $excludeJobListingIds, filterParams: $filterParams,
                keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow,
                pageCursor: $pageCursor, pageNumber: $pageNumber, originalPageUrl: $originalPageUrl,
                seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl,
                searchType: SR, includeIndeedJobAttributes: $includeIndeedJobAttributes}}
            ) {
                companyFilterOptions { id shortName __typename }
                filterOptions
                indeedCtk
                jobListings { ...JobListingJobView __typename }
                jobSearchTrackingKey
                jobsPageSeoData { pageMetaDescription pageTitle __typename }
                paginationCursors { cursor pageNumber __typename }
                indexablePageForSeo
                searchResultsMetadata {
                    searchCriteria {
                        implicitLocation { id localizedDisplayName type __typename }
                        keyword
                        location { id shortName localizedShortName localizedDisplayName type __typename }
                        __typename
                    }
                    footerVO { countryMenu { childNavigationLinks { id link textKey __typename } __typename } __typename }
                    helpCenterDomain
                    helpCenterLocale
                    jobAlert { jobAlertId __typename }
                    jobSerpFaq { questions { answer question __typename } __typename }
                    jobSerpJobOutlook { occupation paragraph heading __typename }
                    showMachineReadableJobs
                    __typename
                }
                serpSeoLinksVO {
                    relatedJobTitlesResults
                    searchedJobTitle
                    searchedKeyword
                    searchedLocationIdAsString
                    searchedLocationSeoName
                    searchedLocationType
                    topCityIdsToNameResults { key value __typename }
                    topEmployerIdsToNameResults { key value __typename }
                    topOccupationResults
                    __typename
                }
                totalJobsCount
                __typename
            }
        }

        fragment JobListingJobView on JobListingSearchResult {
            jobview {
                header {
                    indeedJobAttribute { skills extractedJobAttributes { key value __typename } __typename }
                    adOrderId ageInDays divisionEmployerName easyApply
                    employer { id name shortName __typename }
                    expired occupations { key __typename }
                    employerNameFromSearch goc gocConfidence gocId isSponsoredJob isSponsoredEmployer jobCountryId
                    jobLink jobResultTrackingKey normalizedJobTitle jobTitleText locationName locationType locId
                    needsCommission payCurrency payPeriod payPeriodAdjustedPay { p10 p50 p90 __typename }
                    rating salarySource savedJobId seoJobLink __typename
                }
                job { descriptionFragmentsText importConfigId jobTitleId jobTitleText listingId __typename }
                jobListingAdminDetails {
                    cpcVal importConfigId jobListingId jobSourceId userEligibleForAdminJobDetails __typename
                }
                overview { shortName squareLogoUrl __typename }
                __typename
            }
            __typename
        }
        """,
        "variables": {
            "keyword": job,
            "locationId": locId,
            "numJobsToShow": numjob,
            "originalPageUrl": url,
            "pageCursor": "",
            "pageNumber": 1,
            "pageType": "SERP",
            "parameterUrlInput": backurl,
            "queryString": "",
            "seoUrl": True,
            "includeIndeedJobAttributes": False
        }
    }

    # Send the request
    response = requests.post(url, headers=headers, json=payload)

    response.raise_for_status()
    return response.json()


def find_jl(data):
    jl = {
        'job': [],
        'jl': []
    }

    for i in range(len(data['data']['jobListings']['jobListings'])):
        jobname = data['data']['jobListings']['jobListings'][i]['jobview']['header']['jobTitleText']
        link = data['data']['jobListings']['jobListings'][i]['jobview']['header']['seoJobLink']
        jl['job'].append(jobname)
        jl['jl'].append(re.findall(r'(\d+)', link)[-1])

    #print(jl)
    return jl

def proper_desc(data):
    desc = []

    company_name = data[0]['data']['jobview']['header']['employerNameFromSearch']
    job_link = data[0]['data']['jobview']['header']['seoJobLink']
    job_desc = data[0]['data']['jobview']['job']['description']

    desc.append(company_name)
    desc.append(job_link)
    desc.append(job_desc)

    #print(desc)

    return desc

def get_job_desc(jl):
    # Define the target URL
    url = "https://www.glassdoor.com/graph"

    # Headers (Extracted from the browser)
    headers = {
        "authority": "www.glassdoor.com",
        "method": "POST",
        "path": "/graph",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "apollographql-client-name": "job-search-next",
        "apollographql-client-version": "7.159.3",
        "content-type": "application/json",
        "cookie": "gdId=a9d66fe3-4026-405b-b1b2-4f150f5964fa; AFSID=MGQ1NTY3MjAtYWZkZS00NTIyLWE3YzctYzcwOGZhOGI2M2Mz; uc=8013A8318C98C5175B5209E39BEB897033A6F39CF905396DFA6C0D67603116045BCAD68167A547E9D552F54B144EBBDAB4051A49A8EBFD08A5D2F1AA304EFBB64F84D7E256A6AEE4ED93AB4C0359A60E83C789298567AFD4C2BA77723657FD663275AA03A438C0A101B644163A07A0FED3E9620C6F000B1274E748E8E324899464E4C07081B40D78F4E1EBFF4D01B6C2; ...",  # Truncated for security
        "dnt": "1",
        "gd-csrf-token": "RW7GdSHJVB-PCyp5znk7OA:FG-ii_HRghg_la0YW8dmZHFLCLTEgbjNMBYtH509mCbbTguKrYianZKzD5KEIrE3jwGDyWU9xsE0IcOgkG3oiw:Hj4GuHFuHKbLm4aIivCZYflXVdzxT4EzptpFdi4IokE",
        "origin": "https://www.glassdoor.com",
        "priority": "u=1, i",
        "referer": "https://www.glassdoor.com/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "x-gd-job-page": "serp",
    }


    # Payload (Extracted from Network tab)
    payload = [
        {
            "operationName": "JobDetailQuery",
            "variables": {
                "enableReviewSummary": True,
                "jl": jl,
                "queryString": "pos=304&ao=1110586&s=58&guid=00000195b7c539079449abb6ddddd73c&src=GD_JOB_AD&t=SR&vt=w&uido=082E034D73372B1549A32500B713A039&ea=1&cs=1_dfe2b6ec&cb=1742544911396&jobListingId=1009653931483&cpc=3BA4CE39D5B5DEF5&jrtk=5-pdx1-0-1imrsaelpgqmg801-0ac40370e4e6dee4---6NYlbfkN0BUxdI6NUc3efLh30aST9GkYiSqrFjIQiZVwYtQ6o5Opu2g-wGsSN4I-HOGtlRpHwhzb-ANkAjot60yx-H7ZyWqjj226ims3lufrL60CZJkA3fSHy766zxm0Iu9iGyWAAqsTwP7XSNvM4qEFH1FhG8dkkipkPPMnM1LP5Fc0oLjLXhZO1AtmODTs93S6wCJOpH3-C4y475T0k_hugJxLt2Dkxrt7N3Nvii7UgocdfN47T9LTO3oSEcA2U5R5omSq43RbBAR9jL27MKzYNK66W1nogG68ymDPyf5LkYE_ACpqMon15SrbE0SbQY7Loxp5b7a9HXVMe1eepT0ubhHF-m6oGBAPnqngPHRNHVBONBDICLmsHVzWYf-KkQWClTY0Z2sjXloqRdkYFeeADtbR5mR6EAZfVaTBjnVi5Z9jZLa85n_FOZB3wZKPBe2yvezDg9Wr0wLKXNfnl3odXVhj7LbwnKoA32FHvOyEuF1qfKAFS3DZ8raQur6RmRfMdEGBK9DjOdlG2aHxR_CjFnhNkIh6L7zmKWMUeoFmy5ZSBRpyF3MDsy8OHTxC6v7umfRcNNcPwvAOtOAlHJi3r2ZTpwReesJqejBecXCq8PkrOI00KsuOayWmhTAW1SwdaPBd0JAC5h7dJO19PBTLTKI4J7OBro2QXtmH3bk0gMhEXTDgELZGpe1S0TouSFT1czJzkZVw4F1nCWWsyYaY26QG4DdZN717xqZUZXTNuXpc_thBWVoeoEE5tjr",
                "pageTypeEnum": "SERP",
                "countryId": 1
            },
            "query": "query JobDetailQuery($jl: Long!, $queryString: String, $enableReviewSummary: Boolean!, $pageTypeEnum: PageTypeEnum, $countryId: Int) { jobview: jobView(listingId: $jl, contextHolder: {queryString: $queryString, pageTypeEnum: $pageTypeEnum}) { ...JobDetailsFragment employerReviewSummary @include(if: $enableReviewSummary) { reviewSummary { highlightSummary { sentiment sentence categoryReviewCount __typename } __typename } __typename } __typename } } fragment JobDetailsFragment on JobView { employerBenefits { benefitsOverview { benefitsHighlights { benefit { commentCount icon name __typename } highlightPhrase __typename } overallBenefitRating employerBenefitSummary { comment __typename } __typename } benefitReviews { benefitComments { id comment __typename } cityName createDate currentJob rating stateName userEnteredJobTitle __typename } numReviews __typename } employerContent { managedContent { id type title body captions photos videos __typename } __typename } employerAttributes { attributes { attributeName attributeValue __typename } __typename } gaTrackerData { jobViewDisplayTimeMillis requiresTracking pageRequestGuid searchTypeCode trackingUrl __typename } header { jobLink adOrderId ageInDays applicationId appliedDate applyUrl applyButtonDisabled categoryMgocId campaignKeys divisionEmployerName easyApply employerNameFromSearch employer { activeStatus bestProfile { id __typename } id name shortName size squareLogoUrl __typename } expired goc gocId hideCEOInfo indeedJobAttribute { education skills educationLabel skillsLabel yearsOfExperienceLabel __typename } isIndexableJobViewPage isSponsoredJob isSponsoredEmployer jobTitleText jobType jobTypeKeys jobCountryId jobResultTrackingKey locId locationName locationType needsCommission normalizedJobTitle payCurrency payPeriod payPeriodAdjustedPay { p10 p50 p90 __typename } profileAttributes { suid label match type __typename } rating remoteWorkTypes salarySource savedJobId seoJobLink serpUrlForJobListing sgocId __typename } job { description discoverDate eolHashCode importConfigId jobTitleId jobTitleText listingId __typename } jobListingAdminDetails { adOrderId cpcVal importConfigId jobListingId jobSourceId userEligibleForAdminJobDetails __typename } map { address cityName country employer { id name __typename } lat lng locationName postalCode stateName __typename } overview { ceo(countryId: $countryId) { name photoUrl __typename } id name shortName squareLogoUrl headquarters links { overviewUrl benefitsUrl photosUrl reviewsUrl salariesUrl __typename } primaryIndustry { industryId industryName sectorName sectorId __typename } ratings { overallRating ceoRating ceoRatingsCount recommendToFriendRating compensationAndBenefitsRating cultureAndValuesRating careerOpportunitiesRating seniorManagementRating workLifeBalanceRating __typename } revenue size sizeCategory type website yearFounded __typename } photos { photos { caption photoId photoId2x photoLink photoUrl photoUrl2x __typename } __typename } reviews { reviews { advice cons countHelpful employerResponses { response responseDateTime userJobTitle __typename } employmentStatus featured isCurrentJob jobTitle { text __typename } lengthOfEmployment pros ratingBusinessOutlook ratingCareerOpportunities ratingCeo ratingCompensationAndBenefits ratingCultureAndValues ratingOverall ratingRecommendToFriend ratingSeniorLeadership ratingWorkLifeBalance reviewDateTime reviewId summary __typename } __typename } __typename }"
        }
    ]


    # Send the request
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    #return response.json()
    return proper_desc(response.json())

def job_scrape(numjob, url, job):
    jobs = {
        "company": [],
        "job-title": [],
        "link": [],
        "job-description": []
    }

    jl = find_jl(get_job(numjob, url, job))

    for value in jl['jl']:

        info = get_job_desc(value)

        jobs["company"].append(info[0])
        jobs["link"].append(info[1])
        jobs["job-description"].append(info[2])

    jobs['job-title'] = jl['job']

    return jobs

def glassdoor_job_searcher(job_description, job_count, resume=None):
   try:
        with st.spinner("🔄Searching jobs based on your prescriptions, please wait...."):
            key = st.secrets["api_keys"]["gemini_1"]
            if resume == None :
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description: {job_description}
                '''
                )
            else:
                reader = PdfReader(resume)
                text = ""
                # Loop through all pages and extract text
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                candidate_preferences = model.generate_content(
                f'''
                From the job description given what are the job preferences, experience and skills of this candidate,
                job description(summarize it): {job_description}

                From the resume texts, summarise all skills and necessary experience that this candidate have
                resume texts :{text}

                your output should be like this:

                Resume information:
                .....

                Job Preferences:
                .......


                '''
                )
                
            print(candidate_preferences.text)
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
            response2 = model.generate_content(
            f'''
            ok now based on the job preferences (not the resume details) right here
            {job_description},
            i want you to fill out this python code right here
            python code :
            keywords = #Here put out the job title like data analyst or full stack developer or cloud engineer (dont put a verb like software engineering, put a role like software engineer) ,only put one job title dont put more than one, if the request has more than one job just choose one
            company = None    # If the text specify a company name, put it here, if not put None , only put one company name dont put more than one, if the request has more than one just choose one 
            location = "Malaysia"  # If the text specify a location, put it here (put the name of the place and nothing else), if not put Malaysia ,also just choose one location if it specify many location
            after filling out this python code, i want you to just return the code and NOTHING ELSE
                        '''
            )
            print(" ")
            print(response2.text)

            code = response2.text
            # Remove code block markers
            code = re.sub(r'```python', '', code)
            code = re.sub(r'```', '', code)


            exec_globals = {}
            code = code.strip()
            if is_code_safe(code):
                exec(code, exec_globals)
                keywords = exec_globals.get('keywords')
                company = exec_globals.get('company')
                location   = exec_globals.get('location')
            else:
                print("The code contains potentially dangerous operations and will not be executed.")

            test_url = url_maker(location, keywords)

            test_job = job_scrape(job_count, test_url, keywords)

            test_df = pd.DataFrame(test_job)

            st.subheader("Scraped Job Data:")
            st.dataframe(test_df)
            with st.spinner("⌛ Filtering jobs that are compatible for you, please wait...."):
                key1=st.secrets["api_keys"]["gemini_1"]
                key2=st.secrets["api_keys"]["gemini_2"]
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                # Assume df and candidate_preferences have already been defined/loaded.
                # For example:
                # df = pd.read_csv('linkedinjobs.csv')
                # candidate_preferences = "..."  # your candidate profile string
                compatible_jobs = []   # List to store rows deemed compatible
                incompatible_jobs = [] # List to store rows deemed not compatible

                # Iterate through each job entry in the DataFrame
                for idx, row in test_df.iterrows():

                    
                    if idx%2 == 0:
                        key=key1
                    else:
                        key=key2
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                    #time.sleep(1.5)
                    job_desc = row.get("job-description", "")
                    
                    # Skip jobs with missing or empty descriptions
                    if pd.isna(job_desc) or not job_desc.strip():
                        row = row.copy()
                        row["reason"] = "Job description missing."
                        incompatible_jobs.append(row)
                        continue

                    # Adjusted prompt: include an example for clarity.
                    prompt = f"""
                    Candidate Profile:
                    {candidate_preferences.text}

                    Job Description:
                    {job_desc}

                    Based on the above, is this job compatible with the candidate's preferences? 
                    Please answer with either "yes" or "no" followed by a brief explanation.
                    For example: "yes, because the role matches the candidate's skills in data analytics."
                    """
                    # Call the Gemini API with the prompt
                    response = model.generate_content(prompt)
                    answer = response.text.strip()
                    answer_lower = answer.lower()
                    
                    # Extract the explanation if available (assumes response in format "yes, because ..." or "no, because ...")
                    if "," in answer:
                        reason = answer.split(",", 1)[1].strip()
                    else:
                        reason = "No explanation provided."

                    row = row.copy()
                    row["reason"] = reason

                    if answer_lower.startswith("yes"):
                        compatible_jobs.append(row)
                    else:
                        incompatible_jobs.append(row)

                # Create DataFrames for the compatible and incompatible jobs
                df_compatible = pd.DataFrame(compatible_jobs)
                df_incompatible = pd.DataFrame(incompatible_jobs)
                st.markdown("---")

                st.subheader("Compatible jobs:")
                st.dataframe(df_compatible)

                st.subheader("Incompatible jobs:")
                st.dataframe(df_incompatible)
   except:
        error_trace = traceback.format_exc()  # Get the full traceback as a string
        st.error("Failed to fetch jobs, please try again")
        print(f"Error details:\n{error_trace}")





            
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_card import card
import re
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

import gspread
from google.oauth2.service_account import Credentials


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
    st.plotly_chart(fig, use_container_width=True)


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

    st.plotly_chart(fig)

####################################### Glassdoor Scraping ##############################################

def in_range(i,word_array):
  try:
    for j in range (i-5,i):
        if word_array[j]== "year" or word_array[j]=="years":
          return j
  except:
    return -1

  return -1

def extract_experience(text):
  word_array = text.split()
  for i in range(len(word_array)) :
    if word_array[i] == "experience" or word_array[i]=="experiences":
      j=in_range(i,word_array)
      if j != -1:
        return word_array[j-1]
  return "Not_specified"

def extract_skills(text,skillset):
    skills = []
    for i in skillset :
      if i.lower() in text.lower():
        skills.append(i)
    return skills

def skill_extractor(programming_languages,frameworks,databases,cloud_service_providers,other_tools,job_requirements,experiences):
  # Load the HTML content
  with open(f'html_scripts\\subpages\\subpage_glassdoor.html', 'r', encoding='utf-8') as file:
      html_content = file.read()

  soup = BeautifulSoup(html_content, 'html.parser')
  skills = programming_languages + frameworks + databases + cloud_service_providers + other_tools
  skills = list(set(skills))
  
  for i in range (len(skills)) :
    if len(skills[i])<=10:
      skills[i]=" "+skills[i]+" "

  text_array = []
  brandviews_div = soup.find('div', attrs={'data-brandviews': True})
    
  if brandviews_div:
      # Extract <li> and <p> tags only from the found <div>
      li_tags = brandviews_div.find_all('li', class_=False)
      p_tags = brandviews_div.find_all('p', class_=False)

      for i in li_tags:
          text_array.append(i.text)

      for i in p_tags:
          text_array.append(i.text)

  concatenated_string = " ".join(text_array)

  concatenated_string = " "+concatenated_string+" "
  concatenated_string = re.sub(r'(?<![A-Za-z0-9])\.|\.(?![A-Za-z0-9])|[^A-Za-z0-9.#+]', ' ', concatenated_string)

  print(concatenated_string)

def check_and_close_login_modal(wd):
    try:
        close_button = wd.find_element(By.CLASS_NAME, "CloseButton")
        close_button.click()
        print("Login modal closed.")
    except NoSuchElementException:
        print("No login modal appeared.")


def get_info():
    with open('html_scripts\\test_glassdoor.html', 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find all divs with the specified class
    divs = soup.find_all('div', class_='EmployerProfile_profileContainer__63w3R EmployerProfile_compact__28h9t')
    Id_array=[]
    company_name=[]

    for div in divs:
        div_id = div.get('id')  # Extract the id attribute
        #print(f"ID: {div_id}")  # Print the ID
        Id_array.append(div_id)
        #print(div.text)  # Print the text content of each div
        company_name.append(div.text)

    job_links = []

    for job_card in soup.find_all('li', {'data-test': 'jobListing'}):
        link = job_card.find('a', {'data-test': 'job-link'})
        age = job_card.find('div', {'data-test': 'job-age'})
        
        if link and age:
            job_links.append(link['href'])  # Get the href attribute
            #job_ages.append(age.text.strip())
    
    job_cards = soup.find_all('div', class_='JobCard_jobCardContainer__arQlW') #if the html code changes search detalSalary in the inspect mode and get the new class name
    
    title=[]
    location=[]
    salary=[]
    employer=[]
    rating=[]

    job_dataframe = []

    i=0
    # Extract relevant information from each job card
    for job_card in job_cards:
        # Extract job title
        job_title = job_card.find('a', class_='JobCard_jobTitle__GLyJ1').text.strip() if job_card.find('a', class_='JobCard_jobTitle__GLyJ1') else "N/A"
        title.append(job_title)

        # Extract job location
        job_location = job_card.find('div', class_='JobCard_location__Ds1fM').text.strip() if job_card.find('div', class_='JobCard_location__Ds1fM') else "N/A"
        location.append(job_location)

        # Extract salary estimate
        job_salary = job_card.find('div', class_='JobCard_salaryEstimate__QpbTW').text.strip() if job_card.find('div', class_='JobCard_salaryEstimate__QpbTW') else "N/A"
        salary.append(job_salary)

        # Extract employer name
        employer_name = job_card.find('span', class_='EmployerProfile_compactEmployerName__9MGcV').text.strip() if job_card.find('span', class_='EmployerProfile_compactEmployerName__9MGcV') else "N/A"
        employer.append(employer_name)

        # Extract employer rating
        employer_rating = job_card.find('span', class_='EmployerProfile_ratingContainer__ul0Ef').text.strip() if job_card.find('span', class_='EmployerProfile_ratingContainer__ul0Ef') else "N/A"
        #rating.append(employer_rating)
        rating.append(None)

        '''
        # Print the extracted information
        print(f"Job Title: {job_title}")
        print(f"Job ID: {Id_array[i]}")
        print(f"Company Name : {company_name[i]}")
        print(f"Location: {job_location}")
        print(f"Salary: {job_salary}")
        print(f"Employer: {employer_name}")
        print(f"Rating: {employer_rating}")
        print(f"Link : {job_links[i]}")
        print('-' * 40)
        '''
        i=i+1


    print(f"Length of Id_array: {len(Id_array)}")
    print(f"Length of title: {len(title)}")
    print(f"Length of company_name: {len(company_name)}")
    print(f"Length of location: {len(location)}")
    print(f"Length of salary: {len(salary)}")
    print(f"Length of employer: {len(employer)}")
    print(f"Length of job_links: {len(job_links)}")

            
    temp_df=pd.DataFrame({
    "Job ID": Id_array,  # Ensure Id_array is defined and populated
    "Job Title": title,
    "Company Name": company_name,  # Ensure company_name is defined and populated
    "Location": location,
    "Salary": salary,
    "Employer": employer,
    "Rating": employer,
    "Link": job_links,
    })

    job_dataframe.append(temp_df)
        
    df=pd.concat(job_dataframe)
    return df

def scrape_glassdoor(JobTitle):
    driver_path = "chromedriver.exe"
    days=1
    base_url={
    "Data Analyst":f"https://www.glassdoor.com/Job/malaysia-data-analyst-jobs-SRCH_IL.0,8_IN170_KO9,21.htm?fromAge={days}",
    "Data Scientist":f"https://www.glassdoor.com/Job/malaysia-data-scientists-jobs-SRCH_IL.0,8_IN170_KO9,24.htm?fromAge={days}",
    "Data Engineer":f"https://www.glassdoor.com/Job/malaysia-data-engineer-jobs-SRCH_IL.0,8_IN170_KO9,22.htm?fromAge={days}",
    "Full Stack Developer":f"https://www.glassdoor.com/Job/malaysia-full-stack-developer-jobs-SRCH_IL.0,12_IC2986682_KO13,33.htm?fromAge={days}",
    "Frontend Developer":f"https://www.glassdoor.com/Job/malaysia-front-end-developer-jobs-SRCH_IL.0,8_IN170_KO9,28.htm?fromAge={days}",
    "Backend Developer":f"https://www.glassdoor.com/Job/malaysia-backend-developer-jobs-SRCH_IL.0,12_IC2986682_KO13,30.htm?fromAge={days}",
    "Cloud Engineer":f"https://www.glassdoor.com/Job/malaysia-cloud-engineer-jobs-SRCH_IL.0,8_IN170_KO9,23.htm?fromAge={days}",
    "Business Analyst":f"https://www.glassdoor.com/Job/malaysia-business-analyst-jobs-SRCH_IL.0,8_IN170_KO9,25.htm?fromAge={days}"
    }

    url = base_url[JobTitle]
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no window)
    #chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (for headless)
    service = Service(executable_path=driver_path)
    wd = webdriver.Chrome(service=service)
    wd.get(url)
    with open(f"html_scripts\\test_glassdoor.html", "w") as file:
            file.write(wd.page_source)

    with open('html_scripts\\test_glassdoor.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')


    job_titles = soup.find_all('h1', {'data-test': 'search-title'})
    str_=job_titles[0].text.strip()
    number_of_jobs = re.sub(r'\D', '', str_)
    number_of_jobs = int(number_of_jobs)

    number_of_pages = int(number_of_jobs/30)
    if(number_of_pages==0):
         number_of_pages=1
    print("Number of jobs : ",number_of_jobs)
    print("Number of pages : ",number_of_pages)
    time.sleep(5)

    # Click the 'Show More Jobs' button 3 times
    for _ in range(number_of_pages):
        # Check for the login modal before clicking
        check_and_close_login_modal(wd)

        try:
            load_more_button = wd.find_element(By.CSS_SELECTOR, 'button[data-test="load-more"]')
            
            # Click the button to load more jobs
            load_more_button.click()
            
            # Wait for the new jobs to load after the button click
            time.sleep(5)
            
            print("Clicked 'Show more jobs' button.")
            
        except NoSuchElementException:
            print("No 'Show more jobs' button found.")
            break
        except Exception as e:
            print(f"Error: {e}")

    # Save the updated page source
    with open(f"html_scripts\\test_glassdoor.html", "w", encoding='utf-8') as file:
        file.write(wd.page_source)
    df=get_info()
    return df


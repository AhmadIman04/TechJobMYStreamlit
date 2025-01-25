import streamlit as st
import pandas as pd
from streamlit_tags import st_tags
from Functions import get_skill_percentage
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

#alljobsdf= pd.read_csv("alljobs_df_9.csv")
#skill_dim = pd.read_csv("skill_dim.csv")
#job_skills=pd.read_csv("skills_table3.csv")
#skill_dim.rename(columns={"Skill":"Skills"},inplace=True)


#alljobsdf.drop(columns=["Unnamed: 0"],inplace=True)
#skill_dim.drop(columns=["Unnamed: 0"],inplace=True)
#job_skills.drop(columns=["Unnamed: 0"],inplace=True)

#skill_dim.rename(columns={"Skill":"Skills"},inplace=True)

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

if "hasPulledData2" not in st.session_state:
    with st.spinner("🔄 Loading data... Please wait a moment!"):
        # Google Sheets API authorization
        st.session_state.hasPulledData2 = True
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

with col2:
    suggestions = ['Python', 'GitHub', 'React', 'SQL', 'R', 'Tableau', 'Power BI',
       'Excel', 'SAS', 'Looker', 'Google Analytics', 'Parcel', 'Realm',
       'AWS', 'PowerPoint', 'Jira', 'Confluence', 'Bigquery', 'Azure',
       'Git', 'Airflow', 'Docker', 'Java', 'C++', 'Scala', 'MySQL',
       'Redshift', 'Salesforce', 'Oracle', 'Hadoop', 'QlikView',
       'Teradata', 'Cocoa', 'Spark', 'Office Suite', 'sap',
       'Jupyter Notebook', 'Snowflake', 'Box', 'PySpark',
       'Adobe Analytics', 'Sentry', 'Metabase', 'Figma', 'DataStage',
       'SSIS', 'Firebase', 'Alibaba Cloud', 'Apache Superset',
       'Databricks', 'HTML', 'SQL Server', 'spotfire', 'Shopify',
       'Airtable', 'MSSQL', 'Zapier', 'Visio', 'Bash', 'Perl',
       'JavaScript', 'PHP', 'Slack', 'HubSpot', 'Cassandra', 'GCP',
       'Keras', 'Pandas', 'Tensorflow', 'Kubernetes', 'Fly', 'CSS',
       'Sanity', 'Jenkins', 'Selenium', 'Qlik Sense', 'Notion', 'Cobol',
       'Swift', 'Kafka', 'PostgreSQL', 'SharePoint', 'C#', 'NumPy',
       'Scikit', 'Flask', 'Django', 'RESTful API', 'PyTorch', 'S3',
       'Smartsheet', 'Alteryx', 'Composer', 'Microsoft 365', 'JSP',
       'Angular', 'Crystal', 'ABAP', 'CodeIgniter', 'Laravel', 'XGBoost',
       'Elasticsearch', 'IBM Watson', 'OpenCV', 'DigitalOcean', 'Seaborn',
       'Matplotlib', 'MLflow', 'Vuejs', 'Presto', 'jQuery', 'Bootstrap',
       'Golang', 'Terraform', 'GitHub Actions', 'Nodejs', 'TypeScript',
       'Dash', 'Shiny', 'Metaflow', 'LightGBM', 'Enzyme', 'MongoDB',
       'Grafana', 'Azure DevOps', 'Visual Basic', 'Cisco', 'Unity', 'Io',
       'Spring', 'Spring Boot', 'Redis', 'Railway', 'DB2', 'Netezza',
       'Tcl', 'CloudStack', 'IBM Cloud', 'Puppet', 'Prometheus', 'Chef',
       'OpenStack', 'Rackspace', 'Ansible', 'Sass', 'Yarn', 'Nextjs',
       'Nuxtjs', 'npm', 'Webpack', 'Ionic', 'Ruby', 'pytest', 'Bitbucket',
       'GraphQL', 'React Native', 'Kotlin', 'Flutter', 'Xamarin', 'Dart',
       'Apex', 'Rust', 'MATLAB', 'HBase', 'Ray', 'Kibana', 'RabbitMQ',
       'ELK Stack', 'Max', 'WPF', 'CVS', 'QuickBooks', 'Xero',
       'Apache Hive', 'Amazon DynamoDB', 'Trello', 'Postman', 'Sybase',
       'Ruby on Rails', 'JUnit', 'Nginx', 'Groovy', 'SonarQube', 'Svelte',
       'Streamlit', 'CouchDB', 'MariaDB', 'NestJS', 'ASPNET', 'Helm',
       'Expressjs', 'CircleCI', 'GitLab CI', 'NLTK', 'Azure SQL',
       'OpenShift', 'Datadog', 'Joomla', 'Symfony', 'Cypress',
       'Playwright', 'Unreal Engine', 'Chai', 'Mocha', 'Slim', 'Heroku',
       'Semantic UI', 'Jest', 'Gulp', 'Babel', 'YII', 'CakePHP',
       'Wordpress', 'Cordova', 'Apache Cordova', 'Stripe', 'Gitea',
       'Restify', 'Sequelize', 'CSS Modules', 'NUnit', 'SQLite',
       'Apache HTTP Server', 'Robot Framework', 'Amazon Aurora',
       'FastAPI', 'ASPNET Core', 'Grunt', 'Bower', 'TFS',
       'AWS CodePipeline', 'Jasmine', 'SVN', 'Java EE', 'Spring Security',
       'Spring Cloud', 'Quasar Framework', 'Quasar', 'Shopify Plus',
       'Liquid', 'Spring MVC', 'ASPNET MVC', 'Pivotal Cloud Foundry',
       'Solidity', 'UIKit', 'Phaser', 'SEMrush', 'Swing', 'Java Swing',
       'Jersey', 'Tailwind CSS', 'Styled Components', 'Asana',
       'Mercurial', 'Flux', 'PlayCanvas', 'Unity3D', 'Canva', 'Mailchimp',
       'Adobe Creative Suite', 'RxJS', 'Aurelia', 'Concourse',
       'Spring Data', 'Cocos Creator', 'gRPC', 'Puppeteer', 'Travis CI',
       'Hapijs', 'Socketio', 'MobX', 'Vite', 'Mendix', 'Spring Batch',
       'New Relic', 'Spring Integration', 'Koajs', 'KNIME', 'Cognito',
       'Cocos2d', 'RxJava', 'Lucidchart', 'SAP HANA', 'BigCommerce',
       'Cucumber', 'TestNG', 'Oracle Cloud', 'Red Hat OpenShift',
       'Cisco Cloud', 'AppSync', 'Kendo UI', 'WinForms', 'Nagios',
       'AppDynamics', 'Subversion', 'WireMock', 'Vercel', 'Netlify',
       'JSS', 'Cloudflare', 'VBScript', 'Backbonejs', 'Apache Camel',
       'SAP Cloud Platform', 'Druid', 'Neo4j', 'Sed', 'Awk', 'Avro',
       'Memcached', 'Retrofit', 'Threejs', 'Apollo Client',
       'Sencha Touch', 'PhoneGap', 'Adobe Experience Cloud', 'OSGi',
       'Apache Felix', 'Play Framework', 'Gauge', 'XSLT',
       'Apache Phoenix', 'Phoenix', 'Azure Cosmos DB',
       'Assembly Language', 'Haystack', 'spaCy', 'gensim', 'Karma',
       'Ant Design', 'SpecFlow', 'Babylonjs', 'Elixir', 'Informix',
       'Vertx', 'Wix', 'Umbraco', 'Gherkin', 'Yii2', 'MongoDB Atlas',
       'RestAssured', 'Blazor', 'MFC', 'Protractor', 'SwiftUI', 'Linode',
       'Render', 'InVision', 'Emotion', 'Phalcon', 'Zendesk', 'Emberjs',
       'Dask', 'Coda', 'Jackson', 'Apache Ant', 'Elastic Cloud',
       'NIST Cybersecurity Framework', 'ISO 27001', 'Akamai', 'FAIR',
       'PCI DSS', 'Glitch', 'QRadar', 'Miro', 'AutoML', 'Zebra', 'Ceylon',
       'Zoom', 'Apache Flink', 'Lua', 'Amazon Redshift', 'Fastlane',
       'Plotly', 'Citus', 'Tornado', 'CockroachDB', 'Zoho', 'Fossil',
       'Preact', 'ClickHouse', 'F#', 'Webflow', 'Google Workspace',
       'Skeleton', 'Game Framework', 'Electron', 'Calendly', 'Vitest',
       'Shadow DOM', 'Firebase Realtime', 'XamarinForms', 'Pyramid',
       'Firebird', 'Delphi', 'NativeScript', 'Django REST Framework',
       'PyQt', 'Pico', 'Google Slides', 'ITIL', 'Grails', 'Splunk',
       'Octopus Deploy', 'Owasp', 'Dagger', 'Responder', 'GDPR', 'Nessus',
       'Google Cloud Firestore', 'Adobe Acrobat', 'ClickUp',
       'Materialize', 'Couchbase', 'Oracle Cloud Infrastructure', 'Okta',
       'Qt', 'Azure AD', 'QuickBooks Online', 'H2Oai', 'Sophos', 'Ktor',
       'Haskell', 'Atlassian Cloud', 'Alpinejs', 'Balsamiq', 'Checkpoint',
       'WebAssembly', 'Godot', 'Meteor', 'Allegro', 'SOC 2', 'Gatling',
       'Burp Suite']
    
    st.session_state.Skill=st.selectbox(
        "Choose Skill",
        suggestions
    )
st.session_state.mentioned_p,st.session_state.number_of_jobs = get_skill_percentage(st.session_state.Job,st.session_state.Skill,merged_all_table=merged_all_table)
with st.container(border=True):
    st.markdown(
            f"""
            <div style="text-align: center; font-size: 16px;">
                {st.session_state.Skill} is mentioned <b>{st.session_state.mentioned_p}%</b> of the time out of 
                {st.session_state.number_of_jobs} {st.session_state.Job} job postings
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")




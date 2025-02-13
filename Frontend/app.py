import streamlit as st
from dotenv import load_dotenv
import os, sys
sys.path.append("..")

from backend.jenkins_operations import JenkinsOperations
from backend.auth.auth import authenticate
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import Ollama

# Load environment variables
load_dotenv("../backend/config/auth.env")

# Jenkins Configuration
JENKINS_BASE_URL = os.getenv("JENKINS_BASE_URL")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")

# Jenkins API Instance
jenkins_api = JenkinsOperations()

# Authentication state
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tool Functions
def list_all_jobs(*args, **kwargs):
    if not st.session_state.authenticated_user:
        return "⚠️ Please log in first."
    print(f"======logv {st.session_state.authenticated_user}==== ")
    jobs = jenkins_api.get_all_jobs(st.session_state.authenticated_user)
    if isinstance(jobs, dict) and "jobs" in jobs:
        job_list = jobs["jobs"][:10]  # Limit display to first 10 jobs
        return "Here are some available Jenkins jobs:\n" + "\n".join(job_list) + "\n(Type 'Show More' for additional jobs.)"
    return "❌ Failed to fetch job list."

def trigger_job(job_name: str):
    if not st.session_state.authenticated_user:
        return "⚠️ Please log in first."
    return jenkins_api.trigger_job(st.session_state.authenticated_user, job_name, {})

def get_last_build_summary(job_name: str):
    data = jenkins_api.get_last_build_summary(job_name)
    return f"Build #{data['number']} Status: {data['result']} - {data['url']}"

def get_specific_build_summary(job_name: str, build_number: str):
    data = jenkins_api.get_specific_build_summary(job_name, build_number)
    return f"Build #{build_number} Status: {data['result']} - {data['url']}"

def get_job_health(job_name: str):
    return jenkins_api.get_job_health(job_name)

# Define Tools
tools = [
   Tool(
        name="List All Jobs",
        func=list_all_jobs,
        description="Lists available Jenkins jobs and returns them in a structured format.",
        return_direct=True,  # Ensures the response is directly sent to the user
    ),
    Tool(name="Trigger Job", func=trigger_job, description="Triggers a Jenkins job."),
    Tool(name="Get Last Build Summary", func=get_last_build_summary, description="Fetches the last build summary."),
    Tool(name="Get Specific Build Summary", func=get_specific_build_summary, description="Fetches a specific build summary."),
    Tool(name="Get Job Health", func=get_job_health, description="Checks the health status of a Jenkins job."),
]

# Memory and LLM
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
llm = Ollama(model="llama3")

# Initialize AI Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
)

def process_query(query: str):
    if not st.session_state.authenticated_user:
        return "⚠️ Please log in first."
    response = agent.run(query)
    st.session_state.chat_history.append((query, response))
    return response

# Streamlit UI
st.set_page_config(page_title="CICD AI Bot", page_icon="🤖")
st.title("🤖 Jenkins CICD AI Bot")

# Authentication
if not st.session_state.authenticated_user:
    st.subheader("🔑 Login")
    username = st.text_input("Username:", key="username")
    password = st.text_input("Password:", type="password", key="password")
    if st.button("Login"):
        auth_result = authenticate(username, password)
        if auth_result["status"] == "failed":
            st.error(f"❌ {auth_result['message']}")
        else:
            st.session_state.authenticated_user = {"username": username, "role": auth_result["role"]}
            st.success(f"✅ Welcome, {username} ({auth_result['role']})!")
            st.rerun()

# Chat Interface
if st.session_state.authenticated_user:
    st.subheader("💬 AI Chatbot for CICD Operations")
    for query, response in st.session_state.chat_history:
        st.write(f"🧑‍💻 You: {query}")
        st.write(f"🤖 Bot: {response}")
    
    prompt = st.chat_input("Type your command (e.g., trigger job, check build status)...")
    if prompt:
        with st.spinner("Processing..."):
            response = process_query(prompt)
            st.write(f"🤖 {response}")

import os
import requests
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_huggingface import HuggingFaceEndpoint
from langchain.agents import initialize_agent, AgentType
from huggingface_hub import InferenceClient
from auth.auth import authenticate
from core.jenkins_operations import JenkinsOperations
from cicd_operations import CICDOperations

# Load environment variables
load_dotenv()

# Required environment variables
JENKINS_BASE_URL = os.getenv("JENKINS_BASE_URL")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Validate required environment variables
missing_env_vars = [
    var for var in ["JENKINS_BASE_URL", "JENKINS_USER", "JENKINS_API_TOKEN", "HUGGINGFACEHUB_API_TOKEN"]
    if not globals()[var]
]
if missing_env_vars:
    raise ValueError(f"\u274c Missing environment variables: {', '.join(missing_env_vars)}. Please check your .env file.")

# Jenkins API Instances
jenkins_api = JenkinsOperations()
cicd_ops = CICDOperations()

# Authentication storage
authenticated_user = None

# Tool Functions
def get_last_build_summary(job_name: str):
    url = f"{JENKINS_BASE_URL}/job/{job_name}/lastBuild/api/json"
    response = requests.get(url, auth=(JENKINS_USER, JENKINS_API_TOKEN))
    
    if response.status_code == 200:
        data = response.json()
        return f"Build #{data['number']} Status: {data['result']} - {data['url']}"
    return f"\u274c Failed to fetch build summary: {response.status_code} - {response.text}"


def get_specific_build_summary(job_name: str, build_number: str):
    url = f"{JENKINS_BASE_URL}/job/{job_name}/{build_number}/api/json"
    response = requests.get(url, auth=(JENKINS_USER, JENKINS_API_TOKEN))
    
    if response.status_code == 200:
        data = response.json()
        return f"Build #{build_number} Status: {data['result']} - {data['url']}"
    return f"\u274c Failed to fetch build summary for build #{build_number}: {response.status_code} - {response.text}"


def get_job_health(job_name: str):
    url = f"{JENKINS_BASE_URL}/job/{job_name}/api/json"
    response = requests.get(url, auth=(JENKINS_USER, JENKINS_API_TOKEN))
    
    if response.status_code == 200:
        data = response.json()
        health_report = data.get("healthReport", [])
        return f"Health Report: {health_report}" if health_report else "\u26a0\ufe0f No health report available."
    return f"\u274c Failed to fetch job health: {response.status_code} - {response.text}"


def trigger_job(job_name: str):
    global authenticated_user
    if not authenticated_user:
        return "\u26a0\ufe0f Authentication required. Please log in."
    return jenkins_api.trigger_job(authenticated_user, job_name, {})



def list_all_jobs(*_):
    """Lists all available Jenkins jobs (User Authentication Applied)."""
    global authenticated_user
    if not authenticated_user:
        return "\u26a0\ufe0f Authentication required. Please log in."

    return jenkins_api.get_all_jobs(authenticated_user)


# Define Tools
tools = [
    Tool(name="List All Jobs", func=list_all_jobs, description="Lists all available Jenkins jobs."),
    Tool(name="Trigger Job", func=trigger_job, description="Triggers a Jenkins job."),
    Tool(name="Get Last Build Summary", func=get_last_build_summary, description="Fetches the last build summary of a Jenkins job."),
    Tool(name="Get Specific Build Summary", func=get_specific_build_summary, description="Fetches a specific build summary of a Jenkins job."),
    Tool(name="Get Job Health", func=get_job_health, description="Checks the health status of a Jenkins job."),
]

# Memory for Conversation
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

chat_history = memory.load_memory_variables({}).get("chat_history", [])
if not isinstance(chat_history, list):
    chat_history = []

# Language Model 
llm = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.1",
    token=HUGGINGFACEHUB_API_TOKEN
)

def query_llm(prompt: str):
    return llm.text_generation(prompt, max_new_tokens=100)

# Initialize AI Agent
agent = initialize_agent(
    tools=tools,
    llm=HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.1", task="text-generation", temperature=0.7, huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN),
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

def process_query(query: str):
    global authenticated_user
    if not authenticated_user:
        return "\u26a0\ufe0f Please authenticate first."
    return agent.run(query)


def main():
    global authenticated_user

    username = input("\U0001F464 Username: ").strip()
    password = input("\U0001F511 Password: ").strip()
    
    auth_result = authenticate(username, password)
    
    if auth_result["status"] == "failed":
        print(f"\u274c {auth_result['message']}")
        return

    authenticated_user = {"username": username, "role": auth_result["role"]}
    print(f"\n✅ Welcome, {username}! You are logged in as '{auth_result['role']}'.")

    print("\n🔹 Jenkins AI Agent is ready. Type 'exit' to quit.\n")

    while True:
        query = input("\n💬 Enter command: ").strip()
        if query.lower() == "exit":
            print("👋 Exiting agent...")
            break
        
        response = process_query(query)
        print(response)


if __name__ == "__main__":
    main()

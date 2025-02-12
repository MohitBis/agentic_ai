import streamlit as st
import requests
from langchain_community.llms import Ollama  # Import Ollama from langchain_community

# Streamlit page configuration
st.set_page_config(page_title="Ollama Chatbot", page_icon="💬", layout="wide")

# Sidebar: Jenkins Authentication Panel
st.sidebar.markdown("<h2>🔐 Jenkins Authentication</h2>", unsafe_allow_html=True)
jenkins_url = st.sidebar.text_input("🌍 Jenkins URL", placeholder="https://your-jenkins.com")
username = st.sidebar.text_input("👤 Username", placeholder="Enter username")
api_key = st.sidebar.text_input("🔑 Jenkins API Key", type="password", placeholder="Enter API key")

# Test Connection Function
def test_jenkins_connection():
    if not jenkins_url or not username or not api_key:
        return "Please enter all details", False
    try:
        response = requests.get(jenkins_url, auth=(username, api_key))
        if response.status_code == 200:
            return "✅ Connected Successfully!", True
        else:
            return f"⚠️ Connection Failed: {response.status_code}", False
    except Exception as e:
        return f"❌ Error: {e}", False

# Test Connection Button
if st.sidebar.button("🔗 Test Connection"):
    message, status = test_jenkins_connection()
    st.sidebar.success(message) if status else st.sidebar.error(message)

# Class to handle individual chat sessions
class ChatSession:
    def __init__(self, session_name):
        self.session_name = session_name
        self.messages = self.get_default_messages()

    def get_default_messages(self):
        return [
            {"role": "system", "content": "<p style='font-size:22px; font-weight:bold;'>Here are some available commands you can use:</p>"},
            {"role": "system", "content": "<button style='font-size:20px; padding:10px; width:100%; text-align:left;' "
                        "onclick='send_command(\"trigger job\")'>⚡ <b>Trigger Job</b>: Starts a job</button>"},
            {"role": "system", "content": "<button style='font-size:20px; padding:10px; width:100%; text-align:left;' "
                        "onclick='send_command(\"last build summary\")'>📊 <b>Last Build Summary</b>: Displays the last build summary</button>"},
            {"role": "system", "content": "<button style='font-size:20px; padding:10px; width:100%; text-align:left;' "
                        "onclick='send_command(\"specific build summary\")'>🔍 <b>Specific Build Summary</b>: Displays a specific build summary</button>"},
            {"role": "system", "content": "<button style='font-size:20px; padding:10px; width:100%; text-align:left;' "
                        "onclick='send_command(\"job health\")'>💡 <b>Job Health</b>: Displays the job's health status</button>"},
            {"role": "system", "content": "<button style='font-size:20px; padding:10px; width:100%; text-align:left;' "
                        "onclick='send_command(\"exit\")'>❌ <b>Exit</b>: Ends the session</button>"},
            {"role": "system", "content": "<script>"
                        "function send_command(cmd) {"
                        "   const inputBox = window.parent.document.querySelector('input[type=\"text\"]');"
                        "   if (inputBox) { inputBox.value = cmd; inputBox.dispatchEvent(new Event('input', { bubbles: true })); }"
                        "}"
                        "</script>"}
        ]

    def reset_user_messages(self):
        self.messages = self.get_default_messages()

# Class to manage chat history
class ChatHistory:
    def __init__(self):
        if "chat_sessions" not in st.session_state:
            st.session_state["chat_sessions"] = {"default": ChatSession("default")}
        if "current_chat" not in st.session_state:
            st.session_state["current_chat"] = "default"

# Class to interact with Ollama model
class OllamaChat:
    def __init__(self, model="llama3.2"):
        self.model = model

    def fetch_response(self, prompt):
        try:
            ollama_llm = Ollama(model=self.model)
            response = ollama_llm.invoke(prompt)
            return response
        except Exception as e:
            return f"Error: {e}"

# Display the main title
st.markdown("<h1 style='text-align: center;'>🤖 Welcome to Ceph CICD bot!</h1>", unsafe_allow_html=True)

# Initialize chat history and session
chat_history = ChatHistory()

# Get current chat session
current_chat_name = st.session_state.current_chat
current_chat = st.session_state.chat_sessions[current_chat_name]

# Check if user has entered any message
user_has_entered_message = any(msg["role"] in ["user", "assistant"] for msg in current_chat.messages)

# Display chat history
for message in current_chat.messages:
    role = message.get("role", "system")
    if role == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif role == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])
    else:
        st.markdown(message["content"], unsafe_allow_html=True)

# Initialize Ollama model
ollama_chat = OllamaChat()

# Chat input
if prompt := st.chat_input("Type your message here..."):
    current_chat.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = ollama_chat.fetch_response(prompt)
            st.markdown(response)
            current_chat.messages.append({"role": "assistant", "content": response})

    st.rerun()

# Show "Clear Chat" button if messages exist
if user_has_entered_message:
    if st.button(f"🗑️ Clear {current_chat_name} Chat", key=f"clear_chat_{current_chat_name}"):
        st.session_state.chat_sessions[current_chat_name].reset_user_messages()
        st.rerun()


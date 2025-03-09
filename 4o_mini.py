import streamlit as st
import requests
import json
import time

# Custom CSS to mimic ChatGPT's look and feel with full-page layout
st.markdown("""
    <style>
    /* Full-page layout */
    .stApp {
        background-color: #343541;
        color: #d1d5db;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        width: 100vw;
        height: 100vh;
        display: flex;
        flex-direction: row;
        overflow: hidden;
    }
    /* Sidebar */
    .stSidebar {
        background-color: #202123;
        padding: 20px;
        width: 300px;
        height: 100%;
        flex-shrink: 0;
    }
    .stSidebar .stTextArea textarea {
        background-color: #40414f;
        color: #d1d5db;
        border: none;
        border-radius: 5px;
        padding: 10px;
    }
    .stSidebar .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
        margin-top: 10px;
    }
    .stSidebar .stButton > button:hover {
        background-color: #0d8c6b;
    }
    /* Main chat area */
    .main-container {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        height: 100vh;
        width: calc(100vw - 300px); /* Adjust for sidebar */
    }
    /* Chat container */
    .chat-container {
        background-color: #40414f;
        border-radius: 10px;
        padding: 20px;
        flex-grow: 1;
        overflow-y: auto;
        margin: 20px 20px 100px 20px;
    }
    /* User message */
    .user-message {
        background-color: #444654;
        color: #d1d5db;
        padding: 12px 18px;
        border-radius: 8px;
        margin: 10px 0;
        max-width: 75%;
        align-self: flex-end;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    /* AI message */
    .ai-message {
        background-color: #343541;
        color: #d1d5db;
        padding: 12px 18px;
        border-radius: 8px;
        margin: 10px 0;
        max-width: 75%;
        align-self: flex-start;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    /* Fixed input box at the bottom */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 300px; /* Adjust for sidebar width */
        right: 0;
        padding: 15px 20px;
        background-color: #343541;
        border-top: 1px solid #40414f;
        display: flex;
        align-items: center;
    }
    .stTextInput > div > input {
        background-color: #40414f;
        color: #d1d5db;
        border: none;
        border-radius: 5px;
        padding: 10px 15px;
        width: 100%;
        flex-grow: 1;
        margin-right: 10px;
    }
    .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        height: 100%;
    }
    .stButton > button:hover {
        background-color: #0d8c6b;
    }
    /* Hide default Streamlit footer */
    .css-1aumxhk {
        display: none;
    }
    /* Hide Streamlit header */
    header {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful AI assistant."

# API Key
API_KEY = "57cd51661e1f4a96b014510837175dca"

# Function to call the AI/ML API
def get_ai_response(user_input):
    try:
        response = requests.post(
            "https://api.aimlapi.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": st.session_state.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 512,
                "temperature": 1.0,
                "top_p": 1.0,
                "stream": False
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response.text:
            try:
                error_detail = response.json()
                error_msg += f" - Details: {json.dumps(error_detail, indent=2)}"
            except ValueError:
                error_msg += f" - Raw response: {response.text}"
        return f"Error: Could not connect to the API - {error_msg}"
    except (KeyError, IndexError) as e:
        return f"Error: Unexpected API response format - {str(e)} (Response: {json.dumps(response.json(), indent=2)})"

# Sidebar for customizing system prompt
with st.sidebar:
    st.header("Settings")
    system_prompt = st.text_area(
        "System Prompt",
        value=st.session_state.system_prompt,
        height=100,
        help="Set the AI's behavior with a custom system prompt."
    )
    if st.button("Update Prompt"):
        st.session_state.system_prompt = system_prompt
        st.success("System prompt updated!")

# Main chat area
main_container = st.container()
with main_container:
    st.title("Kaiwa")
    
    # Chat container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Fixed input box at the bottom
    input_container = st.container()
    with input_container:
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_input("Type your message...", key="user_input", label_visibility="collapsed")
            with col2:
                submit_button = st.form_submit_button(label="Send")

# Handle form submission
if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        ai_response = get_ai_response(user_input)
        time.sleep(0.5)  # Small delay for smoothness
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.rerun()

# Auto-scroll to the bottom of the chat
st.markdown("""
    <script>
    const chatContainer = window.parent.document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    </script>
""", unsafe_allow_html=True)
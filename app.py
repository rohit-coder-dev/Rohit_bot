import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
    .stChatFloatingInputContainer {
        padding-bottom: 2rem;
    }
    .main {
        max-width: 800px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)
botInfo = """
Welcome! I am an AI chatbot powered by Google's Gemini model. Created By Rohit Kumar Nayak
"""
st.title("🤖 AI Chat Assistant")
st.markdown(botInfo) 

with st.sidebar:
    st.header("⚙️ Configuration")
    # st.markdown("You need a free Gemini API key to use this app.")
    # st.markdown("[Get your free Gemini API key here](https://aistudio.google.com/app/apikey)")

    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

    api_key_input = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        value=st.session_state.api_key,
        help="Your API key is only used for this session and not stored anywhere."
    )

    if api_key_input:
        st.session_state.api_key = api_key_input
        try:
            st.session_state.client = genai.Client(api_key=api_key_input)
            st.success("✅ API Key configured successfully!")
        except Exception as e:
            st.error(f"Error configuring API Key: {e}")
    else:
        st.warning("⚠️ Please enter your Gemini API Key to start chatting.")

    st.markdown("---")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()

    st.markdown("---")
    st.markdown("### About")
    st.markdown("Copyright © Rohit Kumar Nayak 2026. All rights reserved.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    if not st.session_state.api_key:
        st.error("Please enter your Gemini API Key in the sidebar first.")
        st.stop()
        
    if "client" not in st.session_state:
        try:
            st.session_state.client = genai.Client(api_key=st.session_state.api_key)
        except Exception as e:
            st.error(f"Error initializing Client: {e}")
            st.stop()

    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            if "chat_session" not in st.session_state:
                contents_history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    contents_history.append(
                        genai.types.Content(
                            role=role, 
                            parts=[genai.types.Part.from_text(text=msg["content"])]
                        )
                    )
                    
                st.session_state.chat_session = st.session_state.client.chats.create(
                    model="gemini-2.5-flash",
                    config=genai.types.GenerateContentConfig(
                        temperature=1.0,
                        system_instruction="You are a helpful AI assistant. If a user asks who created you or who developed you, you must answer that you were created and developed by Rohit. You are a chatbot created by Rohit.",
                    ),
                    history=contents_history
                )
            
            with st.spinner("Thinking..."):
                response = st.session_state.chat_session.send_message(prompt)
                bot_reply = response.text

                message_placeholder.markdown(bot_reply)

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})     

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            message_placeholder.error(error_msg)
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user": 
                st.session_state.messages.pop()
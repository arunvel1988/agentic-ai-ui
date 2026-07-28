import streamlit as st
from agent import agent
from memory import memory

st.set_page_config(
    page_title="Open Source AI Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Open Source AI Agent")

st.caption("Powered by Ollama + Qwen")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
prompt = st.chat_input("Ask me anything...")

if prompt:

    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = agent.ask(prompt)

            st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


st.sidebar.title("Conversation")

if st.sidebar.button("Clear Chat"):

    st.session_state.messages = []

    memory.clear()

    st.rerun()


st.sidebar.markdown("---")

st.sidebar.write("Model : Qwen3:8B")

st.sidebar.write("LLM : Ollama")

st.sidebar.write("Runtime : Python Agent")

st.sidebar.write("Memory : In-Memory")

st.sidebar.markdown("---")

st.sidebar.write("Available Tools")

for tool in sorted(memory.__dict__.keys()):
    pass

from tools import TOOLS

for tool in TOOLS.keys():

    st.sidebar.write(f"• {tool}")

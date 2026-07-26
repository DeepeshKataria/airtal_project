"""
Airtel B2B AI Sales Assistant - Streamlit UI (Phase 5)
"""

import streamlit as st
import os
import logging
from dotenv import load_dotenv

# Suppress Streamlit's local_sources_watcher warnings about torchvision/transformers
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)

# Ensure .env is loaded at the application entry point
load_dotenv()

from src.agent.agent import AirtelAgent
from src.agent.memory import ConversationMemory
import traceback

st.set_page_config(
    page_title="Airtel B2B AI Sales Assistant",
    page_icon="🔴",
    layout="wide",
)

# ─── Initialization ────────────────────────────────────────────────────────────

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "chat_history" not in st.session_state:
    # Full history for UI display (backend memory might truncate)
    st.session_state.chat_history = []

def reset_conversation():
    st.session_state.memory.clear()
    st.session_state.chat_history = []

# Instantiate agent dynamically per run with the shared memory
try:
    agent = AirtelAgent(memory=st.session_state.memory)
    agent_initialized = True
except Exception as e:
    agent_initialized = False
    agent_error = str(e)


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    logo_path = "assets/airtel_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        st.warning("Logo missing. Please place your image at 'assets/airtel_logo.png'.")
    st.title("Settings & Actions")
    if st.button("Clear Conversation", use_container_width=True):
        reset_conversation()
        st.rerun()

    st.markdown("---")
    st.markdown("### Capabilities")
    st.markdown("""
    - **General RAG Q&A**: "How do I pitch Airtel SD-WAN?"
    - **Product Comparison**: "Compare MPLS and SD-WAN."
    - **Meeting Prep**: "Prepare for a meeting with a manufacturing customer."
    - **Objection Handling**: "Your solution is too expensive."
    - **Follow-up Email**: "Draft a follow-up email after the SD-WAN discussion."
    """)

# ─── Main Interface ───────────────────────────────────────────────────────────

st.title("Airtel B2B AI Sales Assistant")
st.caption("Powered by Groq & Llama 3.3 70B")

if not agent_initialized:
    st.error(f"Failed to initialize agent. Ensure your `.env` file is set up properly.\n\nError: {agent_error}")
    st.stop()

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if query := st.chat_input("Ask a question, prepare for a meeting, or handle an objection..."):
    # Append user message to UI
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                result = agent.answer(query)
                
                # Format intent badge
                intent_map = {
                    "retrieve": "📚 RAG Answer",
                    "direct": "💬 Direct",
                    "clarify": "❓ Clarify",
                    "compare": "⚖️ Comparison",
                    "meeting_prep": "📅 Meeting Prep",
                    "objection": "🛡️ Objection Handling",
                    "follow_up": "✉️ Follow-up Email",
                }
                intent_label = intent_map.get(result.get("intent", "unknown"), result.get("intent", "unknown"))
                
                # Construct display output
                output_content = f"**[{intent_label}]**\n\n{result['response']}"
                
                # Add sources if present
                if result.get("sources"):
                    output_content += "\n\n**Sources:**\n"
                    for source in result["sources"]:
                        output_content += f"- [{source}]({source})\n"

                st.markdown(output_content)
                
                # Append to UI history
                st.session_state.chat_history.append({"role": "assistant", "content": output_content})
            
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}\n\n```python\n{traceback.format_exc()}\n```"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

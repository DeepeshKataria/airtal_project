"""
Airtel Business AI Assistant — Streamlit Frontend
"""

import streamlit as st
import os
import logging
from dotenv import load_dotenv

logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)
load_dotenv()

from src.agent.agent import AirtelAgent
from src.agent.memory import ConversationMemory
import traceback

st.set_page_config(
    page_title="Airtel Business AI",
    page_icon="assets/airtel_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Font ─────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Chat avatars ─────────────────────────────────────────────────────── */
div[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarCustom"],
div[data-testid="stChatMessage"] .stChatMessageAvatar,
div[data-testid="stChatMessage"] [class*="Avatar"] {
    font-size: 0 !important;
    overflow: hidden;
}

div[data-testid="stChatMessage"] img[data-testid="chatAvatarIcon-assistant"],
div[data-testid="stChatMessage"] img[data-testid="chatAvatarIcon-user"] {
    display: none !important;
}

/* Force avatar containers to show clean text */
div[data-testid="stChatMessage"] > div:first-child > div:first-child {
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    border-radius: 6px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    line-height: 1 !important;
    flex-shrink: 0 !important;
    margin-top: 2px !important;
}

/* ── Hide Streamlit defaults ──────────────────────────────────────────── */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
div[data-testid="stToolbar"] {display: none;}
div[data-testid="stDecoration"] {display: none;}
div[data-testid="stStatusWidget"] {display: none;}

/* ── Root overrides ───────────────────────────────────────────────────── */
.stApp {
    background-color: #0a0a0a;
}

section[data-testid="stSidebar"] {
    background-color: #0f0f0f;
    border-right: 1px solid #1e1e1e;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] > div {
    padding-top: 0;
}

/* ── Typography ───────────────────────────────────────────────────────── */
h1 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #f5f5f5 !important;
}

h2, h3 {
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    color: #e5e5e5 !important;
}

p, li, span {
    color: #d4d4d4;
    line-height: 1.65;
}

/* ── Sidebar styling ──────────────────────────────────────────────────── */
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 13px;
    color: #a3a3a3;
    margin-bottom: 4px;
}

section[data-testid="stSidebar"] h1 {
    font-size: 18px !important;
    margin-bottom: 2px !important;
    color: #f5f5f5 !important;
}

section[data-testid="stSidebar"] h3 {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #737373 !important;
    margin-top: 14px !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}

/* ── Sidebar status card ──────────────────────────────────────────────── */
.status-card {
    background: #141414;
    border: 1px solid #262626;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 8px 0;
}

.status-card .status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    font-size: 12.5px;
}

.status-card .status-label {
    color: #737373;
    font-weight: 500;
}

.status-card .status-value {
    color: #d4d4d4;
    font-weight: 500;
}

.status-card .status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 6px;
    box-shadow: 0 0 6px rgba(34, 197, 94, 0.4);
}

/* ── Sidebar action buttons ───────────────────────────────────────────── */
section[data-testid="stSidebar"] .stButton > button {
    background: #141414;
    color: #e5e5e5;
    border: 1px solid #262626;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    padding: 7px 0;
    width: 100%;
    transition: all 0.15s ease;
    cursor: pointer;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1c1c1c;
    border-color: #3a3a3a;
    color: #ffffff;
    transform: translateY(-1px);
}

section[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(0);
}

/* ── Sidebar quick-action items ───────────────────────────────────────── */
.quick-action {
    display: block;
    padding: 8px 12px;
    margin: 3px 0;
    border-radius: 6px;
    font-size: 12.5px;
    color: #a3a3a3;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    border: none;
    background: transparent;
}

.quick-action:hover {
    background: #1a1a1a;
    color: #e5e5e5;
}

/* ── Landing hero ─────────────────────────────────────────────────────── */
.landing-hero {
    text-align: center;
    padding: 48px 0 16px 0;
    max-width: 680px;
    margin: 0 auto;
}

.landing-hero h1 {
    font-size: 32px !important;
    font-weight: 700 !important;
    color: #f5f5f5 !important;
    margin-bottom: 8px !important;
    letter-spacing: -0.03em !important;
}

.landing-hero .subtitle {
    font-size: 14.5px;
    color: #737373;
    margin-bottom: 40px;
    line-height: 1.5;
}

.landing-hero .accent-dot {
    color: #ED1C24;
}

/* ── Prompt cards ─────────────────────────────────────────────────────── */
.prompt-card {
    background: #141414;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.15s ease;
    height: 100%;
    min-height: 100px;
    display: flex;
    flex-direction: column;
}

.prompt-card:hover {
    border-color: #333333;
    background: #191919;
    transform: translateY(-1px);
}

.prompt-card .card-icon {
    font-size: 16px;
    margin-bottom: 8px;
    display: block;
}

.prompt-card .card-title {
    font-size: 13px;
    font-weight: 600;
    color: #e5e5e5;
    margin-bottom: 5px;
    line-height: 1.35;
}

.prompt-card .card-desc {
    font-size: 11.5px;
    color: #737373;
    line-height: 1.4;
    margin-top: auto;
}

/* ── Chat area ────────────────────────────────────────────────────────── */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 14px 0 !important;
    max-width: 860px;
}

/* User message */
div[data-testid="stChatMessage"][data-testid-role="user"] {
    background: transparent !important;
}

/* Assistant message */
div[data-testid="stChatMessage"]:not([data-testid-role="user"]) {
    background: transparent !important;
}

div[data-testid="stChatMessage"] .stMarkdown {
    font-size: 14px;
    line-height: 1.75;
}

div[data-testid="stChatMessage"] .stMarkdown p {
    color: #d4d4d4;
    margin-bottom: 10px;
}

div[data-testid="stChatMessage"] .stMarkdown h1 {
    font-size: 20px !important;
    margin-top: 20px !important;
    margin-bottom: 10px !important;
}

div[data-testid="stChatMessage"] .stMarkdown h2 {
    font-size: 17px !important;
    margin-top: 18px !important;
    margin-bottom: 8px !important;
}

div[data-testid="stChatMessage"] .stMarkdown h3 {
    font-size: 15px !important;
    margin-top: 16px !important;
    margin-bottom: 6px !important;
}

div[data-testid="stChatMessage"] .stMarkdown ul,
div[data-testid="stChatMessage"] .stMarkdown ol {
    margin: 10px 0;
    padding-left: 22px;
}

div[data-testid="stChatMessage"] .stMarkdown li {
    margin-bottom: 5px;
    line-height: 1.7;
}

div[data-testid="stChatMessage"] .stMarkdown code {
    background: #1e1e1e;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
    color: #e5e5e5;
}

div[data-testid="stChatMessage"] .stMarkdown pre {
    background: #141414 !important;
    border: 1px solid #262626;
    border-radius: 8px;
    padding: 16px !important;
    margin: 12px 0 !important;
}

div[data-testid="stChatMessage"] .stMarkdown table {
    margin: 12px 0;
    border-collapse: collapse;
    width: 100%;
}

div[data-testid="stChatMessage"] .stMarkdown th,
div[data-testid="stChatMessage"] .stMarkdown td {
    padding: 8px 12px;
    border: 1px solid #262626;
    font-size: 13px;
}

div[data-testid="stChatMessage"] .stMarkdown th {
    background: #171717;
    font-weight: 600;
    color: #e5e5e5;
}

div[data-testid="stChatMessage"] .stMarkdown strong {
    color: #e5e5e5;
    font-weight: 600;
}

/* ── Intent badge ─────────────────────────────────────────────────────── */
.intent-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
    margin-bottom: 12px;
    text-transform: uppercase;
}

.intent-retrieve { background: #1a2332; color: #60a5fa; border: 1px solid #1e3a5f; }
.intent-direct { background: #1a2e1a; color: #86efac; border: 1px solid #1e4620; }
.intent-clarify { background: #2e2a1a; color: #fde68a; border: 1px solid #4a3f1e; }
.intent-compare { background: #2a1a2e; color: #c4b5fd; border: 1px solid #3b1e4a; }
.intent-meeting { background: #1a2e2e; color: #67e8f9; border: 1px solid #1e4a4a; }
.intent-objection { background: #2e1a1a; color: #fca5a5; border: 1px solid #4a1e1e; }
.intent-email { background: #1e2a1a; color: #a3e635; border: 1px solid #2e4a1e; }

/* ── Source chips ─────────────────────────────────────────────────────── */
.source-section {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid #1e1e1e;
}

.source-section .source-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #525252;
    margin-bottom: 8px;
}

.source-chip {
    display: inline-block;
    padding: 4px 10px;
    background: #141414;
    border: 1px solid #262626;
    border-radius: 4px;
    font-size: 11.5px;
    color: #a3a3a3;
    margin: 3px 4px 3px 0;
    text-decoration: none;
    transition: all 0.2s ease;
    max-width: 280px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.source-chip:hover {
    border-color: #404040;
    color: #d4d4d4;
}

/* ── Chat input ───────────────────────────────────────────────────────── */
div[data-testid="stChatInput"] {
    max-width: 860px;
}

div[data-testid="stChatInput"] textarea {
    background: #141414 !important;
    border: 1px solid #262626 !important;
    border-radius: 10px !important;
    color: #e5e5e5 !important;
    font-size: 14px !important;
    padding: 14px 16px !important;
}

div[data-testid="stChatInput"] textarea:focus {
    border-color: #404040 !important;
    box-shadow: none !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #525252 !important;
}

/* ── Error styling ────────────────────────────────────────────────────── */
.stAlert {
    background: #1a1111 !important;
    border: 1px solid #3d1515 !important;
    border-radius: 8px !important;
    color: #fca5a5 !important;
}

/* ── Thinking indicator ───────────────────────────────────────────────── */
.thinking-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #737373;
    font-size: 13px;
    padding: 8px 0;
}

.thinking-dots {
    display: flex;
    gap: 3px;
}

.thinking-dots span {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #525252;
    animation: thinking 1.4s infinite ease-in-out;
}

.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes thinking {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40% { transform: scale(1); opacity: 1; }
}

/* ── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #262626; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #404040; }

/* ── Divider override ─────────────────────────────────────────────────── */
hr {
    border-color: #1e1e1e !important;
    margin: 12px 0 !important;
}

/* ── Sidebar logo constraint ──────────────────────────────────────────── */
section[data-testid="stSidebar"] img {
    max-width: 100px;
    margin-bottom: 4px;
}

/* ── Column gap fix for prompt cards ──────────────────────────────────── */
div[data-testid="stHorizontalBlock"] {
    gap: 12px;
}

</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


def reset_conversation():
    st.session_state.memory.clear()
    st.session_state.chat_history = []


# Agent initialization
try:
    agent = AirtelAgent(memory=st.session_state.memory)
    agent_ready = True
except Exception as e:
    agent_ready = False
    agent_error = str(e)


# ── Sidebar ───────────────────────────────────────────────────────────────────

AIRTEL_LOGO_SVG = """
<svg width="90" height="32" viewBox="0 0 256 92" xmlns="http://www.w3.org/2000/svg">
  <g fill="#ED1C24">
    <path d="M67.6,7.1C55.5-3,37.5-2.3,26.1,8.5c-5.4,5.1-8.6,11.7-9.5,18.7c-0.5,3.5-0.3,7.1,0.5,10.6 c1.4,5.7,4.5,10.8,9.1,14.7c5.3,4.5,11.6,6.7,18.2,6.7c5,0,10.2-1.3,15-4.1c-12.4,1.8-23.6-5.9-26.5-17.2 c-1.7-6.5-0.5-13.2,3.3-18.8c3.8-5.6,9.6-9.2,16.3-10.1C59.1,8,65.1,10.1,69.7,14c4.6,3.9,7.4,9.3,7.9,15.2 c0.5,5.9-1.3,11.7-5.2,16.3c-5.5,6.6-13.8,9.4-21.5,8.6c8.9,5.2,20.5,4.3,28.4-3.1C90,40.5,89.3,24.3,67.6,7.1z"/>
    <path d="M105.3,25.5h-8.6l-16.2,46.9h8.6l3.8-11.5h16.1l3.9,11.5h8.8L105.3,25.5z M95.1,54.4l6-18.2l6.1,18.2H95.1z"/>
    <path d="M127.2,32.4c-2.3,0-4.2,1.9-4.2,4.2c0,2.3,1.9,4.2,4.2,4.2c2.3,0,4.2-1.9,4.2-4.2C131.4,34.3,129.5,32.4,127.2,32.4z"/>
    <rect x="123.2" y="43.6" width="8" height="28.8"/>
    <path d="M152.5,43.1c-3.1,0-5.8,1.1-7.8,3.2v-2.7h-7.6v28.8h8v-15c0-4.6,2.5-7.2,6.2-7.2v-7.1C153.4,43.1,152.8,43.1,152.5,43.1z"/>
    <path d="M171.7,50.5v-6.9h-6.4v-9.4l-8,2.7v6.7h-4.8v6.9h4.8v12.7c0,6.6,3.7,9.8,10.8,9.2v-6.7c-2.8,0.2-2.8-1.3-2.8-2.8V50.5H171.7z"/>
    <path d="M195.1,55.4c0-7.2-5.6-12.8-13.1-12.8c-7.7,0-13.5,5.7-13.5,13c0,7.5,5.8,13.1,13.9,13.1c5.2,0,9.5-2.5,11.6-6.5 l-6.7-2c-1.3,1.7-3,2.6-5.1,2.6c-3.5,0-5.8-1.8-6.4-5.1h19.2C195.1,56.9,195.1,56.1,195.1,55.4z M176,54.1 c0.6-3.1,2.8-4.9,5.8-4.9c3.1,0,5.2,1.9,5.5,4.9H176z"/>
    <rect x="199.5" y="25.5" width="8" height="46.9"/>
  </g>
</svg>
"""

with st.sidebar:
    st.markdown(AIRTEL_LOGO_SVG, unsafe_allow_html=True)

    st.markdown("# Airtel Business AI")
    st.markdown("Sales assistant for B2B account managers.")

    st.markdown("---")

    if st.button("↻  New conversation", use_container_width=True):
        reset_conversation()
        st.rerun()

    # Status card
    turns_used = len(st.session_state.memory) // 2
    status_color = "#22c55e" if agent_ready else "#ef4444"
    status_text = "Online" if agent_ready else "Offline"

    st.markdown(f"""
    <div class="status-card">
        <div class="status-row">
            <span class="status-label">AI Assistant</span>
            <span class="status-value"><span class="status-dot" style="background:{status_color}; box-shadow: 0 0 6px {status_color}40;"></span>{status_text}</span>
        </div>
        <div class="status-row">
            <span class="status-label">Knowledge Base</span>
            <span class="status-value"><span class="status-dot"></span>Connected</span>
        </div>
        <div class="status-row">
            <span class="status-label">Context</span>
            <span class="status-value">{turns_used} / 6 turns</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Quick prompts")

    sidebar_prompts = [
        "Compare SD-WAN vs MPLS",
        "Prepare for a customer meeting",
        "Draft a follow-up email",
        "Pitch Airtel Cloud solutions",
        "Handle a pricing objection",
    ]

    for prompt_text in sidebar_prompts:
        if st.button(prompt_text, key=f"sb_{prompt_text}", use_container_width=True):
            st.session_state.pending_prompt = prompt_text
            st.rerun()


# ── Intent display helpers ────────────────────────────────────────────────────

INTENT_CONFIG = {
    "retrieve":     ("RAG",         "intent-retrieve"),
    "direct":       ("Direct",      "intent-direct"),
    "clarify":      ("Clarify",     "intent-clarify"),
    "compare":      ("Compare",     "intent-compare"),
    "meeting_prep": ("Meeting",     "intent-meeting"),
    "objection":    ("Objection",   "intent-objection"),
    "follow_up":    ("Email",       "intent-email"),
}


def format_intent_badge(intent: str) -> str:
    label, css_class = INTENT_CONFIG.get(intent, (intent, "intent-retrieve"))
    return f'<div class="intent-badge {css_class}">{label}</div>'


def format_sources(sources: list) -> str:
    if not sources:
        return ""
    chips = ""
    for url in sources:
        # Extract a readable label from the URL path
        short = url.replace("https://", "").replace("http://", "")
        # Show just the meaningful path segment
        parts = short.rstrip("/").split("/")
        if len(parts) > 2:
            short = parts[0] + "/…/" + parts[-1]
        if len(short) > 40:
            short = short[:37] + "…"
        chips += f'<a href="{url}" target="_blank" class="source-chip">↗ {short}</a>'
    return f'<div class="source-section"><div class="source-label">Sources</div>{chips}</div>'


# ── Main area ─────────────────────────────────────────────────────────────────

if not agent_ready:
    st.error(f"Could not connect to the AI model. Check your `.env` configuration.\n\n{agent_error}")
    st.stop()


# Landing state — shown when there's no conversation yet
if not st.session_state.chat_history and st.session_state.pending_prompt is None:
    st.markdown("""
    <div class="landing-hero">
        <h1>Airtel Business AI<span class="accent-dot">.</span></h1>
        <p class="subtitle">Ask about Airtel B2B products, compare solutions, prepare for meetings, handle objections, or draft follow-up emails.</p>
    </div>
    """, unsafe_allow_html=True)

    # Prompt card data
    cards = [
        {
            "icon": "⇄",
            "title": "Compare SD-WAN and MPLS",
            "desc": "Side-by-side analysis for enterprise networking decisions",
            "prompt": "Compare SD-WAN and MPLS for enterprise networking",
        },
        {
            "icon": "◎",
            "title": "Prepare for a client meeting",
            "desc": "Briefing notes for a manufacturing sector prospect",
            "prompt": "Prepare for a meeting with a manufacturing customer",
        },
        {
            "icon": "✉",
            "title": "Draft a follow-up email",
            "desc": "Professional email after an SD-WAN product demo",
            "prompt": "Draft a follow-up email after the SD-WAN discussion",
        },
        {
            "icon": "△",
            "title": "Pitch Airtel Cloud",
            "desc": "Talking points for a mid-size company pitch",
            "prompt": "How should I pitch Airtel Cloud to a mid-size company?",
        },
        {
            "icon": "◇",
            "title": "Handle a pricing objection",
            "desc": "Rebuttals when a customer says your solution is too expensive",
            "prompt": "The customer says your solution is too expensive",
        },
    ]

    # Render prompt cards in a row
    cols = st.columns(len(cards), gap="small")
    for i, card in enumerate(cards):
        with cols[i]:
            st.markdown(f"""
            <div class="prompt-card">
                <span class="card-icon">{card["icon"]}</span>
                <div class="card-title">{card["title"]}</div>
                <div class="card-desc">{card["desc"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Use →", key=f"card_{i}", use_container_width=True):
                st.session_state.pending_prompt = card["prompt"]
                st.rerun()


# Display chat history
for msg in st.session_state.chat_history:
    avatar = "AI" if msg["role"] == "assistant" else "You"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"], unsafe_allow_html=True)


# ── Process input ─────────────────────────────────────────────────────────────

# Determine input source: chat input or pending prompt card click
query = st.chat_input("Ask about Airtel products, prepare for meetings...")

if st.session_state.pending_prompt:
    query = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if query:
    # Append and render user message
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="You"):
        st.markdown(query)

    # Generate response
    with st.chat_message("assistant", avatar="AI"):
        # Thinking indicator
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("""
        <div class="thinking-indicator">
            <div class="thinking-dots"><span></span><span></span><span></span></div>
            Thinking
        </div>
        """, unsafe_allow_html=True)

        try:
            result = agent.answer(query)

            # Clear thinking indicator
            thinking_placeholder.empty()

            # Build formatted response
            intent = result.get("intent", "retrieve")
            badge_html = format_intent_badge(intent)
            response_body = result["response"]
            sources_html = format_sources(result.get("sources", []))

            display_content = f'{badge_html}\n\n{response_body}\n\n{sources_html}'

            st.markdown(display_content, unsafe_allow_html=True)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": display_content,
            })

        except Exception as e:
            thinking_placeholder.empty()
            error_msg = f"Something went wrong.\n\n```\n{traceback.format_exc()}\n```"
            st.error(error_msg)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_msg,
            })

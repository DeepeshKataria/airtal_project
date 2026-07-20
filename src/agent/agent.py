"""
Airtel B2B AI Sales Assistant — Agent Loop (Phase 3)

Decision logic:
  - RETRIEVE  → product/solution/technical questions needing Airtel-specific knowledge
  - DIRECT    → greetings, meta questions, general knowledge with no Airtel specifics needed
  - CLARIFY   → ambiguous requests where the intent is unclear
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.rag.retriever import retrieve_similar_chunks

# ── Configuration ─────────────────────────────────────────────────────────────

load_dotenv(dotenv_path=Path(__file__).parents[2] / ".env", override=True)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not found. Set it in your .env file (see .env.example)."
    )

MODEL_NAME = "llama-3.3-70b-versatile"   # Groq's latest Llama 3.3 70B
TOP_K = 4                                 # chunks to retrieve per query
MIN_RELEVANCE_SCORE = 0.45               # below this → treat as out-of-scope

PROMPTS_DIR = Path(__file__).parents[1] / "prompts"


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


# Preload prompt templates once
_SYSTEM_PROMPT = _load_prompt("system_prompt.md")
_RAG_PROMPT_TPL = _load_prompt("rag_prompt.md")


def _get_llm() -> ChatGroq:
    return ChatGroq(
        model=MODEL_NAME,
        temperature=0,
        api_key=GROQ_API_KEY,
    )


# ── Intent classification ─────────────────────────────────────────────────────

# Keywords that clearly signal a need for Airtel-specific retrieval
_RETRIEVE_SIGNALS = re.compile(
    r"""(
        airtel|sd.wan|mpls|iot|cpaas|broadband|5g|leased.line|
        internet|cloud|data.cent(re|er)|security|cyber|
        colocation|isoc|spam|voice|sip|toll.free|
        pitch|pitch\s+airtel|compare|comparison|competitor|vs\.?|versus|
        meeting.prep|meeting\s+prep|prepare\s+for|
        customer|enterprise|solution|product|feature|benefit|
        pricing|price|cost|tariff|plan|package|offer|
        deploy|rollout|bandwidth|latency|uptime|sla|
        objection|follow.?up|email|proposal|
        retail|manufacturing|banking|telecom|logistics|travel|energy
    )""",
    re.VERBOSE | re.IGNORECASE,
)

# Clear DIRECT signals — small talk, meta, greetings
_DIRECT_SIGNALS = re.compile(
    r"^(hi|hello|hey|good\s+(morning|afternoon|evening)|thanks|thank you|"
    r"what (can|do) you do|who are you|help me|what is your (name|role)|okay|ok|sure|great)\b",
    re.IGNORECASE,
)


def classify_intent(query: str) -> str:
    """
    Returns one of: 'retrieve', 'direct', 'clarify'
    """
    q = query.strip()
    # Very short with no Airtel signal → possibly ambiguous
    if len(q) < 12 and not _RETRIEVE_SIGNALS.search(q):
        return "clarify"
    if _DIRECT_SIGNALS.match(q) and not _RETRIEVE_SIGNALS.search(q):
        return "direct"
    if _RETRIEVE_SIGNALS.search(q):
        return "retrieve"
    # Default: if we can't decide, retrieve anyway — retrieval is cheap and safe
    return "retrieve"


# ── Context builder ───────────────────────────────────────────────────────────

def _build_context(chunks: list[dict]) -> tuple[str, list[str]]:
    """Returns (formatted_context_string, list_of_unique_source_urls)"""
    if not chunks:
        return "", []

    context_parts = []
    seen_urls: list[str] = []
    for c in chunks:
        url = c.get("source_url", "")
        context_parts.append(
            f"[Source: {url}]\n{c['text']}"
        )
        if url and url not in seen_urls:
            seen_urls.append(url)

    return "\n\n---\n\n".join(context_parts), seen_urls


# ── Main agent ────────────────────────────────────────────────────────────────

class AirtelAgent:
    """
    Stateless single-turn agent for Phase 3.
    Phase 4 will add multi-turn memory.
    """

    def __init__(self):
        self._llm = _get_llm()

    def answer(self, query: str) -> dict:
        """
        Process a user query and return:
          {
            "intent":   "retrieve" | "direct" | "clarify",
            "response": str,
            "sources":  list[str],
            "chunks":   list[dict],
          }
        """
        intent = classify_intent(query)

        if intent == "direct":
            return self._direct_answer(query)
        if intent == "clarify":
            return self._clarify(query)
        return self._rag_answer(query)

    # -- helpers ---------------------------------------------------------------

    def _direct_answer(self, query: str) -> dict:
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]
        response = self._llm.invoke(messages)
        return {
            "intent": "direct",
            "response": response.content,
            "sources": [],
            "chunks": [],
        }

    def _clarify(self, query: str) -> dict:
        clarify_prompt = (
            "The user sent a very short or ambiguous request. "
            "Ask ONE focused clarifying question to understand what Airtel B2B product "
            "or use case they need help with.\n\nUser message: " + query
        )
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=clarify_prompt),
        ]
        response = self._llm.invoke(messages)
        return {
            "intent": "clarify",
            "response": response.content,
            "sources": [],
            "chunks": [],
        }

    def _rag_answer(self, query: str) -> dict:
        chunks = retrieve_similar_chunks(query, k=TOP_K)

        # Check if top result is relevant enough
        if not chunks or chunks[0]["score"] < MIN_RELEVANCE_SCORE:
            return {
                "intent": "retrieve",
                "response": (
                    "I don't have verified information about that topic in the "
                    "Airtel B2B documentation. Please check "
                    "https://www.airtel.in/b2b/ or contact your Airtel account team."
                ),
                "sources": [],
                "chunks": chunks,
            }

        context_str, source_urls = _build_context(chunks)
        rag_user_msg = _RAG_PROMPT_TPL.format(
            context=context_str,
            question=query,
        )

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=rag_user_msg),
        ]
        response = self._llm.invoke(messages)
        return {
            "intent": "retrieve",
            "response": response.content,
            "sources": source_urls,
            "chunks": chunks,
        }


def ask(query: str) -> dict:
    """Convenience function — creates a one-shot agent and returns the result."""
    return AirtelAgent().answer(query)

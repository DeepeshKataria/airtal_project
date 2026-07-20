"""
Airtel B2B AI Sales Assistant — Agent Loop (Phase 3 + Phase 4)

Decision logic:
  - RETRIEVE       → product/solution/technical questions needing Airtel-specific knowledge
  - DIRECT         → greetings, meta questions, general knowledge with no Airtel specifics needed
  - CLARIFY        → ambiguous requests where the intent is unclear
  - COMPARE        → requests to compare two Airtel products/technologies  [Phase 4]
  - MEETING_PREP   → requests to prepare for a customer meeting            [Phase 4]
  - OBJECTION      → customer objections to handle                         [Phase 4]
  - FOLLOW_UP      → requests to draft a follow-up email                   [Phase 4]
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
from src.agent.memory import ConversationMemory
from src.agent.tools import (
    compare_products,
    meeting_prep,
    handle_objection,
    draft_followup_email,
)

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


# ── Tool-routing patterns (Phase 4) — checked BEFORE generic retrieve ─────────

# compare: "compare X and Y", "X vs Y", "difference between X and Y"
_COMPARE_SIGNALS = re.compile(
    r"(compare|comparison|vs\.?|versus|difference.between|how.does.+differ)",
    re.IGNORECASE,
)

# meeting prep: "prepare for", "meeting with", "meeting prep for"
_MEETING_SIGNALS = re.compile(
    r"(prepare\s+for|meeting\s+with|meeting\s+prep|pre-?meeting|brief\s+me|brief\s+for)",
    re.IGNORECASE,
)

# objection: explicit objection keywords
_OBJECTION_SIGNALS = re.compile(
    r"(objection|too\s+expensive|too\s+costly|too\s+complex|not\s+worth|"
    r"why\s+should\s+we|vendor\s+lock|migration\s+risk|downtime|switching\s+cost)",
    re.IGNORECASE,
)

# follow-up email: draft / write / send email after a meeting
_EMAIL_SIGNALS = re.compile(
    r"(follow.?up\s+email|draft.+email|write.+email|send.+email|email\s+after|"
    r"post.?meeting\s+email|meeting\s+summary\s+email)",
    re.IGNORECASE,
)

# Keywords that clearly signal a need for Airtel-specific retrieval
_RETRIEVE_SIGNALS = re.compile(
    r"""(
        airtel|sd.wan|mpls|iot|cpaas|broadband|5g|leased.line|
        internet|cloud|data.cent(re|er)|security|cyber|
        colocation|isoc|spam|voice|sip|toll.free|
        pitch|pitch\s+airtel|
        customer|enterprise|solution|product|feature|benefit|
        pricing|price|cost|tariff|plan|package|offer|
        deploy|rollout|bandwidth|latency|uptime|sla|
        proposal|
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
    Returns one of: 'retrieve', 'direct', 'clarify', 'compare',
                    'meeting_prep', 'objection', 'follow_up'

    Tool-routing intents (compare, meeting_prep, objection, follow_up) are
    checked first so they take priority over the generic 'retrieve' branch.
    """
    q = query.strip()
    # ── Phase 4 tool intents (highest priority) ──────────────────────────────
    if _EMAIL_SIGNALS.search(q):
        return "follow_up"
    if _COMPARE_SIGNALS.search(q):
        return "compare"
    if _MEETING_SIGNALS.search(q):
        return "meeting_prep"
    if _OBJECTION_SIGNALS.search(q):
        return "objection"
    # ── Phase 3 intents ───────────────────────────────────────────────────────
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
    Stateful multi-turn agent (Phase 3 + Phase 4).

    - Maintains in-process conversation memory (ConversationMemory).
    - Routes to specialised tool functions for Phase 4 features.
    - Preserves all Phase 3 RAG answer, direct answer, and clarify paths.

    Instantiate once per conversation session; call .answer() repeatedly.
    """

    def __init__(self, memory: Optional[ConversationMemory] = None):
        self._llm = _get_llm()
        # Memory is injected so callers can share, persist, or replace it
        self.memory: ConversationMemory = memory or ConversationMemory()

    def answer(self, query: str, **tool_kwargs) -> dict:
        """
        Process a user query and return:
          {
            "intent":   str,
            "response": str,
            "sources":  list[str],
            "chunks":   list[dict],
          }

        Extra keyword arguments are forwarded to Phase 4 tool functions
        (e.g. customer=, industry=, objection=, solutions=, next_steps=).
        """
        intent = classify_intent(query)

        # ── Phase 4 tool routing ─────────────────────────────────────────────
        if intent == "compare":
            result = self._tool_compare(query, **tool_kwargs)
        elif intent == "meeting_prep":
            result = self._tool_meeting_prep(query, **tool_kwargs)
        elif intent == "objection":
            result = self._tool_objection(query, **tool_kwargs)
        elif intent == "follow_up":
            result = self._tool_follow_up(query, **tool_kwargs)
        # ── Phase 3 paths ────────────────────────────────────────────────────
        elif intent == "direct":
            result = self._direct_answer(query)
        elif intent == "clarify":
            result = self._clarify(query)
        else:
            result = self._rag_answer(query)

        # Persist turn in memory regardless of intent
        self.memory.add_human(query)
        self.memory.add_ai(result["response"])
        return result

    # -- Phase 3 helpers -------------------------------------------------------

    def _build_messages(self, user_content: str) -> list:
        """Prepend history from memory before the new user message."""
        return [
            SystemMessage(content=_SYSTEM_PROMPT),
            *self.memory.messages,
            HumanMessage(content=user_content),
        ]

    def _direct_answer(self, query: str) -> dict:
        messages = self._build_messages(query)
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
        messages = self._build_messages(clarify_prompt)
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
        messages = self._build_messages(rag_user_msg)
        response = self._llm.invoke(messages)
        return {
            "intent": "retrieve",
            "response": response.content,
            "sources": source_urls,
            "chunks": chunks,
        }

    # -- Phase 4 tool dispatchers ---------------------------------------------
    # These extract parameters from the query text when not explicitly provided.

    def _tool_compare(self, query: str, product_a: str = "", product_b: str = "", **_) -> dict:
        # Attempt to parse "X vs Y" or "compare X and Y" from the query
        if not (product_a and product_b):
            m = re.search(
                r"(?:compare\s+)?(.+?)\s+(?:vs\.?|versus|and|compared?\s+to)\s+(.+)",
                query, re.IGNORECASE,
            )
            if m:
                product_a = m.group(1).strip()
                product_b = m.group(2).strip()
            else:
                product_a, product_b = product_a or "SD-WAN", product_b or "MPLS"
        result = compare_products(product_a, product_b, self._llm)
        result["intent"] = "compare"
        return result

    def _tool_meeting_prep(
        self, query: str,
        customer: str = "",
        industry: str = "",
        **_,
    ) -> dict:
        if not industry:
            # Try to extract industry from query (e.g. "meeting with a retail company")
            m = re.search(
                r"(?:with\s+(?:a\s+)?|for\s+(?:a\s+)?)([\w\s]+?)(?:\s+company|\s+customer|\s+client|\s+enterprise|$)",
                query, re.IGNORECASE,
            )
            industry = m.group(1).strip() if m else "enterprise"
        result = meeting_prep(customer or "Prospect", industry, self._llm)
        result["intent"] = "meeting_prep"
        return result

    def _tool_objection(
        self, query: str,
        product_context: str = "Airtel B2B solutions",
        **_,
    ) -> dict:
        result = handle_objection(query, self._llm, product_context=product_context)
        result["intent"] = "objection"
        return result

    def _tool_follow_up(
        self, query: str,
        customer: str = "the customer",
        solutions: str = "",
        next_steps: str = "",
        meeting_context: str = "",
        **_,
    ) -> dict:
        if not solutions:
            # Pull solutions from recent memory if available
            history_text = " ".join(
                m.content for m in self.memory.messages
            )
            m = re.search(
                r"(SD-WAN|MPLS|ILL|IoT|CPaaS|Cloud|5G|Cybersecurity)",
                history_text, re.IGNORECASE,
            )
            solutions = m.group(1) if m else "Airtel B2B solutions"
        result = draft_followup_email(
            customer, solutions,
            next_steps or "Schedule a technical demo",
            self._llm,
            meeting_context=meeting_context,
        )
        result["intent"] = "follow_up"
        return result


def ask(query: str, memory: Optional[ConversationMemory] = None, **tool_kwargs) -> dict:
    """
    Convenience function for one-shot queries.
    Pass `memory` to maintain session state across multiple calls.
    """
    return AirtelAgent(memory=memory).answer(query, **tool_kwargs)

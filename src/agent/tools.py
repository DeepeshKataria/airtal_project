"""
Phase 4 Sales Tools — four independently callable functions.

Each function:
  1. Retrieves relevant documentation via the existing RAG retriever.
  2. Builds a structured prompt from src/prompts/.
  3. Calls the LLM and returns a typed result dict.

All functions accept an `llm` parameter so the caller (AirtelAgent) can
pass its already-initialised ChatGroq instance — avoiding repeated model
loading in the hot path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.messages import SystemMessage, HumanMessage

from src.rag.retriever import retrieve_similar_chunks
from src.agent.utils import _build_context

PROMPTS_DIR = Path(__file__).parents[1] / "prompts"


def _load(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


# ── System prompt (shared across all tools) ───────────────────────────────────

_SYSTEM_PROMPT = _load("system_prompt.md")


# ── Tool 1: Product Comparison ────────────────────────────────────────────────

def compare_products(
    product_a: str,
    product_b: str,
    llm: Any,
    top_k: int = 5,
) -> dict:
    """
    Compare two Airtel B2B products using retrieved documentation only.

    Returns::

        {
            "product_a":  str,
            "product_b":  str,
            "response":   str,
            "sources":    list[str],
            "chunks":     list[dict],
        }
    """
    # Retrieve for both products combined for richer context
    query = f"Compare {product_a} and {product_b} Airtel B2B features benefits differences"
    chunks_a = retrieve_similar_chunks(product_a, k=top_k)
    chunks_b = retrieve_similar_chunks(product_b, k=top_k)
    # Merge, dedupe by chunk_id
    seen_ids: set[str] = set()
    merged_chunks = []
    for c in chunks_a + chunks_b:
        cid = c.get("chunk_id", c.get("text", "")[:40])
        if cid not in seen_ids:
            seen_ids.add(cid)
            merged_chunks.append(c)

    context_str, source_urls = _build_context(merged_chunks[:top_k * 2])

    template = _load("comparison_prompt.md")
    user_msg = template.format(
        context=context_str,
        product_a=product_a,
        product_b=product_b,
    )

    response = llm.invoke([SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=user_msg)])
    return {
        "product_a": product_a,
        "product_b": product_b,
        "response": response.content,
        "sources": source_urls,
        "chunks": merged_chunks,
    }


# ── Tool 2: Meeting Preparation ───────────────────────────────────────────────

def meeting_prep(
    customer: str,
    industry: str,
    llm: Any,
    top_k: int = 5,
) -> dict:
    """
    Generate a structured pre-meeting brief for an Airtel Account Manager.

    Returns::

        {
            "customer":  str,
            "industry":  str,
            "response":  str,
            "sources":   list[str],
            "chunks":    list[dict],
        }
    """
    query = f"Airtel B2B solutions for {industry} industry customer enterprise"
    chunks = retrieve_similar_chunks(query, k=top_k)
    context_str, source_urls = _build_context(chunks)

    template = _load("meeting_prep_prompt.md")
    user_msg = template.format(
        context=context_str,
        customer=customer,
        industry=industry,
    )

    response = llm.invoke([SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=user_msg)])
    return {
        "customer": customer,
        "industry": industry,
        "response": response.content,
        "sources": source_urls,
        "chunks": chunks,
    }


# ── Tool 3: Objection Handling ────────────────────────────────────────────────

def handle_objection(
    objection: str,
    llm: Any,
    product_context: str = "Airtel B2B solutions",
    top_k: int = 4,
) -> dict:
    """
    Generate a grounded objection-handling response for a sales conversation.

    Returns::

        {
            "objection":        str,
            "product_context":  str,
            "response":         str,
            "sources":          list[str],
            "chunks":           list[dict],
        }
    """
    query = f"Airtel B2B {product_context} value benefits ROI {objection}"
    chunks = retrieve_similar_chunks(query, k=top_k)
    context_str, source_urls = _build_context(chunks)

    template = _load("objection_prompt.md")
    user_msg = template.format(
        context=context_str,
        objection=objection,
        product_context=product_context,
    )

    response = llm.invoke([SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=user_msg)])
    return {
        "objection": objection,
        "product_context": product_context,
        "response": response.content,
        "sources": source_urls,
        "chunks": chunks,
    }


# ── Tool 4: Follow-up Email ───────────────────────────────────────────────────

def draft_followup_email(
    customer: str,
    solutions: str,
    next_steps: str,
    llm: Any,
    meeting_context: str = "",
    top_k: int = 3,
) -> dict:
    """
    Draft a professional follow-up email after a sales meeting.

    Returns::

        {
            "customer":   str,
            "solutions":  str,
            "response":   str,
            "sources":    list[str],
            "chunks":     list[dict],
        }
    """
    # Retrieve context for the discussed solution(s) to enrich the email
    query = f"Airtel {solutions} benefits features enterprise"
    chunks = retrieve_similar_chunks(query, k=top_k)
    _, source_urls = _build_context(chunks)

    template = _load("followup_email_prompt.md")
    user_msg = template.format(
        meeting_context=meeting_context or f"Meeting about Airtel {solutions}",
        customer=customer,
        solutions=solutions,
        next_steps=next_steps,
    )

    response = llm.invoke([SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=user_msg)])
    return {
        "customer": customer,
        "solutions": solutions,
        "response": response.content,
        "sources": source_urls,
        "chunks": chunks,
    }

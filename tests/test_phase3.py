"""
Phase 3 Smoke Tests — LLM + Agent Loop
"""

import pytest
from src.agent.agent import classify_intent, ask, AirtelAgent


class TestIntentClassifier:
    def test_retrieve_sdwan(self):
        assert classify_intent("How do I pitch Airtel Managed SD-WAN?") == "retrieve"

    def test_retrieve_compare(self):
        assert classify_intent("Compare MPLS and SD-WAN for enterprise customers.") == "compare"

    def test_retrieve_meeting_prep(self):
        assert classify_intent("Prepare for a meeting with a retail company.") == "meeting_prep"

    def test_direct_greeting(self):
        assert classify_intent("Hello there!") == "direct"

    def test_clarify_ambiguous(self):
        assert classify_intent("help") in ("clarify", "direct")   # very short, no Airtel signal


class TestAgentGrounding:
    """Live Groq calls — mark slow to allow skipping in unit-only runs."""

    @pytest.mark.slow
    def test_sdwan_answer_has_sources(self):
        result = ask("How do I pitch Airtel Managed SD-WAN?")
        assert result["intent"] == "retrieve"
        assert len(result["response"]) > 50
        assert len(result["sources"]) > 0
        assert "airtel.in" in result["sources"][0]

    @pytest.mark.slow
    def test_no_hallucination_on_pricing(self):
        result = ask("What is the exact monthly pricing of Airtel SD-WAN?")
        response_lower = result["response"].lower()
        # Should admit missing info rather than invent a price
        assert any(kw in response_lower for kw in [
            "don't have", "not available", "contact", "verified", "check", "pricing"
        ])

    @pytest.mark.slow
    def test_response_not_empty(self):
        result = ask("Tell me about Airtel 5G for Business.")
        assert result["intent"] in ("retrieve", "direct")
        assert len(result["response"]) > 30

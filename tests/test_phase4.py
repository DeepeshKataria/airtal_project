"""
Phase 4 Tests — Memory, Comparison, Meeting Prep, Objection Handling, Follow-up Email.

Unit tests (no LLM calls) run instantly.
Integration tests marked @pytest.mark.slow make live Groq API calls.
"""

import pytest
from src.agent.memory import ConversationMemory
from src.agent.agent import classify_intent, AirtelAgent, ask


# ── Memory Unit Tests ─────────────────────────────────────────────────────────

class TestConversationMemory:
    def test_add_and_retrieve(self):
        mem = ConversationMemory()
        mem.add_human("Tell me about SD-WAN")
        mem.add_ai("Airtel SD-WAN is a managed solution...")
        assert len(mem) == 2
        assert mem.messages[0].content == "Tell me about SD-WAN"
        assert mem.messages[1].content == "Airtel SD-WAN is a managed solution..."

    def test_max_messages_capped(self):
        mem = ConversationMemory(max_messages=4)
        for i in range(4):
            mem.add_human(f"Q{i}")
            mem.add_ai(f"A{i}")
        # maxlen=4, so only last 4 messages kept
        assert len(mem) == 4
        # Oldest Q0/A0 and Q1/A1 pushed out; Q2 and Q3 remain
        contents = [m.content for m in mem.messages]
        assert "Q0" not in contents
        assert "Q2" in contents
        assert "Q3" in contents

    def test_clear(self):
        mem = ConversationMemory()
        mem.add_human("Hello")
        mem.add_ai("Hi")
        mem.clear()
        assert len(mem) == 0
        assert mem.messages == []

    def test_empty_messages(self):
        mem = ConversationMemory()
        assert mem.messages == []
        assert len(mem) == 0


# ── Intent Classification Unit Tests (Phase 4 intents) ───────────────────────

class TestPhase4IntentClassifier:
    def test_compare_vs(self):
        assert classify_intent("Compare Airtel SD-WAN vs MPLS") == "compare"

    def test_compare_versus(self):
        assert classify_intent("SD-WAN versus MPLS — which is better?") == "compare"

    def test_compare_difference(self):
        assert classify_intent("What is the difference between MPLS and SD-WAN?") == "compare"

    def test_meeting_prep_prepare_for(self):
        assert classify_intent("Prepare for a meeting with a manufacturing customer") == "meeting_prep"

    def test_meeting_prep_meeting_with(self):
        assert classify_intent("I have a meeting with a retail company tomorrow") == "meeting_prep"

    def test_objection_expensive(self):
        assert classify_intent("Your solution is too expensive") == "objection"

    def test_objection_vendor_lock(self):
        assert classify_intent("We're worried about vendor lock-in") == "objection"

    def test_objection_downtime(self):
        assert classify_intent("What about downtime during migration?") == "objection"

    def test_followup_email(self):
        assert classify_intent("Draft a follow-up email after the SD-WAN meeting") == "follow_up"

    def test_followup_email_write(self):
        assert classify_intent("Write a follow-up email to the customer") == "follow_up"

    def test_email_takes_priority_over_compare(self):
        # "follow-up email" should beat "comparison" signal in same sentence
        assert classify_intent("Write a follow-up email comparing our SD-WAN options") == "follow_up"


# ── Integration Tests (live Groq API calls) ───────────────────────────────────

class TestPhase4Integration:
    """All tests here make live Groq calls. Marked slow."""

    @pytest.mark.slow
    def test_compare_sdwan_mpls(self):
        result = ask("Compare Airtel SD-WAN vs MPLS")
        assert result["intent"] == "compare"
        assert len(result["response"]) > 100
        # Both product names should appear in the response
        resp_lower = result["response"].lower()
        assert "sd-wan" in resp_lower or "sdwan" in resp_lower
        assert "mpls" in resp_lower

    @pytest.mark.slow
    def test_meeting_prep_manufacturing(self):
        result = ask("Prepare for a meeting with a manufacturing customer")
        assert result["intent"] == "meeting_prep"
        assert len(result["response"]) > 200
        resp_lower = result["response"].lower()
        # Should contain at least one meeting-prep section keyword
        assert any(kw in resp_lower for kw in [
            "challenge", "agenda", "talking point", "discovery", "next step"
        ])

    @pytest.mark.slow
    def test_objection_handling_expensive(self):
        result = ask("Your solution is too expensive")
        assert result["intent"] == "objection"
        assert len(result["response"]) > 100
        resp_lower = result["response"].lower()
        # Should contain an empathetic or value-focused response — not just "yes it is"
        assert any(kw in resp_lower for kw in [
            "understand", "value", "roi", "cost", "benefit", "invest", "saving"
        ])

    @pytest.mark.slow
    def test_followup_email_generation(self):
        result = ask(
            "Draft a follow-up email after the SD-WAN discussion",
            solutions="Airtel Managed SD-WAN",
            customer="TechCorp Ltd",
            next_steps="Schedule a technical demo next week",
        )
        assert result["intent"] == "follow_up"
        resp = result["response"]
        assert len(resp) > 100
        # Email should have a subject line or a greeting
        assert any(kw in resp.lower() for kw in ["subject", "dear", "hi", "hello", "thank"])

    @pytest.mark.slow
    def test_memory_persists_across_turns(self):
        """
        Simulates a multi-turn conversation where the second question
        depends on context from the first turn.
        """
        agent = AirtelAgent()

        r1 = agent.answer("Tell me about Airtel Managed SD-WAN")
        assert r1["intent"] in ("retrieve", "compare", "meeting_prep")
        assert len(r1["response"]) > 50

        # Memory should now have 2 messages
        assert len(agent.memory) == 2

        r2 = agent.answer("What are the key benefits you just mentioned?")
        assert len(r2["response"]) > 30

        # Memory should now have 4 messages
        assert len(agent.memory) == 4

        # The second response should reference SD-WAN context from memory
        r2_lower = r2["response"].lower()
        assert any(kw in r2_lower for kw in [
            "sd-wan", "network", "benefit", "agility", "cloud", "cost"
        ])

    @pytest.mark.slow
    def test_no_hallucination_in_comparison(self):
        result = ask("Compare Airtel SD-WAN vs MPLS")
        response_lower = result["response"].lower()
        # Should not invent specific pricing
        assert "₹" not in result["response"]
        assert "$ " not in result["response"]
        # Should cite sources
        assert len(result.get("sources", [])) > 0

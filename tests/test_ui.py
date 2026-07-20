import pytest
from streamlit.testing.v1 import AppTest
import os

@pytest.mark.slow
def test_app_ui_all_capabilities():
    # Setup AppTest
    at = AppTest.from_file("app.py", default_timeout=60)
    at.run()
    
    # 1. Check title and initialization
    assert not at.exception
    assert at.title[0].value == "Airtel B2B AI Sales Assistant"
    
    # 2. General RAG Q&A
    print("Testing General RAG Q&A...")
    at.chat_input[0].set_value("How do I pitch Airtel SD-WAN?")
    at.run()
    assert not at.exception
    response_text = at.chat_message[1].markdown[0].value
    assert "📚 RAG Answer" in response_text or "intent" in response_text.lower() or "pitch" in response_text.lower()
    
    # 3. Product Comparison
    print("Testing Product Comparison...")
    at.chat_input[0].set_value("Compare MPLS and SD-WAN.")
    at.run()
    assert not at.exception
    response_text = at.chat_message[3].markdown[0].value
    assert "⚖️ Comparison" in response_text or "compare" in response_text.lower()
    
    # 4. Meeting Prep
    print("Testing Meeting Prep...")
    at.chat_input[0].set_value("Prepare for a meeting with a manufacturing customer.")
    at.run()
    assert not at.exception
    response_text = at.chat_message[5].markdown[0].value
    assert "📅 Meeting Prep" in response_text or "meeting" in response_text.lower()

    # 5. Objection Handling
    print("Testing Objection Handling...")
    at.chat_input[0].set_value("Your solution is too expensive.")
    at.run()
    assert not at.exception
    response_text = at.chat_message[7].markdown[0].value
    assert "🛡️ Objection Handling" in response_text or "expensive" in response_text.lower() or "cost" in response_text.lower()
    
    # 6. Follow-up Email
    print("Testing Follow-up Email...")
    at.chat_input[0].set_value("Draft a follow-up email after the SD-WAN discussion.")
    at.run()
    assert not at.exception
    response_text = at.chat_message[9].markdown[0].value
    assert "✉️ Follow-up Email" in response_text or "subject" in response_text.lower()
    
    # 7. Check Clear Conversation button
    print("Testing Clear Conversation...")
    at.sidebar.button[0].click()
    at.run()
    assert not at.exception
    # No chat messages should remain
    assert len(at.chat_message) == 0

"""
Airtel B2B AI Sales Assistant - Final Evaluation Module (Phase 6)
"""

import os
from src.agent.agent import AirtelAgent
from src.agent.memory import ConversationMemory

def run_evaluations():
    print("Starting final evaluations...")
    
    agent = AirtelAgent(memory=ConversationMemory())
    
    test_cases = [
        {
            "name": "General RAG Q&A",
            "query": "How do I pitch Airtel SD-WAN?",
            "expected_intent": "retrieve",
            "must_contain": ["sd-wan", "pitch", "network"],
            "must_have_sources": True
        },
        {
            "name": "Product Comparison",
            "query": "Compare MPLS and SD-WAN.",
            "expected_intent": "compare",
            "must_contain": ["mpls", "sd-wan"],
            "must_have_sources": True
        },
        {
            "name": "Meeting Preparation",
            "query": "Prepare for a meeting with a manufacturing customer.",
            "expected_intent": "meeting_prep",
            "must_contain": ["manufacturing", "meeting", "agenda"],
            "must_have_sources": True
        },
        {
            "name": "Objection Handling",
            "query": "Your solution is too expensive.",
            "expected_intent": "objection",
            "must_contain": ["cost", "value", "understand"],
            "must_have_sources": True
        },
        {
            "name": "Follow-up Email",
            "query": "Draft a follow-up email after the SD-WAN discussion.",
            "expected_intent": "follow_up",
            "must_contain": ["subject", "sd-wan", "dear"],
            "must_have_sources": False
        },
        {
            "name": "Out-of-scope / Hallucination Prevention",
            "query": "What is the exact pricing of Airtel SD-WAN in USD?",
            "expected_intent": "retrieve",
            "must_contain": [],
            "must_have_sources": False
        }
    ]

    report_lines = [
        "# Phase 6 Final Evaluation Report",
        "",
        "| Test Case | Query | Expected Intent | Actual Intent | Sources Found | Pass/Fail |",
        "|-----------|-------|-----------------|---------------|---------------|-----------|"
    ]

    for tc in test_cases:
        print(f"Running: {tc['name']}...")
        try:
            result = agent.answer(tc["query"])
            actual_intent = result["intent"]
            response_text = result["response"].lower()
            sources = result.get("sources", [])
            
            # Check intent
            intent_pass = actual_intent == tc["expected_intent"]
            
            # Check content
            content_pass = True
            for kw in tc["must_contain"]:
                if kw.lower() not in response_text:
                    # In some cases exact keyword might vary, we are checking lowercase.
                    content_pass = False
                    print(f"  Missing keyword: {kw}")
            
            # Check sources
            sources_pass = True
            if tc["must_have_sources"] and not sources:
                sources_pass = False
                print("  Missing sources")

            passed = intent_pass and content_pass and sources_pass
            pass_str = "✅ PASS" if passed else "❌ FAIL"
            
            sources_found = "Yes" if sources else "No"
            
            report_lines.append(f"| {tc['name']} | `{tc['query']}` | `{tc['expected_intent']}` | `{actual_intent}` | {sources_found} | {pass_str} |")
            
        except Exception as e:
            report_lines.append(f"| {tc['name']} | `{tc['query']}` | `{tc['expected_intent']}` | ERROR | N/A | ❌ FAIL |")
            print(f"  Error: {e}")

    report_content = "\n".join(report_lines)
    
    with open("EVALUATION_REPORT.md", "w") as f:
        f.write(report_content)
        
    print("\nEvaluation complete! Report saved to EVALUATION_REPORT.md")

if __name__ == "__main__":
    run_evaluations()

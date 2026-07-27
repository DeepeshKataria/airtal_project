"""
Phase 3 CLI — interactive conversation with the Airtel B2B AI Sales Assistant.
Usage:
    python -m src.agent.cli "How do I pitch Airtel Managed SD-WAN?"
    python -m src.agent.cli   (interactive mode)
"""

import argparse
from src.agent.agent import ask, MODEL_NAME

SEPARATOR = "─" * 62

def print_result(result: dict):
    print()
    intent_label = {"retrieve": "📚 RAG Answer", "direct": "💬 Direct", "clarify": "❓ Clarify"}.get(
        result["intent"], result["intent"]
    )
    print(f"[{intent_label}]")
    print(SEPARATOR)
    print(result["response"])
    if result.get("sources"):
        print()
        print("Sources:")
        for url in result["sources"]:
            print(f"  • {url}")
    print(SEPARATOR)

def main():
    parser = argparse.ArgumentParser(description="Airtel B2B AI Sales Assistant — Phase 3 CLI")
    parser.add_argument("query", nargs="?", help="Question to ask")
    parser.add_argument("-k", "--top-k", type=int, default=4)
    args = parser.parse_args()

    print(f"\n🤖  Airtel B2B AI Sales Assistant  |  model: {MODEL_NAME}")

    if args.query:
        result = ask(args.query)
        print(f"\nQuery: {args.query}")
        print_result(result)
    else:
        print("Type your question and press Enter. Type 'exit' to quit.\n")
        while True:
            try:
                query = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Bye!")
                break
            result = ask(query)
            print_result(result)

if __name__ == "__main__":
    main()

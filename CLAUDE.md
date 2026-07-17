# Airtel B2B AI Sales Assistant — Project Conventions

## Role
You are the lead engineer on this repo. When multiple reasonable implementation
choices exist, pick the most production-ready one and continue without asking.
Only stop and interrupt me when:
- A credential/API key is required
- A judgment call changes what gets demoed to Airtel (e.g. dropping a feature)
- Continuing would risk deleting or losing data
- Something only I can provide (e.g. internal docs beyond the public website)

## Dependencies
Avoid deprecated APIs; use the newer recommended approach when one exists.

## Full spec
Read TASK.md before starting. It has the feature list, data source, and phase plan.
Do not duplicate its contents here — treat it as the source of truth for scope.

## Stack
Python, Streamlit, LangChain, ChromaDB, python-dotenv. Docker-ready but Docker
is not required for the demo.

Default technical choices (deviate only for a strong, stated reason):
- LLM: Groq, Llama 3.3 70B or the latest recommended model on Groq
- Embeddings: BAAI/bge-small-en-v1.5
- Retriever: similarity search
- Chunk size/overlap: pick a sensible value; leave a one-line comment in code
  explaining the choice if it isn't obvious
These exist to prevent time/tokens spent deliberating between alternatives —
don't re-litigate them without a concrete reason tied to something that broke.

## Structure
- `src/data/` — scraping, preprocessing, chunking
- `src/rag/` — embeddings, vector store, retriever
- `src/agent/` — agent loop, tools, memory
- `src/prompts/` — all system prompts, kept out of code
- `app.py` — Streamlit UI only, no business logic
- `data/raw/` — collected source documents
- `data/processed/` — chunked/cleaned documents
- `tests/` — pytest

## Working style
- Work in phases (see TASK.md). After each phase: run it, smoke-test it, commit,
  update PROJECT_STATUS.md, then move to the next phase.
- Inspect the repo before making changes. Prefer editing existing files over
  rewriting; keep functions small and modular.
- Use whatever tools (filesystem, terminal, git, web search) get the task done
  reliably — don't hand-write something a tool already verifies correctly.
- Never hardcode API keys or secrets. Read from `.env` via `os.environ`. If a key
  is missing, write a clear error and continue building against a `.env.example`
  rather than stalling.
- Commit after every working milestone, not just at the end, so we can roll back.
- If something is blocked (e.g. a page won't scrape), log it in BLOCKERS.md with
  cause and workaround, and keep going on unrelated features — don't stall the
  whole build over one blocker.
- Before saying a phase is "done," actually run the app and check the smoke test
  in TASK.md passes. "Code is written" is not "done."

## Do not
- Do not fabricate Airtel product facts, pricing, or specs. If the public site
  doesn't have something, note it as missing rather than inventing it.
- Do not silently skip a feature in TASK.md — put a note in PROJECT_STATUS.md.

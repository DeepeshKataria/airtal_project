# Project Status — Airtel B2B AI Sales Assistant

## Current Phase
**Phase 5 — UI** (Complete)

## Phase Checklist
- [x] **Phase 0 — Project Setup**: Repository structure, configuration, virtual environment, and dependency setup. Verified via smoke test import check.
- [x] **Phase 1 — Data**: Scraped public Airtel B2B pages → deduplicated → chunked (286 chunks) → saved to `data/processed/chunks.json`. Verified via `test_phase1.py` and smoke test ingest execution.
- [x] **Phase 2 — RAG Core**: Embeddings (`BAAI/bge-small-en-v1.5`), ChromaDB vector store (`chroma_db/`), retriever, and CLI interface (`src/rag/cli.py`). Verified via `test_phase2.py` and query retrieval smoke test.
- [x] **Phase 3 — LLM + Agent Loop**: Groq `llama-3.3-70b-versatile` wired to retriever. System/RAG prompts in `src/prompts/`. Decision loop (retrieve / direct / clarify) in `src/agent/agent.py`. CLI in `src/agent/cli.py`. Answers are grounded with source citations; pricing query correctly declined instead of hallucinating. Verified via `test_phase3.py` and 4 live query smoke tests.
- [x] **Phase 4 — Memory + Features**: In-process `ConversationMemory` (deque, max 6 turns). Four grounded sales tools: product comparison, meeting prep, objection handling, follow-up email drafting. All tools route via `classify_intent()` in `src/agent/agent.py`. Dedicated prompts in `src/prompts/`. Verified via `test_phase4.py` (15 unit tests + 6 integration tests) and 5 CLI smoke tests.
- [x] **Phase 5 — UI**: Streamlit web application in `app.py`. Integrates `AirtelAgent` backend, uses `st.session_state` for conversation memory, supports all Phase 4 tools, displays intent badges and source citations cleanly. Tested via `streamlit.testing.v1.AppTest` in `tests/test_ui.py`.
- [ ] **Phase 6 — Evals**: Evaluation dataset and automated pass/fail scoring.

## Notes & Updates
- Initialized Phase 0 project structure, environment configuration, and placeholder tracking files.
- Phase 4 architecture: tools are independently callable functions (`src/agent/tools.py`), injected with the agent's shared `ChatGroq` instance. Memory is isolated in `src/agent/memory.py` and replaceable with LangChain memory in Phase 5.

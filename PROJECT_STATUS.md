# Project Status — Airtel B2B AI Sales Assistant

## Current Phase
**Phase 2 — RAG Core** (Complete)

## Phase Checklist
- [x] **Phase 0 — Project Setup**: Repository structure, configuration, virtual environment, and dependency setup. Verified via smoke test import check.
- [x] **Phase 1 — Data**: Scraped public Airtel B2B pages -> deduplicated -> chunked (286 chunks) -> saved to `data/processed/chunks.json`. Verified via `test_phase1.py` and smoke test ingest execution.
- [x] **Phase 2 — RAG Core**: Embeddings (`BAAI/bge-small-en-v1.5`), ChromaDB vector store (`chroma_db/`), retriever, and CLI interface (`src/rag/cli.py`). Verified via `test_phase2.py` and query retrieval smoke test.
- [ ] **Phase 3 — LLM + Agent Loop**: Groq LLM integration, system prompts, decision loop.
- [ ] **Phase 4 — Memory + Features**: Multi-turn conversation memory, meeting prep, product comparison, objection handling, email drafting.
- [ ] **Phase 5 — UI**: Streamlit web application.
- [ ] **Phase 6 — Evals**: Evaluation dataset and automated pass/fail scoring.

## Notes & Updates
- Initialized Phase 0 project structure, environment configuration, and placeholder tracking files.

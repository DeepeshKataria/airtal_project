# Airtel B2B AI Sales Assistant

An AI assistant designed for Airtel Account Managers to query Airtel Business products, conduct meeting preparation, compare products, handle objections, and generate follow-up emails using RAG.

## Project Structure
- `src/data/` — Scraping, preprocessing, deduplication, chunking
- `src/rag/` — Embeddings, vector store, retriever
- `src/agent/` — Agent loop, tools, memory
- `src/prompts/` — System, RAG, comparison, meeting prep, objection, and email prompts
- `app.py` — Streamlit UI (Phase 5)
- `data/raw/` — Collected source documents
- `data/processed/` — Chunked/processed documents
- `tests/` — Pytest test suite

## Features
- Retrieval-Augmented Generation (RAG) over Airtel B2B public documentation
- Airtel product Q&A with source citations
- Product comparison (e.g. SD-WAN vs MPLS)
- Meeting preparation brief generator
- Objection handling with grounded rebuttals
- Follow-up email drafting
- Multi-turn conversation memory (last 6 turns)
- Streamlit web interface (Phase 5)

## Quick Start

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### 2. Data Ingestion
```bash
python -m src.data.scraper
python -m src.data.ingest
```

### 3. Build Vector Store
```bash
python -m src.rag.vectorstore
```

### 4. Run AI Sales Assistant CLI (Phase 3 & 4)
```bash
# Single query
python -m src.agent.cli "How do I pitch Airtel Managed SD-WAN?"

# Phase 4 examples
python -m src.agent.cli "Compare Airtel SD-WAN vs MPLS"
python -m src.agent.cli "Prepare for a meeting with a manufacturing customer"
python -m src.agent.cli "Your solution is too expensive"
python -m src.agent.cli "Draft a follow-up email after the SD-WAN discussion"

# Interactive multi-turn mode
python -m src.agent.cli
```

### 5. Run RAG CLI Retriever only (Phase 2)
```bash
python -m src.rag.cli "How do I pitch Airtel Managed SD-WAN?" --top-k 4
```

### 6. Run Tests
```bash
# Unit tests only (fast, no API calls)
pytest tests/ -k "not slow" -v

# All tests including live Groq integration tests
pytest tests/ -v
```

### 7. Run Application (Phase 5)
```bash
streamlit run app.py
```

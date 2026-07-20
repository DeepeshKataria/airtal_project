# Airtel B2B AI Sales Assistant

An AI assistant designed for Airtel Account Managers to query Airtel Business products, conduct meeting preparation, compare products, handle objections, and generate follow-up emails using RAG.

## Project Structure
- `src/data/` — Scraping, preprocessing, deduplication, chunking
- `src/rag/` — Embeddings, vector store, retriever
- `src/agent/` — Agent loop, tools, memory
- `src/prompts/` — System prompts
- `app.py` — Streamlit UI
- `data/raw/` — Collected source documents
- `data/processed/` — Chunked/processed documents
- `tests/` — Pytest test suite

## Features
- Retrieval-Augmented Generation (RAG) over Airtel Business public documentation
- Airtel product Q&A with source citations
- Product comparison
- Meeting preparation assistant
- Objection handling
- Follow-up email generation
- Streamlit web interface

## Quick Start

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Data Ingestion
```bash
python -m src.data.scraper
python -m src.data.ingest
```

### 3. Run RAG CLI Retriever (Phase 2)
```bash
# Query with specific question
python -m src.rag.cli "How do I pitch Airtel Managed SD-WAN?" --top-k 4

# Or interactive mode
python -m src.rag.cli
```

### 4. Run Application (Phase 5)
```bash
streamlit run app.py
```

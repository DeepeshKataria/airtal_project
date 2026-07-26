# Airtel B2B AI Sales Assistant

An AI assistant designed for Airtel Account Managers to query Airtel Business products, conduct meeting preparation, compare products, handle objections, and generate follow-up emails using RAG.

## Project Structure
- `src/data/` — Scraping, preprocessing, deduplication, chunking
- `src/rag/` — Embeddings, vector store, retriever
- `src/agent/` — Agent loop, tools, memory
- `src/prompts/` — System, RAG, comparison, meeting prep, objection, and email prompts
- `app.py` — Streamlit UI
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
- Streamlit web interface

## Architecture Overview
The system follows a lightweight Agentic RAG architecture:
1. **Data Pipeline**: Scrapes Airtel B2B public pages, deduplicates, and chunks them.
2. **Retrieval**: Uses BAAI/bge-small-en-v1.5 embeddings stored locally in ChromaDB.
3. **Agent Loop**: A stateful routing loop (`AirtelAgent`) determines the user's intent using regular expressions.
4. **Tools**: Based on the intent, it delegates to specific sales tools (e.g. `compare_products`, `meeting_prep`) or falls back to generic RAG or direct LLM responses.
5. **Memory**: An in-process `ConversationMemory` stores the last 6 turns (12 messages) to provide contextual awareness.
6. **UI**: A Streamlit frontend (`app.py`) manages session state for the agent and memory per user.

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

### 7. Run Streamlit UI Application
```bash
streamlit run app.py
```

## Screenshots
*(Add screenshots of the UI here)*

## Known Limitations
- The application relies on web-scraped data from Airtel public documentation which can become stale over time.
- The retrieval similarity threshold is statically defined (`MIN_RELEVANCE_SCORE`). Some highly nuanced questions may fall below the threshold and trigger a fallback out-of-scope response.
- In-process conversation memory (`ConversationMemory`) limits deployment scaling across multiple load-balanced workers without sticky sessions.
- Embeddings (`BAAI/bge-small-en-v1.5`) run on the CPU locally which may be slow on some environments.

## Future Improvements
- Integrate LangChain's persistent memory (e.g., Redis or SQLite) for true multi-session support.
- Upgrade the retriever to hybrid search (keyword + semantic) or use an external vector database like Pinecone.
- Enhance the scraping pipeline to automatically detect and ingest new documentation periodically.
- Deploy the Streamlit application using Docker and Streamlit Cloud.
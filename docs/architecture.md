# Architecture

## System Overview

The Airtel B2B AI Sales Assistant follows a lightweight **Agentic RAG** (Retrieval-Augmented Generation) pattern. The system retrieves relevant documentation from a local vector store, routes to specialised tools based on intent classification, and generates grounded responses using an LLM.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend (app.py)                 │
│  Session State · Chat History · Prompt Cards · Intent Badges    │
└────────────────────────────┬────────────────────────────────────┘
                             │ query
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AirtelAgent (src/agent/agent.py)              │
│                                                                 │
│  1. classify_intent(query) ──▶ regex-based intent router        │
│  2. Route to handler:                                           │
│     ├── retrieve   → _rag_answer()                              │
│     ├── direct     → _direct_answer()                           │
│     ├── clarify    → _clarify()                                 │
│     ├── compare    → _tool_compare()                            │
│     ├── meeting    → _tool_meeting_prep()                       │
│     ├── objection  → _tool_objection()                          │
│     └── follow_up  → _tool_follow_up()                          │
│  3. Persist turn in ConversationMemory                          │
└────────┬────────────────────────┬───────────────────────────────┘
         │                        │
         ▼                        ▼
┌────────────────┐    ┌──────────────────────────────────┐
│ ConversationMemory │ │  Sales Tools (src/agent/tools.py) │
│ (deque, 12 msgs)   │ │  compare_products()              │
│ HumanMessage        │ │  meeting_prep()                  │
│ AIMessage           │ │  handle_objection()              │
└────────────────┘    │  draft_followup_email()           │
                      └───────────────┬────────────────────┘
                                      │ retrieve context
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              RAG Retriever (src/rag/retriever.py)               │
│  AirtelRetriever.retrieve(query, k) → similarity search        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          ChromaDB Vector Store (src/rag/vectorstore.py)         │
│  BAAI/bge-small-en-v1.5 embeddings · chroma_db/ on disk        │
└────────────────────────────┬────────────────────────────────────┘
                             │ built from
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Data Pipeline (src/data/)                          │
│  scraper.py → data/raw/*.md                                    │
│  ingest.py  → dedupe → chunk → data/processed/chunks.json      │
└─────────────────────────────────────────────────────────────────┘
```

## Data Pipeline

### Scraping (`src/data/scraper.py`)

The scraper crawls Airtel's public B2B pages starting from a set of seed URLs. For each URL, it:
1. Fetches the HTML with standard headers.
2. Detects JS-rendered SPA pages (which can't be scraped with `requests`) and logs them to `MISSING_DATA.md`.
3. Converts static HTML to clean Markdown using BeautifulSoup, preserving headings, paragraphs, and list items.
4. Discovers linked B2B pages and adds them to the crawl queue (up to 40 pages).

### Ingestion (`src/data/ingest.py`)

The ingestion pipeline processes raw Markdown files into retrieval-ready chunks:
1. Extracts the source URL from the HTML comment header.
2. Deduplicates content at the paragraph level within and across documents.
3. Chunks text at ~800 characters with 100-character overlap, respecting paragraph boundaries.
4. Assigns stable chunk IDs and deduplicates by content hash.
5. Outputs `data/processed/chunks.json`.

## Retrieval

### Embeddings

The system uses `BAAI/bge-small-en-v1.5` (384 dimensions) from Hugging Face, running on CPU. The embedding model instance is shared via a singleton pattern to avoid repeated loading.

### Vector Store (`src/rag/vectorstore.py`)

ChromaDB is used as a local persistent vector store. On first run, it builds the index from `chunks.json`. On subsequent runs, it reuses the existing index unless `force_rebuild=True` is passed.

### Retriever (`src/rag/retriever.py`)

`AirtelRetriever` wraps ChromaDB's `similarity_search_with_relevance_scores` to return the top-k most relevant chunks, each with a relevance score. A minimum relevance threshold (`MIN_RELEVANCE_SCORE`, default 0.45) is applied in the agent to filter low-quality retrievals.

## Intent Routing

The `classify_intent()` function in `agent.py` uses a priority-ordered set of compiled regex patterns:

1. **Email signals** (highest priority) — `follow-up email`, `draft email`, etc.
2. **Compare signals** — `compare`, `vs`, `difference between`, etc.
3. **Meeting signals** — `prepare for`, `meeting with`, etc.
4. **Objection signals** — `too expensive`, `vendor lock`, `downtime`, etc.
5. **Retrieve signals** — Airtel product names, technical terms, industry keywords.
6. **Direct signals** — Greetings, meta questions (`hello`, `what can you do`).
7. **Clarify fallback** — Very short queries (<12 chars) with no product signals.

This ordering ensures that tool intents take priority over generic retrieval.

## Tools

Each tool function in `src/agent/tools.py`:
1. Retrieves relevant documentation via the RAG retriever.
2. Formats a structured prompt from `src/prompts/`.
3. Calls the LLM with the system prompt and tool-specific user prompt.
4. Returns a typed result dict with `response`, `sources`, and `chunks`.

All tools share the agent's `ChatGroq` instance to avoid redundant model initialization.

## Memory

`ConversationMemory` in `src/agent/memory.py` is a bounded deque of LangChain message objects (max 12 messages = 6 full turns). It provides:
- `add_human(text)` and `add_ai(text)` to append messages.
- `messages` property to retrieve the current history.
- `clear()` to reset the conversation.

The memory is injected into the agent at construction, so callers can share or replace it.

## UI Interaction

The Streamlit frontend (`app.py`) manages:
- **Session state** for the agent, memory, and chat history.
- **Prompt cards** on the landing page for quick interaction.
- **Sidebar** with status indicators, quick prompts, conversation export, and a reset button.
- **Intent badges** colour-coded by classification result.
- **Source citations** as clickable chips linking to original Airtel documentation.
- **Response timing** showing generation duration.
- **Error handling** with user-friendly messages and expandable technical details.

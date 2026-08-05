# Airtel B2B AI Sales Assistant

> An AI-powered sales copilot for Airtel Account Managers — instant answers, meeting briefs, product comparisons, objection handling, and follow-up emails, all grounded in official Airtel B2B documentation.

---

## Features

| Feature | Description |
|---|---|
| **RAG Q&A** | Ask questions about Airtel B2B products and get grounded answers with source citations |
| **Product Comparison** | Side-by-side comparison of Airtel solutions (e.g. SD-WAN vs MPLS) |
| **Meeting Preparation** | Generate structured pre-meeting briefs tailored to industry and customer |
| **Objection Handling** | Counter sales objections with data-backed rebuttals |
| **Follow-up Email** | Draft professional post-meeting emails referencing discussed solutions |
| **Conversation Memory** | Maintains context across the last 6 turns for coherent multi-turn dialogue |
| **Intent Routing** | Automatically classifies queries and routes to the appropriate tool or RAG pipeline |
| **Source Citations** | Every grounded answer includes links to the original Airtel B2B documentation |

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| LLM | Groq (Llama 3.3 70B) | Fast inference for response generation |
| Embeddings | BAAI/bge-small-en-v1.5 | Semantic similarity for document retrieval |
| Vector Store | ChromaDB | Local persistent vector database |
| Framework | LangChain | LLM orchestration and message handling |
| Frontend | Streamlit | Interactive web UI with session state |
| Environment | python-dotenv | Secure configuration management |

## Architecture Overview

The system follows a lightweight **Agentic RAG** architecture:

1. **Data Pipeline** — Scrapes Airtel B2B public pages, deduplicates, and chunks them into retrievable segments.
2. **Retrieval** — Uses `BAAI/bge-small-en-v1.5` embeddings stored locally in ChromaDB for semantic similarity search.
3. **Intent Router** — A regex-based classifier (`classify_intent`) determines the user's intent before any LLM call.
4. **Tool Dispatch** — Based on the intent, delegates to specialised tool functions (`compare_products`, `meeting_prep`, `handle_objection`, `draft_followup_email`) or falls back to generic RAG or direct LLM responses.
5. **Memory** — An in-process `ConversationMemory` (bounded deque) stores the last 6 full turns (12 messages) for contextual awareness.
6. **UI** — A Streamlit frontend manages session state, displays intent badges, source citations, and supports prompt cards for quick interaction.

> For a detailed architecture walkthrough, see [docs/architecture.md](docs/architecture.md).

## Repository Structure

```
Airtel-ai-assistant/
├── app.py                          # Streamlit web application
├── src/
│   ├── agent/
│   │   ├── agent.py                # Intent classifier + AirtelAgent loop
│   │   ├── tools.py                # Phase 4 sales tools (compare, meeting, objection, email)
│   │   ├── memory.py               # Bounded conversation memory
│   │   ├── utils.py                # Shared helpers (context formatting)
│   │   ├── evaluate.py             # Automated evaluation runner
│   │   └── cli.py                  # Terminal chat interface
│   ├── rag/
│   │   ├── vectorstore.py          # ChromaDB vector store manager
│   │   ├── retriever.py            # Similarity search retriever
│   │   └── cli.py                  # RAG-only CLI for chunk inspection
│   ├── data/
│   │   ├── scraper.py              # Airtel B2B page scraper
│   │   └── ingest.py               # Deduplication + chunking pipeline
│   └── prompts/
│       ├── system_prompt.md         # Core system prompt
│       ├── rag_prompt.md            # RAG retrieval prompt template
│       ├── comparison_prompt.md     # Product comparison prompt
│       ├── meeting_prep_prompt.md   # Meeting preparation prompt
│       ├── objection_prompt.md      # Objection handling prompt
│       └── followup_email_prompt.md # Follow-up email prompt
├── data/
│   ├── raw/                         # Scraped Airtel B2B pages (markdown)
│   └── processed/                   # Chunked documents (chunks.json)
├── tests/                           # Pytest test suite
├── docs/                            # Project documentation
├── .streamlit/config.toml           # Streamlit theme and server config
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
└── .gitignore
```

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

### 4. Run the Streamlit Application

```bash
streamlit run app.py
```

### 5. Run the CLI (alternative)

```bash
# Single query
python -m src.agent.cli "How do I pitch Airtel Managed SD-WAN?"

# Interactive multi-turn mode
python -m src.agent.cli
```

### 6. Run Tests

```bash
# Unit tests only (fast, no API calls)
pytest tests/ -k "not slow" -v

# All tests including live Groq integration tests
pytest tests/ -v
```

## Example Queries

| Query | Intent | What It Does |
|---|---|---|
| `How do I pitch Airtel Managed SD-WAN?` | RAG | Retrieves product docs and generates a grounded sales pitch |
| `Compare SD-WAN and MPLS for enterprise networking` | Compare | Side-by-side analysis with strengths, trade-offs, and recommendations |
| `Prepare for a meeting with a manufacturing customer` | Meeting Prep | Generates a structured briefing with talking points and discovery questions |
| `Your solution is too expensive` | Objection | Produces empathetic, value-focused rebuttals backed by documentation |
| `Draft a follow-up email after the SD-WAN discussion` | Email | Creates a professional post-meeting email with next steps |
| `Hello` | Direct | Responds conversationally without unnecessary retrieval |

## Design Decisions

| Decision | Rationale |
|---|---|
| **RAG over fine-tuning** | Grounded answers with source citations are more convincing for a sales tool than a fine-tuned model that could hallucinate. RAG also allows easy knowledge base updates without retraining. |
| **Regex intent routing** | Fast, transparent, and debuggable. No LLM call wasted on routing — the regex classifier runs in microseconds and handles all observed query patterns reliably. |
| **Groq (Llama 3.3 70B)** | Free tier, fast inference (~2-4s responses), and strong instruction following. Ideal for a demo project. |
| **ChromaDB (local)** | Zero-config local vector store with persistence. No external service dependencies for the demo. |
| **Bounded memory (6 turns)** | Fits comfortably within the LLM context window while keeping API costs low. Simple deque-based implementation is easy to replace with persistent storage later. |

> For a full explanation, see [docs/design-decisions.md](docs/design-decisions.md).

## Known Limitations

- Web-scraped data can become stale if Airtel updates their documentation.
- Static relevance threshold (`MIN_RELEVANCE_SCORE`) may cause some nuanced queries to trigger fallback responses.
- In-process memory does not persist across server restarts.
- CPU-based embeddings may be slow on resource-constrained environments.

> For a detailed analysis, see [docs/limitations.md](docs/limitations.md).

## Acknowledgements

- **Airtel Business** — Public B2B documentation used as the knowledge base.
- **Groq** — Free-tier LLM inference API.
- **LangChain** — LLM orchestration framework.
- **ChromaDB** — Open-source embedding database.
- **Hugging Face** — `BAAI/bge-small-en-v1.5` embedding model.
- **Streamlit** — Web application framework.

## License

This project is for educational and portfolio purposes. The scraped Airtel B2B content remains the property of Bharti Airtel Limited.

## Author

**Deepesh Kataria**

GitHub: https://github.com/DeepeshKataria

LinkedIn: https://www.linkedin.com/in/deepesh-kataria-3392aa2b8/
# Limitations & Future Improvements

## Current Limitations

### Data Coverage

- **JS-rendered pages not scraped.** Many Airtel B2B product pages are single-page applications that require JavaScript execution. The scraper uses `requests` (HTTP only), so these pages return empty content and are logged in `MISSING_DATA.md`. This means the knowledge base is incomplete for products like Airtel IQ, Cloud, Cybersecurity, IoT, and others.
- **Static data snapshot.** The knowledge base is a point-in-time snapshot of Airtel's public documentation. Product changes, new offerings, and pricing updates are not automatically reflected.
- **No internal documentation.** The assistant only has access to publicly available information. Internal sales playbooks, pricing sheets, and competitive intelligence are not included.

### Retrieval Quality

- **Fixed relevance threshold.** The `MIN_RELEVANCE_SCORE` (default 0.45) is a static cutoff. Some valid but nuanced queries may fall below this threshold and trigger a fallback "I don't have information" response, even when partially relevant chunks exist.
- **No hybrid search.** The retriever uses pure semantic similarity. Adding keyword-based search (BM25) alongside embeddings would improve recall for queries containing specific product names or technical terms.
- **Chunk boundary artifacts.** The chunking strategy splits at ~800 characters with paragraph-aware boundaries. Some complex product descriptions may be split across chunks, reducing retrieval quality.

### Intent Classification

- **Regex-based routing.** While fast and deterministic, the regex classifier cannot handle highly ambiguous or novel phrasings. A query like "help me win this deal" would be classified as `retrieve` rather than a more specific intent.
- **No confidence scoring.** The classifier returns a single intent with no confidence measure. There is no mechanism to detect borderline cases or route to multiple tools.

### Memory & State

- **In-process memory only.** Conversation history is stored in a Python deque within the Streamlit session. It does not persist across server restarts, browser refreshes, or multiple concurrent users on separate workers.
- **No user identity.** There is no authentication or user management. All sessions are anonymous and independent.

### Deployment

- **Single-process Streamlit.** The application runs as a single Streamlit process. It is not designed for high-concurrency production use.
- **CPU-based embeddings.** The `BAAI/bge-small-en-v1.5` model runs on CPU, which may cause noticeable latency on first load (model download + initialisation) and on resource-constrained environments.

---

## Trade-offs

| Trade-off | Chosen Approach | Alternative | Why |
|---|---|---|---|
| Retrieval accuracy vs speed | BGE-small (384d, CPU) | BGE-large (1024d, GPU) | Sufficient quality for demo; no GPU requirement |
| Intent routing cost | Regex (free, instant) | LLM classifier (accurate, costly) | Covers all observed patterns; zero latency |
| Memory persistence | In-process deque | Redis / SQLite | Simplicity; no external dependencies for demo |
| Data freshness | Static snapshot | Scheduled re-scraping | Manual re-scrape is sufficient for portfolio use |
| Frontend framework | Streamlit | React + FastAPI | Single-language stack; fastest path to demo |

---

## Future Improvements

### Short-Term (Low Effort)

- **Hybrid retrieval.** Add BM25 keyword search alongside semantic similarity to improve recall for product-name-heavy queries.
- **Dynamic relevance threshold.** Use the score distribution of retrieved chunks to adaptively decide when to trigger fallback responses.
- **Headless browser scraping.** Use Playwright or Selenium to scrape JS-rendered Airtel pages, filling the gaps in `MISSING_DATA.md`.

### Medium-Term

- **Persistent conversation memory.** Replace the in-process deque with Redis or SQLite-backed storage for cross-session continuity.
- **LLM-based intent fallback.** Use a cheap, fast LLM call as a secondary classifier when regex confidence is low.
- **Streaming responses.** Stream LLM output token-by-token in the Streamlit UI for a more responsive feel.
- **User feedback loop.** Add thumbs-up/down buttons to responses and log feedback for retrieval quality monitoring.

### Long-Term

- **Scheduled data refresh.** Automatically re-scrape and re-index Airtel documentation on a weekly or monthly schedule.
- **Multi-user deployment.** Containerise with Docker, add authentication, and deploy behind a load balancer.
- **Analytics dashboard.** Track query patterns, intent distributions, and retrieval hit rates to identify knowledge gaps.
- **Fine-tuned reranker.** Add a cross-encoder reranker after initial retrieval to improve precision on ambiguous queries.

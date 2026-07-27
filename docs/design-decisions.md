# Design Decisions

This document explains the key technology and architectural choices made in the Airtel B2B AI Sales Assistant.

---

## RAG Instead of Fine-Tuning

**Decision:** Use Retrieval-Augmented Generation (RAG) over fine-tuning.

**Rationale:**
- **Grounded answers with citations.** A sales assistant must be trustworthy. RAG enables every response to cite the exact documentation it drew from, making it easy for Account Managers to verify claims before using them in client conversations.
- **No hallucination risk on facts.** Fine-tuning can memorise training data patterns but may confidently generate incorrect product specifications or pricing. RAG retrieves actual documentation, and the system explicitly declines to answer when retrieval confidence is low.
- **Easy knowledge updates.** When Airtel updates their product pages, the knowledge base can be refreshed by re-running the scraper and ingestion pipeline — no model retraining required.
- **Cost and time efficiency.** Fine-tuning a 70B model requires significant compute and data preparation. RAG achieves comparable quality for domain-specific Q&A with a fraction of the effort.

---

## Streamlit

**Decision:** Use Streamlit as the web frontend.

**Rationale:**
- **Rapid prototyping.** Streamlit allows building a polished chat interface with session state, sidebar controls, and custom HTML/CSS in a single Python file.
- **Native chat components.** `st.chat_message`, `st.chat_input`, and session state provide first-class support for conversational UIs.
- **No frontend build step.** The entire application runs as a single `streamlit run app.py` command — ideal for demos and portfolio presentations.
- **Python-native.** The backend (LangChain, ChromaDB, Groq) is entirely Python, so Streamlit avoids the complexity of a separate API server and JavaScript frontend.

**Trade-offs:** Streamlit's rerun-based execution model can be less intuitive for complex state management, and it is not ideal for production-scale multi-user deployments.

---

## LangChain

**Decision:** Use LangChain for LLM orchestration.

**Rationale:**
- **Standardised message types.** `SystemMessage`, `HumanMessage`, and `AIMessage` provide a clean abstraction for constructing multi-turn prompts.
- **Embedding integrations.** `HuggingFaceEmbeddings` and `Chroma` wrappers simplify vector store setup.
- **Swappable LLM backends.** The `ChatGroq` class can be replaced with `ChatOpenAI` or any other LangChain-compatible provider with minimal code changes.
- **Community ecosystem.** Well-documented, widely used, and actively maintained.

**Trade-offs:** LangChain introduces a dependency layer that can be opaque for debugging. The project uses it lightly — primarily for message types and embeddings — so it could be removed without major refactoring if needed.

---

## ChromaDB

**Decision:** Use ChromaDB as the vector store.

**Rationale:**
- **Zero-config local persistence.** ChromaDB stores embeddings on disk (`chroma_db/`) with no external database server required.
- **LangChain integration.** `langchain-chroma` provides `from_documents()` and `similarity_search_with_relevance_scores()` out of the box.
- **Suitable for demo scale.** With ~286 document chunks, a local vector store is more than sufficient. No need for a hosted service like Pinecone or Weaviate.

**Trade-offs:** ChromaDB is not designed for high-concurrency production workloads. For a multi-user deployment, a managed vector database would be more appropriate.

---

## Groq (Llama 3.3 70B)

**Decision:** Use Groq's hosted Llama 3.3 70B as the primary LLM.

**Rationale:**
- **Free tier availability.** Groq offers a generous free tier, making it ideal for a demo and portfolio project.
- **Fast inference.** Groq's custom hardware delivers responses in 2-4 seconds, providing a responsive user experience.
- **Strong instruction following.** Llama 3.3 70B reliably follows structured prompts (comparison tables, meeting briefs, email formats) without extensive prompt engineering.
- **No GPU required locally.** All LLM inference runs in the cloud, keeping the local setup lightweight.

**Trade-offs:** Dependence on Groq's API availability. The project is designed to be easily switchable to OpenAI or another provider via LangChain.

---

## Sentence-Transformers (BAAI/bge-small-en-v1.5)

**Decision:** Use `BAAI/bge-small-en-v1.5` for embedding generation.

**Rationale:**
- **Small and fast.** 384-dimensional embeddings with a ~33M parameter model. Runs on CPU without significant latency.
- **Strong retrieval quality.** BGE models are specifically trained for retrieval tasks and perform well on semantic similarity benchmarks.
- **Normalised embeddings.** The model supports L2-normalised output, which pairs well with cosine similarity search in ChromaDB.
- **No API dependency.** Embeddings are generated locally, so the retrieval pipeline works offline and has no per-query cost.

**Trade-offs:** Larger models (e.g., `bge-large-en-v1.5`) would provide marginally better retrieval accuracy at the cost of slower inference and higher memory usage.

---

## Regex-Based Intent Classification

**Decision:** Use compiled regex patterns instead of an LLM call for intent classification.

**Rationale:**
- **Speed.** Regex matching runs in microseconds, avoiding an extra LLM round-trip before the main response generation.
- **Transparency.** The classification logic is fully deterministic and inspectable — each regex pattern maps to a specific intent with no ambiguity.
- **Testability.** Intent classification has comprehensive unit tests (15+ test cases) that run instantly without API calls.
- **Cost.** No token usage for routing decisions.

**Trade-offs:** Regex cannot handle truly ambiguous or novel phrasings as well as an LLM classifier. In practice, the current patterns cover all observed query types reliably. An LLM-based fallback could be added for edge cases if needed.

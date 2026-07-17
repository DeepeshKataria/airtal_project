# TASK: Airtel B2B AI Sales Assistant

## Goal
An AI assistant for Airtel Account Managers that answers questions about Airtel
Business products using RAG, and helps with meeting prep, product comparison,
sales pitches, objection handling, and follow-up emails.
Priority:
Correctness > Reliability > Maintainability > Speed > Extra features.
Never sacrifice correctness for additional features.

## Data source
Primary: https://www.airtel.in/b2b/ (public pages only — products, solutions,
FAQs). Prefer official Airtel pages over third-party sources. Do not attempt
to access anything requiring login.

If a page is blocked (JS-rendered, robots restrictions, etc.): save whatever
is accessible, log the rest in `MISSING_DATA.md` with URL and reason, and
keep going — never stall the build waiting on a page.

Phase 1 must produce:
- `data/raw/` populated with saved pages (markdown or text, one file per page,
  with source URL in a header comment)
- `MISSING_DATA.md` listing any page/section that couldn't be scraped
  automatically, with the URL and reason
- A note on total page/document count collected

## Phases (do them in order; commit + smoke-test after each)

**Phase 0 — Project setup**
Create the project structure and these files: `README.md`, `.env.example`,
`requirements.txt`, `.gitignore`, `PROJECT_STATUS.md`, `BLOCKERS.md`,
`MISSING_DATA.md` (empty/placeholder is fine for the last three at this
point — they get filled in as phases progress). Install dependencies in a
virtual environment.
*Smoke test: project installs cleanly in a fresh virtual environment, no
errors.*

**Phase 1 — Data**
Scrape public Airtel B2B pages → save to `data/raw/` → dedupe → chunk → save to
`data/processed/`. Build the ingestion so new docs can be dropped into
`data/raw/` and reprocessed without code changes.
*Smoke test: run the ingest script, confirm N documents chunked, no crashes.*

**Phase 2 — RAG core**
Embeddings (sentence-transformers) → ChromaDB → retriever. Simple CLI script
that takes a question and prints top-k retrieved chunks.
*Smoke test: ask "how to pitch Airtel SD-WAN" from the CLI, confirm relevant
chunks come back.*

**Phase 3 — LLM + agent loop**
Wire retriever to an LLM (Groq API — free, fast; fall back to OpenAI if I give
you a key). Write the system prompt in `src/prompts/`. Build the decision loop:
when to retrieve vs. answer directly vs. ask a clarifying question.
*Smoke test: CLI conversation answers a product question correctly and cites
which source chunk it used.*

**Phase 4 — Memory + features**
Add short-term conversation memory (last 5-6 turns). Add: product comparison,
meeting-prep generation, objection handling, follow-up email drafting — as
distinct callable functions/tools, not just prompt variations, so they can be
tested independently.
*Smoke test: multi-turn conversation stays coherent; each feature has one
working example.*

**Phase 5 — UI**
Streamlit app: chat, conversation history, source citations panel, retrieved-
docs debug panel, settings (model choice, temperature), loading states.
Should look polished enough to demo to Airtel management — professional
layout, avoid default-looking Streamlit where practical. Usability over
visual effects; don't spend Phase 5 time on cosmetics that don't serve
clarity. Extra visual polish is fine only after all 6 phases pass (see
"Explicitly NOT required" below).
*Smoke test: full conversation end-to-end in the browser, no crashes.*

**Phase 6 — Evals**
10-15 test questions with expected-correct answers (grounded in the scraped
data). Simple pass/fail script, no need for anything elaborate.
*Smoke test: eval script runs and reports a score.*

## Definition of done
- The app runs from a clean clone (fresh install of deps, no manual fixes)
  with `streamlit run app.py`
- All 6 phase smoke tests pass, with no unresolved runtime errors
- Code is modular (see CLAUDE.md structure) and maintainable, not one giant file
- PROJECT_STATUS.md reflects real state, not aspirational state
- MISSING_DATA.md and BLOCKERS.md exist (even if empty) and are accurate
- I can ask it 5 real Airtel B2B product questions and get grounded,
  non-hallucinated answers with citations

## Explicitly NOT required
- Finetuning (mentioned in earlier brainstorm — skip it; not worth the time
  for an internship demo, evals + solid RAG is more convincing)
- Docker deployment (nice-to-have only if time remains)
- Telegram bot (Streamlit only)
- Extra UI polish beyond Phase 5's bar — fine to add once all 6 phases pass
  and time remains, not before

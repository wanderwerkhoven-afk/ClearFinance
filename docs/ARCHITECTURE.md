# ClearFinance — technical architecture (research prototype)

## Current components
- **Frontend:** Next.js static site on GitHub Pages, PDF.js with page highlighting, IndexedDB document storage. No accounts.
- **API:** Python FastAPI, locally hosted. `POST /api/analyze` and `POST /api/ask` accept `{blocks:[{id,page,text}]}` from existing frontend.
- **Retrieval:** deterministic BM25 implemented in `backend/app/core.py`. Its ranking is a reproducible zero-cost baseline; no claim of semantic understanding.
- **Model:** local Ollama `qwen2.5:3b`, configurable. An available model is required for generated answers. Failures return clearly labeled literal excerpts instead.
- **Data:** optional SQLite FTS5 research store `backend/app/storage.py`. Browser remains the primary document store until a privacy-reviewed account architecture exists.
- **References:** generated points without known source IDs are discarded. Known ID ≠ proven factual support. Independent evaluation is required.
- **Security boundary:** NO AUTHENTICATION or rate limiting on research API. Bind to localhost only; DO NOT deploy on public internet or upload real bank/customer records. Frontend's public GitHub Pages deployment cannot reach a local HTTP API securely from HTTPS. Use both locally for live AI demos, or implement a secured HTTPS backend later.

## Interface example
```http
POST /api/analyze
Content-Type: application/json

{"blocks":[{"id":"p1-b1","page":1,"text":"De rente staat tien jaar vast."}]}
```

## Roadmap
1. Add document-layout extraction, scanned PDF OCR and source bounding boxes.
2. Compare BM25 to a local multilingual embedding retriever (BGE-M3) on annotated data.
3. Add a reranker, evaluate Recall@5/MRR.
4. Label claim/source pairs, train and validate an NLI baseline and fine-tuned model.
5. Separate authenticated user storage with encryption/retention controls.
6. Evaluate summarization comprehension, source precision and failure modes with participants.

## Research controls
- No dataset or trained verifier exists yet. Do not invent evaluation scores.
- Split by *document*, not individual chunks, to prevent data leakage.
- Track model version, prompts, seeds and datasets.
- Prefer public/synthetic financial documents until bank approvals exist.
- Model output is informational, not personalized advice.

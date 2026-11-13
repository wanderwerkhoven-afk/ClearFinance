# Summarization Engine V2 — Implementation and next gate

## Implemented in source
- Local Ollama generation, structured JSON, separate original citation IDs.
- Structure-aware chunks using optional `section` metadata and conservative heading inference.
- Chunk-level, section-level and document-level summarization.
- BM25 document-wide retrieval of original evidence for business-critical topics.
- Local model-call limit, transparent incomplete output and per-run audit object.
- `/api/analyze` uses V2, `/api/analyze/v1` uses previous implementation and `/api/analyze/flat` is original baseline.
- Automated tests mock the LLM so CI requires no Ollama or external services.

## Critical limitations and next work
1. The frontend currently sends flat text blocks and does not yet generate reliable `section` headings. Production-grade structure requires Docling and header/table parsing.
2. BM25 is only the lexical retrieval baseline; BGE-M3 and hybrid retrieval require separate benchmarking and locally downloaded model weights.
3. No request queue or checkpoint-resume for very long documents; `CLEARFINANCE_MAX_MODEL_CALLS` defaults to 200, and model processing can be slow. Limited result must remain visible.
4. The API has no authentication. Only local testing; do not expose it publicly or use confidential client records.
5. A citation ID can point at a real passage but still fail to entail the claim. The Evaluation Engine is required for factual validation.
6. No user-facing run-progress UI yet; server can process synchronously on developer machine.

## Experiment protocol
Compare `/api/analyze/flat`, `/api/analyze/v1`, and `/api/analyze` on the same publicly usable documents and same local LLM. Record generation time, coverage, source-ID validity, claim support by human raters and any critical omissions. Do not report synthetic scores as performance evidence.

## Model improvement
Use future Evaluation Engine to optimize prompts on a held-out validation set. Keep a separate final test set grouped by source document. This is prompt optimization, **not reinforcement learning** unless an actual RL objective and training procedure are implemented.

# ClearFinance hierarchical summarization + retrieval — V1

## Implemented
- Page-preserving text chunks over the existing PDF.js text blocks.
- Level 1: chunk summaries with source IDs.
- Level 2: batches of up to four chunks to section summaries.
- Level 3: document summary enriched with original passages retrieved via BM25 over *all* supplied blocks.
- Output compatible with the existing frontend `Analysis` type.
- Invalid/unrecognized source IDs are rejected at each level.
- Transparent fallback if Ollama is unavailable; partial-document processing flagged as `limited`.
- API: `POST /api/analyze/hierarchical` returns `{analysis,audit}`.
- Main `POST /api/analyze` now uses hierarchical pipeline by default. `POST /api/analyze/flat` retains original approach as baseline.

## Important limitations
- The input `blocks` currently has only ID, page and text; true heading-aware chunking, tables and geometric bounding boxes await Docling integration.
- Default is at most 32 chunks (approx 4,700 chars per chunk). Longer documents are **marked as limited**; this is not a complete summary of a 300-page report yet.
- BM25 is lexical retrieval, not vector RAG. BGE-M3 / FAISS integration is next.
- Known citation IDs only show that referenced passages exist. They do **not** prove semantic entailment or accuracy. Evaluation Engine is needed.
- Prompt-injection defense is best effort: documents are treated as untrusted text and should not contain instructions to the model.
- Avoid real bank/customer data: local research API has no authentication.
- Running Ollama locally costs no API fees but requires CPU/GPU, memory and time.
- Multi-stage generation can make many requests; for large documents optimize caching, incremental processing and batch workers.

## How to use
Install and launch Ollama and backend according to `backend/README.md`. The frontend currently calls `/api/analyze` and therefore uses hierarchical generation automatically with an active local backend. The public GitHub Pages site remains a non-AI demonstration.

For reproducible comparisons, keep the same input, Ollama model, sampling settings and datasets; compare `/api/analyze/flat` with `/api/analyze/hierarchical`. Next experiment: measure coverage and citation precision for both methods; later incorporate evaluation feedback into prompt revisions (not necessarily reinforcement learning).

## Prompt optimization roadmap
1. Freeze a held-out set of documents and human judgments.
2. Version prompts and identify target errors (missed financial risks, wrong numbers, weak citations).
3. Generate alternatives offline; compare with independent evaluator(s) and human judgments.
4. Change only documented prompt variables and retest; use the validation set, never tune on final test.
5. Only consider preference-based fine-tuning / RL if volume and quality of data justify it.

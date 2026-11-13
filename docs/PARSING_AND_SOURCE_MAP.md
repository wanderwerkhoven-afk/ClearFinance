# PDF/DOCX parsing with Docling

Install the optional heavy model stack locally:
```bash
pip install -r backend/requirements-docling.txt
```

Run local API and POST a PDF or DOCX as multipart `file` to `/api/parse`. The endpoint provides `{blocks:[{id,page,text,section,kind,bbox?}]}` with document reading order. This output can be fed to `/api/analyze` locally.

Use **public or synthetic files only**. API is unauthenticated and is not approved for real bank documents. Model weights may be downloaded at first run and can use substantial memory.

`bbox` originates from Docling's provenance; it is not yet rendered directly by the browser PDF viewer. Browser PDF.js currently uses text matching for highlights. PDF page size/coordinate conversions need integration and manual verification.

Limitations:
- The upload parser currently has a 20 MB file cap. There is no asynchronous job queue.
- Some complex tables and multicolumn layouts can be misread. Verify reading order and figures on held-out examples.
- The frontend currently extracts PDFs itself and uses existing flat source blocks; it does not yet call /api/parse automatically. This is an opt-in backend document pipeline.
- The research API remains local-only, with no authentication.

"""Local ingestion of public/synthetic PDF, TXT or parser-neutral JSON documents.

PDF extraction uses PyMuPDF only, no LLM. Each text block is traceable to a
page; page layout and table fidelity must still be manually audited.
"""
from __future__ import annotations
from pathlib import Path
import re
from .pipeline import Block, parse_json

def text_blocks(content: str) -> list[Block]:
    paragraphs=[x.strip() for x in re.split(r"\n\s*\n",content) if x.strip()]
    blocks=[]
    section="Document"
    for i,paragraph in enumerate(paragraphs,1):
        if "\n" not in paragraph and len(paragraph)<72 and not re.search(r"[.!?]$",paragraph):
            section=paragraph
        for j in range(0,len(paragraph),800):
            part=paragraph[j:j+800].strip()
            if part:
                blocks.append(Block(f"p1-b{len(blocks)+1}",1,section,part))
    if not blocks: raise ValueError("No readable text in file")
    return blocks

def pdf_blocks(path: str | Path, max_pages: int=200) -> list[Block]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PDF support requires: pip install pymupdf") from exc
    result=[]
    with fitz.open(str(path)) as doc:
        if doc.needs_pass: raise ValueError("Encrypted PDFs are unsupported")
        if len(doc)>max_pages: raise ValueError(f"PDF exceeds {max_pages} page limit")
        for page_num,page in enumerate(doc,1):
            section=f"Pagina {page_num}"
            raw=page.get_text("blocks",sort=True)
            for item in raw:
                if len(item)<5:continue
                text=str(item[4]).strip()
                if not text:continue
                # Preserve original reading-order block before segmentation.
                first=text.splitlines()[0].strip()
                if 5<=len(first)<=85 and len(text)<110 and not re.search(r"[.!?]$",first):
                    section=first[:100]
                for part in (text[i:i+850] for i in range(0,len(text),850)):
                    part=part.strip()
                    if len(part)>5:
                        result.append(Block(f"p{page_num}-b{len(result)+1}",page_num,section,part))
    if not result: raise ValueError("No selectable text: scanned PDF needs OCR")
    return result

def load_document(path: str | Path) -> list[Block]:
    path=Path(path)
    if path.suffix.lower()==".json":return parse_json(path)
    if path.suffix.lower()==".txt":return text_blocks(path.read_text(encoding="utf-8"))
    if path.suffix.lower()==".pdf":return pdf_blocks(path)
    raise ValueError("Allowed inputs: PDF, TXT, JSON")

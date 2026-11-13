"""Document layout parsing with optional Docling (local-only).

Docling is deliberately optional: regular backend CI stays lightweight.
Source blocks preserve section, page and original-page bounding box metadata.
"""
from __future__ import annotations
from io import BytesIO
from typing import Any

MAX_FILE_BYTES = 20 * 1024 * 1024

def to_blocks(doc: Any, max_text: int = 1100) -> list[dict]:
    """Convert Docling reading-order items into serializable source blocks."""
    blocks=[]
    section="Algemeen"
    for item, _level in doc.iterate_items():
        label=str(getattr(item,"label","")).lower()
        if "section_header" in label or label.endswith("title"):
            heading=str(getattr(item,"text","")).strip()
            if heading:
                section=heading[:100]
        text=str(getattr(item,"text","") or "")
        if "table" in label and hasattr(item,"export_to_markdown"):
            try:
                text=item.export_to_markdown(doc=doc)
            except (ValueError,TypeError,AttributeError):
                text=text or "[Tabel zonder uitleesbare tekst]"
        text=" ".join(text.split()).strip()
        if not text:
            continue
        prov=getattr(item,"prov",[]) or []
        page=int(prov[0].page_no) if prov else 1
        source_bbox=None
        if prov and getattr(prov[0],"bbox",None) is not None:
            bbox=prov[0].bbox
            source_bbox={
                "l":float(bbox.l),"t":float(bbox.t),"r":float(bbox.r),
                "b":float(bbox.b),"origin":str(getattr(bbox,"coord_origin","BOTTOMLEFT"))
            }
        # Fragment ID remains unique and is scoped to original page.
        for i in range(0,len(text),max_text):
            segment=text[i:i+max_text]
            if len(segment)<8:
                continue
            id_=f"p{page}-b{len(blocks)+1}"
            b={"id":id_,"page":page,"text":segment,"section":section,"kind":"table" if "table" in label else "text"}
            if source_bbox:
                b["bbox"]=source_bbox
            blocks.append(b)
    return blocks

def parse_file(data: bytes, filename: str) -> list[dict]:
    """Blocking Docling invocation; call via asyncio.to_thread from API."""
    if not filename.lower().endswith((".pdf",".docx")):
        raise ValueError("Only PDF and DOCX are supported by the parser")
    if not data or len(data)>MAX_FILE_BYTES:
        raise ValueError("Empty document or file too large (20MB max)")
    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import DocumentStream
    except ImportError as exc:
        raise RuntimeError("Docling missing; install backend/requirements-docling.txt") from exc
    result=DocumentConverter().convert(DocumentStream(name=filename,stream=BytesIO(data)))
    blocks=to_blocks(result.document)
    if not blocks:
        raise ValueError("No extractable text found")
    return blocks

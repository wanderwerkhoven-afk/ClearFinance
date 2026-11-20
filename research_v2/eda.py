"""Minimal transparent EDA from parser-neutral source blocks."""
import re
from collections import Counter
from .metrics import numbers
def describe(blocks):
    if not blocks: raise ValueError("No documents")
    sections=Counter(b.section for b in blocks)
    pages=sorted(set(b.page for b in blocks))
    return {
        "block_count":len(blocks),
        "page_count":len(pages),
        "sections":dict(sorted(sections.items())),
        "table_blocks":sum(b.kind=="table" for b in blocks),
        "characters":sum(len(b.text) for b in blocks),
        "approx_tokens_whitespace":sum(len(b.text.split()) for b in blocks),
        "numeric_candidates":sum(len(numbers(b.text)) for b in blocks),
        "year_occurrences":sum(len(re.findall(r"\b(?:19|20)\d{2}\b",b.text)) for b in blocks),
        "note":"Whitespace token counts and number candidates are proxies; not actual LLM tokenization or verified table extraction."
    }

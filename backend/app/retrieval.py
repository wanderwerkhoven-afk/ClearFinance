"""Optional local BGE-M3 dense or hybrid retrieval with BM25 fallback."""
from __future__ import annotations
import os
from functools import lru_cache
from .core import rank_bm25

DEFAULT_MODE = os.getenv("CLEARFINANCE_RETRIEVAL", "bm25").lower()
MODEL_NAME = os.getenv("CLEARFINANCE_EMBEDDING_MODEL", "BAAI/bge-m3")

@lru_cache(maxsize=2)
def load_encoder(name: str):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name, trust_remote_code=False)

def rank(blocks: list[dict], query: str, k: int = 8, mode: str = "bm25", encoder=None):
    if mode not in ("bm25", "dense", "hybrid"):
        raise ValueError("Invalid retrieval mode")
    if not blocks:
        return [], mode
    if mode == "bm25":
        return rank_bm25(blocks, query, k), mode
    try:
        model = encoder if encoder is not None else load_encoder(MODEL_NAME)
        embeddings = model.encode([b["text"] for b in blocks], normalize_embeddings=True, convert_to_numpy=True)
        question = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
        scores = embeddings @ question
        dense = sorted(range(len(blocks)), key=lambda i: (-float(scores[i]), i))
    except (ImportError, RuntimeError, OSError, ValueError) as error:
        return rank_bm25(blocks, query, k), f"bm25-fallback:{type(error).__name__}"
    if mode == "dense":
        return [blocks[i] for i in dense[:k]], mode
    lexical = rank_bm25(blocks, query, len(blocks))
    id_to_index = {b["id"]: i for i,b in enumerate(blocks)}
    votes = {}
    for ordering in (lexical, [blocks[i] for i in dense]):
        for position, item in enumerate(ordering, 1):
            votes[item["id"]] = votes.get(item["id"], 0.0) + 1/(60 + position)
    ids = sorted(votes, key=lambda ident: (-votes[ident], id_to_index[ident]))
    return [blocks[id_to_index[ident]] for ident in ids[:k]], mode

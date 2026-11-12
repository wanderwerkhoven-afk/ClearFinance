"""Standalone BM25 benchmark without fabricated results."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "backend"))
from app.core import rank_bm25

def evaluate(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("Empty evaluation data")
    ranks = []
    for row in rows:
        relevant = set(row["relevant_ids"])
        if not relevant:
            raise ValueError(f'No gold evidence for {row.get("document_id","unknown")}')
        ranking = [x["id"] for x in rank_bm25(row["blocks"],row["question"],len(row["blocks"]))]
        ranks.append(next((i + 1 for i,id_ in enumerate(ranking) if id_ in relevant),None))
    n = len(ranks)
    return {"questions":n,
            "recall_at_1":sum(r is not None and r<=1 for r in ranks)/n,
            "recall_at_5":sum(r is not None and r<=5 for r in ranks)/n,
            "mrr":sum(1/r for r in ranks if r is not None)/n}

def main(path: str) -> None:
    rows=[json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(evaluate(rows),indent=2))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python research/evaluate_retrieval.py gold.jsonl")
    main(sys.argv[1])

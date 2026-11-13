from app.retrieval import rank

BLOCKS=[
    {"id":"p1-b1","page":1,"text":"Vaste hypotheekrente tien jaar"},
    {"id":"p1-b2","page":1,"text":"Vervroegd aflossen zonder boete"},
    {"id":"p2-b3","page":2,"text":"Omzet en winst"}
]

def test_bm25_baseline():
    hits,mode=rank(BLOCKS,"hypotheekrente",mode="bm25")
    assert hits[0]["id"]=="p1-b1"
    assert mode=="bm25"

def test_fallback_without_embeddings(monkeypatch):
    def fail(name):
        raise ImportError("offline")
    monkeypatch.setattr("app.retrieval.load_encoder",fail)
    hits,mode=rank(BLOCKS,"aflossen",mode="hybrid")
    assert hits[0]["id"]=="p1-b2"
    assert mode.startswith("bm25-fallback")

def test_invalid_mode_rejected():
    import pytest
    with pytest.raises(ValueError):
        rank(BLOCKS,"anything",mode="invalid")

def test_hybrid_fusion_with_fake_vectors():
    import numpy as np
    class FakeEncoder:
        def encode(self,texts,**kwargs):
            return np.asarray([[1.,0.] if "aflossen" in t else [0.,1.] for t in texts])
    hits,mode=rank(BLOCKS,"aflossen",3,mode="hybrid",encoder=FakeEncoder())
    assert mode=="hybrid"
    assert hits[0]["id"]=="p1-b2"
    assert len({b["id"] for b in hits})==3

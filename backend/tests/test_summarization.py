import asyncio
from app.summarization import make_chunks, hierarchical_analyze, extract_points, retrieval_evidence
from app.main import app
from fastapi.testclient import TestClient

BLOCKS=[
    {"id":f"p{i+1}-b{i+1}","page":i+1,"text":t}
    for i,t in enumerate([
        "De omzet bedroeg 120 miljoen euro in 2025.",
        "De nettowinst daalde door hoge financieringslasten.",
        "De schuld is 50 miljoen euro en de rente varieert.",
        "Een liquiditeitsrisico kan extra financiering vereisen.",
        "De onderneming verwacht voor 2026 groei.",
        "Een verplichting vervalt op 1 januari 2027.",
    ])
]

def fake_model(prompt):
    async def run():
        import re
        ids=list(dict.fromkeys(re.findall(r"p\d+-b\d+",prompt)))
        if "STAP 3/3" in prompt:
            return {"headline":"Overzicht","introduction":"Gebaseerd op het document",
                    "sections":[{"title":"Financieel", "points":[{"text":"De omzet is 120 miljoen.","sourceIds":[ids[0]]}]}],
                    "keyTerms":[]}
        if "STAP 2/3" in prompt:
            return {"title":"Financieel overzicht","points":[{"text":"Feiten uit de bron","sourceIds":[ids[0]]}]}
        return {"points":[{"text":"Een feit.","sourceIds":[ids[0]]}]}
    return run()

def test_preserve_order_and_page_boundaries():
    long_blocks=[{**b,"text":b["text"]*12} for b in BLOCKS]
    chunks=make_chunks(long_blocks, max_chars=1200)
    assert [b["id"] for c in chunks for b in c.blocks]==[b["id"] for b in long_blocks]
    assert len(chunks)>1

def test_unsupported_ids_removed():
    assert extract_points({"points":[{"text":"Verzonnen","sourceIds":["p999-b999"]}]},BLOCKS)==[]

def test_three_level_pipeline_yields_frontend_contract():
    result,audit=asyncio.run(hierarchical_analyze(BLOCKS,fake_model))
    assert result["mode"]=="ai"
    assert result["sections"][0]["points"][0]["sourceIds"][0] in {b["id"] for b in BLOCKS}
    assert audit["method"]=="hierarchical-rag"
    assert audit["processedBlocks"]==6
    assert audit["generation"]=="ai"

def test_partial_coverage_explicit():
    long_blocks=[{**b,"text":b["text"]*35} for b in BLOCKS]
    result,audit=asyncio.run(hierarchical_analyze(long_blocks,fake_model,max_chunks=1))
    assert result["limited"] is True
    assert audit["processedChunks"]==1
    assert any("niet volledig verwerkt" in w for w in audit["warnings"])

def test_no_model_does_not_fake_ai():
    async def fail(prompt):
        raise ConnectionError("offline")
    result,audit=asyncio.run(hierarchical_analyze(BLOCKS,fail))
    assert result["mode"]=="local"
    assert "Geen AI-output beschikbaar" in " ".join(audit["warnings"])

def test_retrieval_returns_existing_source_ids():
    assert set(b["id"] for b in retrieval_evidence(BLOCKS)).issubset(set(b["id"] for b in BLOCKS))

def test_route_is_available():
    client=TestClient(app)
    response=client.post("/api/analyze/hierarchical",json={"blocks":BLOCKS})
    # It may fall back if Ollama is absent; the endpoint retains the contract.
    assert response.status_code==200
    assert "analysis" in response.json() and "audit" in response.json()

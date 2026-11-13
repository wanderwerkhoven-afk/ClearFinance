import asyncio
from app.summarization_v2 import chunk_document, summarize

BLOCKS=[
 {"id":"p1-b1","page":1,"text":"1. Financiële resultaten","section":"Financiële resultaten"},
 {"id":"p1-b2","page":1,"text":"De omzet steeg naar 150 miljoen euro.","section":"Financiële resultaten"},
 {"id":"p2-b3","page":2,"text":"2. Risico's","section":"Risico's"},
 {"id":"p2-b4","page":2,"text":"Het renterisico kan toekomstige kosten verhogen.","section":"Risico's"}
]
async def stub(prompt):
    import re
    ids=list(dict.fromkeys(re.findall(r"p\d+-b\d+",prompt)))
    if "DOCUMENT LEVEL" in prompt:
        return {"headline":"Samenvatting","introduction":"Kernpunten","sections":[
            {"title":"Belangrijk","points":[{"text":"Er is een renterisico.","sourceIds":[ids[-1]]}]}],"keyTerms":[]}
    return {"points":[{"text":"Dit is een brongebonden feit.","sourceIds":[ids[-1]]}]}

def test_structure_aware_chunks():
    chunks=chunk_document(BLOCKS)
    assert len(chunks)==2
    assert chunks[0].section=="Financiële resultaten"
    assert chunks[1].section=="Risico's"
    assert [b["id"] for c in chunks for b in c.blocks]==[b["id"] for b in BLOCKS]

def test_hierarchy_full_coverage_and_audit():
    analysis,audit=asyncio.run(summarize(BLOCKS,stub))
    assert analysis["mode"]=="ai"
    assert analysis["limited"] is False
    assert audit["complete"] is True
    assert audit["processedBlocks"]==len(BLOCKS)
    assert audit["sectionCount"]==2
    assert audit["modelCalls"]==5

def test_budget_partial_is_disclosed():
    analysis,audit=asyncio.run(summarize(BLOCKS,stub,max_calls=1))
    assert analysis["limited"] is True
    assert audit["processedChunks"]<audit["chunkCount"]
    assert audit["generation"]=="partial"
    assert any("limiet" in w for w in audit["warnings"])

def test_unknown_source_ids_never_displayed():
    async def malicious(prompt):
        if "DOCUMENT LEVEL" in prompt:
            return {"headline":"Fout","introduction":"","sections":[{"title":"Fout","points":[
                {"text":"Fictieve winst","sourceIds":["fabricated-id"]}]}],"keyTerms":[]}
        return {"points":[{"text":"Ondersteund","sourceIds":["p1-b2"]}]}
    analysis,audit=asyncio.run(summarize(BLOCKS,malicious))
    assert all("fabricated-id" not in p["sourceIds"] for s in analysis["sections"] for p in s["points"])
    assert analysis["limited"]

def test_no_model_marks_local_not_ai():
    async def offline(prompt):
        raise ConnectionError("Ollama unavailable")
    analysis,audit=asyncio.run(summarize(BLOCKS,offline))
    assert analysis["mode"]=="local"
    assert analysis["limited"] is True
    assert audit["generation"]=="local"

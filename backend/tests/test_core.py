from app.core import rank_bm25, sanitize_analysis, local_summary
from fastapi.testclient import TestClient
from app.main import app

BLOCKS=[
 {"id":"p1-b1","page":1,"text":"De hypotheekrente is 3,8 procent voor de eerste tien jaar."},
 {"id":"p2-b2","page":2,"text":"Na tien jaar wordt de rente opnieuw vastgesteld."},
 {"id":"p3-b3","page":3,"text":"Vervroegd aflossen kan kosten met zich meebrengen."}
]

def test_bm25_finds_relevant_evidence():
    assert rank_bm25(BLOCKS,"Wat is de hypotheekrente?")[0]["id"]=="p1-b1"

def test_no_invented_citations():
    result=sanitize_analysis({"headline":"Test","introduction":"",
        "sections":[{"title":"Uitkomst","points":[
            {"text":"Ongefundeerd","sourceIds":["invented"]},
            {"text":"Wel ondersteund","sourceIds":["p2-b2"]}]}],
        "keyTerms":[]},BLOCKS,False)
    assert len(result["sections"][0]["points"])==1
    assert result["sections"][0]["points"][0]["sourceIds"]==["p2-b2"]

def test_fallback_is_clearly_labeled():
    assert local_summary(BLOCKS)["mode"]=="local"

def test_health_and_validation():
    client=TestClient(app)
    assert client.get("/api/health").json()["ok"] is True
    assert client.post("/api/analyze",json={"blocks":[{"id":"invalid","page":1,"text":"x"}]}).status_code==422
    assert client.post("/api/analyze",json={"blocks":[]}).status_code==422

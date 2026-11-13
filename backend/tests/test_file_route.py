from fastapi.testclient import TestClient
from app import main

def test_analyze_file_end_to_end_contract_with_stubbed_parser(monkeypatch):
    # Avoids heavy Docling and Ollama installation in CI while checking API wiring.
    sample=[{"id":"p1-b1","page":1,"text":"De omzet bedroeg 100 miljoen euro.","section":"Resultaat"}]
    monkeypatch.setattr(main,"parse_file",lambda data,name:sample)
    async def fake_summarize(blocks):
        assert blocks==sample
        return ({"headline":"Omzet","introduction":"De omzet bedraagt 100 miljoen euro.",
                 "sections":[{"title":"Resultaat","points":[{"id":"ai-0","text":"Omzet is 100 miljoen.","sourceIds":["p1-b1"]}]}],
                 "keyTerms":[],"mode":"ai","limited":False},
                {"method":"hierarchical-rag","complete":True,"processedBlocks":1})
    monkeypatch.setattr(main,"summarize",fake_summarize)
    response=TestClient(main.app).post("/api/analyze/file",files={"file":("report.pdf",b"%PDF mocked","application/pdf")})
    assert response.status_code==200
    assert response.json()["blocks"][0]["section"]=="Resultaat"
    assert response.json()["analysis"]["sections"][0]["points"][0]["sourceIds"]==["p1-b1"]

def test_upload_file_type_rejected():
    response=TestClient(main.app).post("/api/analyze/file",files={"file":("evil.exe",b"hello","application/octet-stream")})
    assert response.status_code==415

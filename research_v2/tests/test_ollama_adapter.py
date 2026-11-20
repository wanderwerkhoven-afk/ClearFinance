"""Contract tests for local-only Ollama integration (no actual GPU/model in CI)."""
import json
from unittest.mock import patch
from research_v2.pipeline import Claim,OllamaMerger

class FakeResponse:
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,*args):return b""

def test_ollama_contract_and_provenance(monkeypatch):
    captured={}
    class Response(FakeResponse):
        def __iter__(self):return iter([])
    def fake_urlopen(req,timeout=0):
        captured["url"]=req.full_url
        captured["request"]=json.loads(req.data)
        class R(FakeResponse):
            def read(self,*args):
                return json.dumps({
                    "message":{"content":json.dumps({"text":"De omzet is 120 miljoen euro.","source_ids":["p1-b1","fake"]})},
                    "prompt_eval_count":25,"eval_count":17,
                }).encode()
        return R()
    monkeypatch.setattr("research_v2.pipeline.urlopen",fake_urlopen)
    merger=OllamaMerger(model="qwen2.5:7b",seed=42)
    output=merger.merge([Claim("L1-1","De omzet is 120 miljoen euro.",["p1-b1"])],"L2-C1")
    assert captured["url"]=="http://127.0.0.1:11434/api/chat"
    assert captured["request"]["options"]["seed"]==42
    assert captured["request"]["options"]["temperature"]==0
    assert captured["request"]["stream"] is False
    assert output.source_ids==["p1-b1"]
    assert output.origin_ids==["L1-1"]
    assert merger.calls==1 and merger.tokens==42

def test_ollama_rejects_unverified_claim(monkeypatch):
    def response(req,timeout=0):
        class R(FakeResponse):
            def read(self,*args):
                return json.dumps({"message":{"content":json.dumps(
                    {"text":"Claims","source_ids":["unknown"]})}}).encode()
        return R()
    monkeypatch.setattr("research_v2.pipeline.urlopen",response)
    import pytest
    with pytest.raises(ValueError,match="Unverifiable"):
        OllamaMerger().merge([Claim("L1-1","Value 12",["p1-b1"])],"L2")

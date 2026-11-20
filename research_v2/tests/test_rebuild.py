import json
from pathlib import Path
import pytest
from research_v2.pipeline import Block,OllamaMerger,parse_json,run
from research_v2.metrics import evaluate,number_check,rouge_n,rouge_l
from research_v2.injections import inject_number,inject_year,inject_omission

FIXTURE=Path(__file__).parents[1]/"fixtures/synthetic_report.json"

def test_pipeline_is_reproducible_and_all_layers_traceable():
    blocks=parse_json(FIXTURE)
    result=run(blocks,fan_in=3)
    again=run(blocks,fan_in=3)
    assert len(result["layers"])==3
    assert result["layers"][-1]["claims"]==again["layers"][-1]["claims"]
    assert result["run"]["source_hash"]==again["run"]["source_hash"]
    assert result["run"]["llm_calls"]==0
    assert all(c["source_ids"] for layer in result["layers"] for c in layer["claims"])
    assessed=evaluate(result)
    assert all(x["source_pages"] for level in assessed["levels"] for x in level["checks"])

def test_numeric_injection_review_and_rouge_stability():
    text="De omzet bedroeg 120 miljoen euro in 2025."
    injected=inject_number(text,"120","125")
    assert number_check(text,[text])["status"]=="pass"
    assert number_check(injected["mutated"],[text])["status"]=="review"
    assert rouge_n(text,injected["mutated"],1)>0.5

def test_year_and_omission():
    assert inject_year("Winst steeg in 2025",2025,2024)["kind"]=="wrong_year"
    assert inject_omission([{"id":"risk"},{"id":"profit"}],"risk")["target"]=="risk"

def test_rouge_baselines():
    assert rouge_n("x y z","x y z",1)==1
    assert rouge_l("x y z","x y z")==1
    assert rouge_n("x y z","a b c",2)==0

def test_external_host_rejected():
    with pytest.raises(ValueError): OllamaMerger(endpoint="https://api.example.org")

def test_invalid_provenance_reported():
    result=run([Block("p1-b1",1,"A","De omzet steeg")])
    result["layers"][-1]["claims"][0]["source_ids"]=["fake"]
    assert evaluate(result)["levels"][-1]["checks"][0]["invalid_ids"]==["fake"]

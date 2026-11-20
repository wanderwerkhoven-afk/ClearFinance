from pathlib import Path
from research_v2.experiments import synthetic_experiment
from research_v2.eda import describe
from research_v2.pipeline import Block

def test_synthetic_experiment_runs_and_reports_metrics():
    path=Path(__file__).parents[1]/"fixtures/synthetic_report.json"
    out=synthetic_experiment(path)
    assert out["eda"]["block_count"]==7
    assert out["eda"]["table_blocks"]==1
    assert len(out["cases"])==4
    assert out["cases"][0]["numeric"]=="pass"
    assert out["cases"][1]["numeric"]=="review"
    assert out["cases"][2]["numeric"]=="review"

def test_empty_eda_fails():
    import pytest
    with pytest.raises(ValueError):describe([])

"""Run from repo root: python -m research_v2.cli --input research_v2/fixtures/synthetic_report.json."""
import argparse,json
from pathlib import Path
from .pipeline import ExtractiveMerger,OllamaMerger,parse_json,run
from .metrics import evaluate
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--out",default="research_v2/output")
    parser.add_argument("--merger",choices=["extractive","ollama"],default="extractive")
    parser.add_argument("--model",default="qwen2.5:7b")
    parser.add_argument("--seed",type=int,default=42)
    parser.add_argument("--fan-in",type=int,default=3)
    a=parser.parse_args()
    merger=OllamaMerger(a.model,seed=a.seed) if a.merger=="ollama" else ExtractiveMerger()
    result=run(parse_json(a.input),merger,a.fan_in)
    output=Path(a.out);output.mkdir(parents=True,exist_ok=True)
    (output/"layers.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    assessment=evaluate(result)
    (output/"metrics.json").write_text(json.dumps(assessment,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"method":result["run"]["method"],"layers":len(result["layers"]),
                      "llm_calls":result["run"]["llm_calls"],
                      "numeric_reviews":sum(x["numeric_review_count"] for x in assessment["levels"]),
                      "output":str(output)},ensure_ascii=False))
if __name__=="__main__":main()

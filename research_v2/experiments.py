"""Fixed synthetic error-injection benchmark, NOT a domain validity claim."""
from __future__ import annotations
import json
from pathlib import Path
from .pipeline import parse_json
from .metrics import number_check,rouge_n,rouge_l
from .injections import inject_number,inject_year
from .eda import describe
def synthetic_experiment(path):
    blocks=parse_json(path)
    probe=next(b for b in blocks if "120 miljoen" in b.text)
    original=probe.text
    variants=[
        {"kind":"unchanged","mutated":original,"expected":"pass"},
        inject_number(original,"120","125"),
        inject_year(original,2025,2024),
        {"kind":"benign_reorder","mutated":"In 2025 bedroeg de omzet 120 miljoen euro.","expected":"pass"},
    ]
    results=[]
    for variant in variants:
        text=variant["mutated"]
        results.append({"kind":variant["kind"],"expected":variant["expected"],
                        "numeric":number_check(text,[original])["status"],
                        "rouge1_f1":round(rouge_n(original,text,1),4),
                        "rouge2_f1":round(rouge_n(original,text,2),4),
                        "rougeL_f1":round(rouge_l(original,text),4)})
    return {"dataset":"synthetic_report.json","eda":describe(blocks),"cases":results,
            "warning":"Synthetic illustrative examples, not accuracy/sensitivity estimates."}
def main():
    path=Path(__file__).parent/"fixtures/synthetic_report.json"
    output=Path(__file__).parent/"output"/"first_metric_experiment.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    content=synthetic_experiment(path)
    output.write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"saved":str(output),"cases":len(content["cases"]),"eda_blocks":content["eda"]["block_count"]},ensure_ascii=False))
if __name__=="__main__":main()

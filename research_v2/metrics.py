"""Deterministic *candidate* checks. Semantic faithfulness is deliberately not fabricated."""
from __future__ import annotations
import re
from decimal import Decimal,InvalidOperation
from collections import Counter
NUMBER=re.compile(r'(?<!\w)(?:€\s*)?[-+]?\d{1,3}(?:[., ]\d{3})*(?:[.,]\d+)?|(?<!\w)(?:€\s*)?[-+]?\d+(?:[.,]\d+)?')
YEAR=re.compile(r'\b(?:19|20)\d{2}\b')
UNIT=re.compile(r'€|\b(?:euro|eur|miljoen|mln|mrd|miljard|duizend|procent|bp|basispunten)\b|%',re.I)

def normalize(x):
    x=x.replace("€","").replace(" ","")
    if "," in x and "." in x:
        sep="," if x.rfind(",")>x.rfind(".") else "."
        x=x.replace("." if sep=="," else ",","").replace(sep,".")
    elif "," in x:
        p=x.split(",")
        x="".join(p) if len(p)>1 and all(len(t)==3 for t in p[1:]) else x.replace(",",".")
    elif "." in x:
        p=x.split(".")
        if len(p)>1 and all(len(t)==3 for t in p[1:]):x="".join(p)
    try:return str(Decimal(x).normalize())
    except InvalidOperation:return None

def numbers(text):
    found=[]
    for m in NUMBER.finditer(text):
        value=normalize(m.group())
        if value is None:continue
        area=text[max(0,m.start()-18):m.end()+25]
        y=YEAR.search(area)
        found.append({"value":value,"year":y.group() if y else None,
                      "units":[x.lower() for x in UNIT.findall(area)][:3],"raw":m.group().strip()})
    return found

def number_check(claim,evidence):
    reference=[n for p in evidence for n in numbers(p)]
    detected=numbers(claim)
    misses=[]
    for n in detected:
        matched=any(n["value"]==s["value"] and
                    (not n["year"] or not s["year"] or n["year"]==s["year"]) and
                    (not n["units"] or not s["units"] or set(n["units"])&set(s["units"]))
                    for s in reference)
        if not matched: misses.append(n)
    return {"status":"not_applicable" if not detected else "review" if misses else "pass",
            "unmatched":misses,"detected":detected}

def rouge_n(reference,candidate,n=1):
    def count(text):
        t=re.findall(r'\w+',text.lower(),flags=re.UNICODE)
        return Counter(tuple(t[i:i+n]) for i in range(len(t)-n+1))
    a,b=count(reference),count(candidate)
    common=sum((a&b).values());p=common/max(1,sum(b.values()));r=common/max(1,sum(a.values()))
    return 2*p*r/(p+r) if p+r else 0.

def rouge_l(reference,candidate):
    a=re.findall(r'\w+',reference.lower());b=re.findall(r'\w+',candidate.lower())
    dp=[0]*(len(b)+1)
    for x in a:
        next_dp=[0]
        for j,y in enumerate(b,1): next_dp.append(dp[j-1]+1 if x==y else max(dp[j],next_dp[-1]))
        dp=next_dp
    count=dp[-1];p=count/max(1,len(b));r=count/max(1,len(a))
    return 2*p*r/(p+r) if p+r else 0.

def evaluate(run):
    source={b["id"]:b for b in run["source"]}
    prev=None
    layers=[]
    for layer in run["layers"]:
        checks=[]
        for claim in layer["claims"]:
            actual=[source[i] for i in claim["source_ids"] if i in source]
            origins={x["id"] for x in prev["claims"]} if prev else set()
            checks.append({"claim_id":claim["id"],"source_pages":sorted(set(x["page"] for x in actual)),
                           "invalid_ids":[i for i in claim["source_ids"] if i not in source],
                           "numeric":number_check(claim["text"],[x["text"] for x in actual]),
                           "lineage_valid":all(x in origins for x in claim["origin_ids"]) if prev else None,
                           "local_faithfulness":"not_evaluated","global_faithfulness":"not_evaluated",
                           "drift":"not_evaluated"})
        previous_chars=sum(len(c["text"]) for c in prev["claims"]) if prev else sum(len(s["text"]) for s in run["source"])
        current_chars=sum(len(c["text"]) for c in layer["claims"])
        layers.append({"level":layer["level"],"compression_ratio_char":round(current_chars/max(1,previous_chars),4),
                       "checks":checks,"numeric_review_count":sum(x["numeric"]["status"]=="review" for x in checks)})
        prev=layer
    return {"method":"deterministic-prototype-v0","levels":layers,
            "limitations":"Not a semantic or calibrated faithfulness judge. Review numbers manually, especially PDF table context."}

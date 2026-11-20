"""Synthetic corruption fixtures for preliminary metric validation."""
import re
def inject_number(text,old,new):
    pat=r'(?<!\w)'+re.escape(str(old))+r'(?!\w)'
    if not re.search(pat,text):raise ValueError("Number absent")
    return {"kind":"wrong_number","original":text,
            "mutated":re.sub(pat,str(new),text,count=1),"expected":"contradicted"}
def inject_year(text,old,new):
    if old==new or not 1900<=old<=2099 or not 1900<=new<=2099:raise ValueError("Invalid years")
    row=inject_number(text,old,new);row["kind"]="wrong_year";return row
def inject_omission(claims,claim_id):
    if not any(c["id"]==claim_id for c in claims):raise ValueError("Missing claim")
    return {"kind":"critical_omission","mutated":[c for c in claims if c["id"]!=claim_id],
            "target":claim_id,"expected":"coverage_fail"}

"""Optional local cache. OFF by default; not suitable for private bank content."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

def root():
    value=os.getenv("CLEARFINANCE_CACHE_DIR","").strip()
    return Path(value).expanduser() if value else None

def fingerprint(prompt,model,version):
    text=json.dumps([prompt,model,version],ensure_ascii=False)
    return hashlib.sha256(text.encode()).hexdigest()

def load(prompt,model,version):
    folder=root()
    if not folder:
        return None
    try:
        data=json.loads((folder/(fingerprint(prompt,model,version)+".json")).read_text(encoding="utf8"))
        return data if isinstance(data,dict) else None
    except (ValueError,OSError):
        return None

def save(prompt,model,version,result):
    folder=root()
    if not folder:
        return
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/(fingerprint(prompt,model,version)+".json")
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf8",dir=folder,delete=False) as out:
        json.dump(result,out,ensure_ascii=False)
        temp=out.name
    os.replace(temp,target)

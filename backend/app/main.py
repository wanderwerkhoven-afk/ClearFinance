"""ClearFinance research backend. Local only: no auth; never publicly expose."""
from __future__ import annotations
import os
import re
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from .core import analyze, answer
from .summarization import hierarchical_analyze
from .summarization_v2 import summarize
from . import storage
from .parsing import parse_file, MAX_FILE_BYTES

app = FastAPI(title="ClearFinance Research API", version="0.2.0")
origins = [o.strip() for o in os.getenv("CLEARFINANCE_ORIGINS","http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=False,allow_methods=["GET","POST","DELETE"],allow_headers=["Content-Type"])

class BoundingBox(BaseModel):
    l: float
    t: float
    r: float
    b: float
    origin: str = "BOTTOMLEFT"

class Block(BaseModel):
    id: str = Field(pattern=r"^(p\d+-b\d+|demo-[a-z0-9]+)$")
    page: int = Field(ge=1, le=10000)
    text: str = Field(min_length=1,max_length=1200)
    section: str | None = Field(default=None,max_length=100)
    kind: str | None = Field(default=None,max_length=30)
    bbox: BoundingBox | None = None
    @field_validator("text")
    @classmethod
    def no_whitespace_only(cls,value: str) -> str:
        if not value.strip():
            raise ValueError("Empty block")
        return value

class Document(BaseModel):
    blocks: list[Block] = Field(min_length=1,max_length=4000)

class Question(Document):
    question: str = Field(min_length=3,max_length=800)

class SaveDocument(Document):
    name: str = Field(min_length=1,max_length=200)

def blocks_data(items: list[Block]) -> list[dict]:
    ids = [b.id for b in items]
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=422,detail="Duplicated block IDs")
    return [b.model_dump() for b in items]

@app.post("/api/analyze/file")
async def analyze_uploaded_file(file: UploadFile = File(...)):
    """Single-call local PDF/DOCX → structured blocks → hierarchical summary."""
    name=file.filename or ""
    if not name.lower().endswith((".pdf",".docx")):
        raise HTTPException(status_code=415,detail="PDF or DOCX required")
    data=await file.read(MAX_FILE_BYTES+1)
    if len(data)>MAX_FILE_BYTES:
        raise HTTPException(status_code=413,detail="File exceeds 20MB")
    try:
        blocks=await asyncio.to_thread(parse_file,data,name)
        analysis,audit=await summarize(blocks)
    except (ValueError,RuntimeError) as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"analysis":analysis,"audit":audit,"blocks":blocks}

@app.post("/api/parse")
async def parse_upload(file: UploadFile = File(...)):
    name=file.filename or ""
    if not name.lower().endswith((".pdf",".docx")):
        raise HTTPException(status_code=415,detail="PDF or DOCX required")
    data=await file.read(MAX_FILE_BYTES+1)
    if len(data)>MAX_FILE_BYTES:
        raise HTTPException(status_code=413,detail="File exceeds 20MB")
    try:
        blocks=await asyncio.to_thread(parse_file,data,name)
    except (ValueError,RuntimeError) as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"blocks":blocks,"count":len(blocks)}

@app.get("/api/health")
def health():
    return {"ok":True,"provider":"ollama","model":os.getenv("OLLAMA_MODEL","qwen2.5:3b"),"storage":"sqlite"}

@app.post("/api/analyze")
async def analyze_route(document: Document):
    analysis, audit = await summarize(blocks_data(document.blocks))
    return {"analysis":analysis,"audit":audit}

@app.post("/api/analyze/v1")
async def v1_route(document: Document):
    analysis, audit = await hierarchical_analyze(blocks_data(document.blocks))
    return {"analysis":analysis,"audit":audit}

@app.post("/api/analyze/hierarchical")
async def hierarchical_route(document: Document):
    analysis, audit = await summarize(blocks_data(document.blocks))
    return {"analysis":analysis,"audit":audit}

@app.post("/api/analyze/flat")
async def flat_route(document: Document):
    return {"analysis":await analyze(blocks_data(document.blocks))}

@app.post("/api/ask")
async def ask_route(question: Question):
    return {"answer":await answer(question.question,blocks_data(question.blocks))}

# These endpoints are for local research ONLY. No accounts, authentication or tenancy yet.
@app.post("/api/documents",status_code=201)
def create_document(document: SaveDocument):
    identifier = storage.save(document.name,blocks_data(document.blocks))
    return {"id":identifier}

@app.get("/api/documents")
def all_documents():
    return {"documents":storage.list_documents()}

@app.get("/api/documents/{identifier}")
def get_document(identifier: str):
    result = storage.fetch(identifier)
    if not result:
        raise HTTPException(status_code=404,detail="Not found")
    return result

@app.delete("/api/documents/{identifier}")
def delete_document(identifier: str):
    if not storage.delete(identifier):
        raise HTTPException(status_code=404,detail="Not found")
    return {"deleted":True}

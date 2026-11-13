"""ClearFinance research backend. Local only: no auth; never publicly expose."""
from __future__ import annotations
import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from .core import analyze, answer
from .summarization import hierarchical_analyze
from . import storage

app = FastAPI(title="ClearFinance Research API", version="0.2.0")
origins = [o.strip() for o in os.getenv("CLEARFINANCE_ORIGINS","http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=False,allow_methods=["GET","POST","DELETE"],allow_headers=["Content-Type"])

class Block(BaseModel):
    id: str = Field(pattern=r"^(p\d+-b\d+|demo-[a-z0-9]+)$")
    page: int = Field(ge=1, le=10000)
    text: str = Field(min_length=1,max_length=1200)
    @field_validator("text")
    @classmethod
    def no_whitespace_only(cls,value: str) -> str:
        if not value.strip():
            raise ValueError("Empty block")
        return value

class Document(BaseModel):
    blocks: list[Block] = Field(min_length=1,max_length=600)

class Question(Document):
    question: str = Field(min_length=3,max_length=800)

class SaveDocument(Document):
    name: str = Field(min_length=1,max_length=200)

def blocks_data(items: list[Block]) -> list[dict]:
    ids = [b.id for b in items]
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=422,detail="Duplicated block IDs")
    return [b.model_dump() for b in items]

@app.get("/api/health")
def health():
    return {"ok":True,"provider":"ollama","model":os.getenv("OLLAMA_MODEL","qwen2.5:3b"),"storage":"sqlite"}

@app.post("/api/analyze")
async def analyze_route(document: Document):
    analysis, audit = await hierarchical_analyze(blocks_data(document.blocks))
    return {"analysis":analysis,"audit":audit}

@app.post("/api/analyze/hierarchical")
async def hierarchical_route(document: Document):
    analysis, audit = await hierarchical_analyze(blocks_data(document.blocks))
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

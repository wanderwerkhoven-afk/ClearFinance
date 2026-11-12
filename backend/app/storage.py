"""Optional local SQLite document metadata and FTS5; no uploaded files stored."""
from __future__ import annotations
import json
import os
import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path(os.getenv("CLEARFINANCE_DB", "./data/clearfinance.sqlite3"))

def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, name TEXT NOT NULL, blocks_json TEXT NOT NULL)")
    connection.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(doc_id UNINDEXED, block_id UNINDEXED, content)")
    connection.commit()
    return connection

def save(name: str, blocks: list[dict]) -> str:
    identifier = str(uuid.uuid4())
    with connect() as db:
        db.execute("INSERT INTO documents VALUES(?,?,?)",(identifier,name,json.dumps(blocks,ensure_ascii=False)))
        db.executemany("INSERT INTO chunks_fts(doc_id,block_id,content) VALUES(?,?,?)",
                       [(identifier,b["id"],b["text"]) for b in blocks])
    return identifier

def fetch(identifier: str) -> dict | None:
    with connect() as db:
        row = db.execute("SELECT name,blocks_json FROM documents WHERE id=?",(identifier,)).fetchone()
        return {"id":identifier,"name":row[0],"blocks":json.loads(row[1])} if row else None

def list_documents() -> list[dict]:
    with connect() as db:
        rows = db.execute("SELECT id,name FROM documents ORDER BY rowid DESC").fetchall()
        return [{"id":x,"name":y} for x,y in rows]

def delete(identifier: str) -> bool:
    with connect() as db:
        db.execute("DELETE FROM chunks_fts WHERE doc_id=?",(identifier,))
        return db.execute("DELETE FROM documents WHERE id=?",(identifier,)).rowcount > 0

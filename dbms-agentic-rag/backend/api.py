"""
FastAPI REST API Gateway (backend/api.py)
-----------------------------------------
Pure HTTP/REST architecture (Zero TCP socket complexity).
Connects the Black & White UI to the High-End Agentic RAG core and SQLite DBMS.
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import db
from backend import rag_agent

load_dotenv()

UPLOAD_DIR = "./uploaded_notes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="NoteWise AI — Agentic RAG Platform",
    description="High-End Study Assistant (ChromaDB + Hybrid Search + SQLite)",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for separate CSS and JS files
static_dir = os.path.abspath("static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ChatRequest(BaseModel):
    question: str
    provider: Optional[str] = "auto"
    api_key: Optional[str] = None
    session_id: Optional[str] = "student_session_01"


@app.on_event("startup")
def on_startup():
    db.init_db()
    print("[NoteWise AI] Agentic RAG backend initialized successfully.")


@app.get("/", response_class=HTMLResponse)
def index_page():
    html_path = os.path.join("static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("<h2>NoteWise AI: static/index.html not found</h2>", status_code=404)


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "engine": "High-End Agentic RAG",
        "hybrid_search": "Enabled (Dense Vector + BM25 Lexical + RRF)",
        "database": "SQLite (notewise.db)",
        "vector_store": "ChromaDB Persistent"
    }


@app.get("/api/docs")
def list_documents():
    return {"status": "success", "documents": db.get_all_uploaded_files()}


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    save_path = os.path.join(UPLOAD_DIR, filename)

    try:
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        # Ingest through High-End RAG
        stats = rag_agent.ingest_document(save_path, filename)
        file_type = "PDF" if filename.lower().endswith(".pdf") else "TXT"

        # Log into SQLite
        db.log_uploaded_file(
            filename=filename,
            file_type=file_type,
            total_pages=stats.get("total_pages", 1),
            total_chunks=stats.get("total_chunks", 0)
        )

        return {"status": "success", "filename": filename, "stats": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/chat")
def chat(req: ChatRequest):
    query = req.question.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Hybrid Semantic + Lexical Retrieval with RRF Re-ranking
    chunks = rag_agent.hybrid_retrieve(query, top_k=5)

    # 2. Agentic Multi-Model Synthesis
    answer = rag_agent.generate_solution(
        query=query,
        chunks=chunks,
        provider=req.provider,
        custom_api_key=req.api_key
    )

    # 3. Log into SQLite Relational Database
    sources_str = ", ".join([f"{c['source']} (p.{c['page']})" for c in chunks])
    db.save_chat_message(
        session_id=req.session_id,
        user_query=query,
        ai_response=answer,
        sources_cited=sources_str,
        provider=req.provider
    )

    return {
        "status": "success",
        "answer": answer,
        "sources": chunks
    }


@app.post("/api/reset")
def reset_all():
    rag_agent.reset_collection()
    db.clear_all_records()
    return {"status": "success", "message": "Knowledge base reset."}

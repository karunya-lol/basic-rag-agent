#!/usr/bin/env python3
"""
NoteWise AI — High-End Agentic RAG Study Assistant
-------------------------------------------------
Main application entry point.
Run:
    python app.py
or
    python run.py
"""
import os
import sys
import uvicorn

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    print("=" * 60)
    print("🎓 NoteWise AI — Agentic RAG Study Assistant")
    print("=" * 60)
    print(f"🌐 Server URL : http://127.0.0.1:{PORT}")
    print("⚡ Vector DB  : ChromaDB (Local Persistent)")
    print("⚡ LLM Engine : Groq 120B / Google Gemini (Auto-routing)")
    print("🎨 Interface  : Minimalist Black & White Luxury UI")
    print("=" * 60)
    print("💡 Open your browser at: http://127.0.0.1:8000\n")

    uvicorn.run("backend.api:app", host=HOST, port=PORT, reload=False)

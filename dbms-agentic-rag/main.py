"""
NoteWise AI — Main Entrypoint (main.py)
---------------------------------------
Launches the High-End Agentic RAG Platform with the separate Black & White UI.

Usage:
  python main.py
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    print("=" * 60)
    print("   NoteWise AI — High-End Agentic RAG Platform")
    print(f"   Interface running at: http://localhost:{PORT}")
    print("=" * 60)
    uvicorn.run("backend.api:app", host=HOST, port=PORT, reload=False)

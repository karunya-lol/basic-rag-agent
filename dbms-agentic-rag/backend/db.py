"""
Relational DBMS Storage Module (backend/db.py)
----------------------------------------------
Manages SQLite database operations for NoteWise AI:
  1. Tracks uploaded lecture note metadata (filename, page counts, chunk counts)
  2. Persistently logs all conversational turns and cited sources for study review
"""

import sqlite3
import os
from typing import List, Dict, Any

DB_PATH = "notewise.db"


def get_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: Ingested Documents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            total_pages INTEGER DEFAULT 1,
            total_chunks INTEGER DEFAULT 0,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table 2: Conversational History & Audit Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            sources_cited TEXT,
            provider TEXT DEFAULT 'auto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Auto-migrate: ensure provider column exists if table existed from earlier versions
    try:
        cursor.execute("ALTER TABLE chat_history ADD COLUMN provider TEXT DEFAULT 'auto'")
        conn.commit()
    except Exception:
        pass
    conn.close()


def log_uploaded_file(filename: str, file_type: str, total_pages: int = 1, total_chunks: int = 0) -> int:
    """Logs an uploaded document record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO uploaded_files (filename, file_type, total_pages, total_chunks)
        VALUES (?, ?, ?, ?)
    """, (filename, file_type, total_pages, total_chunks))
    conn.commit()
    file_id = cursor.lastrowid
    conn.close()
    return file_id


def get_all_uploaded_files() -> List[Dict[str, Any]]:
    """Retrieves all indexed documents."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, file_type, total_pages, total_chunks, uploaded_at
        FROM uploaded_files
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_chat_message(session_id: str, user_query: str, ai_response: str, sources_cited: str = "", provider: str = "auto"):
    """Saves a user-assistant conversation turn with citations."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (session_id, user_query, ai_response, sources_cited, provider)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, user_query, ai_response, sources_cited, provider))
    conn.commit()
    conn.close()


def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Retrieves session chat logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_query, ai_response, sources_cited, provider, created_at
        FROM chat_history
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_all_records():
    """Resets all database records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM uploaded_files")
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")

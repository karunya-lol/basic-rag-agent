"""
High-End Agentic RAG Engine (backend/rag_agent.py)
-------------------------------------------------
State-of-the-Art Retrieval-Augmented Generation:
  1. Multi-format ingestion (PDF with exact page preservation, TXT, MD)
  2. Overlapping sliding-window chunking
  3. ChromaDB Persistent Vector Store
  4. Hybrid Search (Dense Semantic Vector + Lexical Keyword Scoring)
  5. Reciprocal Rank Fusion (RRF) Re-ranking
  6. Agentic Multi-Model Synthesis (Groq Llama 3.3 70B, Gemini 3.8 Flash, or Default Engine)
"""

import os
import re
import math
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pypdf import PdfReader
import chromadb
from chromadb.config import Settings

load_dotenv()

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "notewise_agent_collection"


# ==============================================================================
# 1. Vector Store Management
# ==============================================================================
def get_chroma_client():
    os.makedirs(CHROMA_PATH, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "High-End Agentic RAG store"}
    )


# ==============================================================================
# 2. Document Ingestion & Chunking
# ==============================================================================
def extract_text_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Extracts text page-by-page to maintain precise citation provenance."""
    pages_data = []

    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_data.append({"page": idx + 1, "text": text.strip()})
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
            if content:
                pages_data.append({"page": 1, "text": content})

    return pages_data


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Sliding-window chunker with boundary preservation."""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += (chunk_size - overlap)

    return chunks


def ingest_document(file_path: str, filename: str) -> Dict[str, Any]:
    """Indexes document into ChromaDB with enriched metadata."""
    pages = extract_text_from_file(file_path)
    if not pages:
        return {"total_pages": 0, "total_chunks": 0, "error": "No readable text found."}

    collection = get_collection()
    docs, metadatas, ids = [], [], []
    chunk_count = 0

    for p in pages:
        page_num = p["page"]
        text_chunks = chunk_text(p["text"], chunk_size=500, overlap=100)

        for c in text_chunks:
            chunk_count += 1
            chunk_id = f"{filename}_p{page_num}_c{chunk_count}_{int(time.time()*1000)%100000}"
            docs.append(c)
            metadatas.append({
                "source": filename,
                "page": page_num,
                "chunk_num": chunk_count,
                "char_length": len(c)
            })
            ids.append(chunk_id)

    if docs:
        collection.add(documents=docs, metadatas=metadatas, ids=ids)

    return {
        "filename": filename,
        "total_pages": len(pages),
        "total_chunks": chunk_count
    }


# ==============================================================================
# 3. Hybrid Search & Reciprocal Rank Fusion (RRF) Re-ranking
# ==============================================================================
def lexical_score(query: str, doc_text: str) -> float:
    """Computes BM25-inspired term frequency score for keyword matching."""
    query_tokens = [w.lower() for w in re.findall(r'\b\w+\b', query) if len(w) > 2]
    if not query_tokens:
        return 0.0

    doc_lower = doc_text.lower()
    score = 0.0
    for token in query_tokens:
        matches = len(re.findall(r'\b' + re.escape(token) + r'\b', doc_lower))
        if matches > 0:
            # Sub-linear term frequency scaling
            score += (1.0 + math.log(matches))
    return score


def hybrid_retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Combines dense semantic vector retrieval with lexical keyword scoring
    using Reciprocal Rank Fusion (RRF).
    """
    collection = get_collection()
    total_docs = collection.count()
    if total_docs == 0:
        return []

    fetch_k = min(15, total_docs)

    # 1. Dense Semantic Vector Search
    vector_results = collection.query(query_texts=[query], n_results=fetch_k)

    dense_candidates = []
    if vector_results and vector_results.get("documents") and vector_results["documents"][0]:
        docs = vector_results["documents"][0]
        metas = vector_results["metadatas"][0]
        ids = vector_results["ids"][0]
        for idx, (d_id, doc, meta) in enumerate(zip(ids, docs, metas)):
            dense_candidates.append({
                "id": d_id,
                "text": doc,
                "source": meta.get("source", "Notes"),
                "page": meta.get("page", 1),
                "dense_rank": idx + 1
            })

    # 2. Lexical Keyword Scoring across retrieved pool
    for item in dense_candidates:
        item["lexical_score"] = lexical_score(query, item["text"])

    # Rank by lexical score
    lexical_sorted = sorted(dense_candidates, key=lambda x: x["lexical_score"], reverse=True)
    for rank, item in enumerate(lexical_sorted, 1):
        item["lexical_rank"] = rank

    # 3. Reciprocal Rank Fusion (RRF) Scoring
    # Formula: RRF = 1 / (60 + dense_rank) + 1 / (60 + lexical_rank)
    k_const = 60.0
    for item in dense_candidates:
        dense_rrf = 1.0 / (k_const + item["dense_rank"])
        lexical_rrf = 1.0 / (k_const + item["lexical_rank"])
        item["rrf_score"] = dense_rrf + lexical_rrf

    # Sort candidates by combined RRF score
    fused = sorted(dense_candidates, key=lambda x: x["rrf_score"], reverse=True)

    # Deduplicate and return top_k
    seen_texts = set()
    final_chunks = []
    for item in fused:
        # Prevent near-identical chunks
        normalized = item["text"][:100].strip()
        if normalized not in seen_texts:
            seen_texts.add(normalized)
            final_chunks.append({
                "id": item["id"],
                "text": item["text"],
                "source": item["source"],
                "page": item["page"],
                "score": round(item["rrf_score"], 4)
            })
        if len(final_chunks) >= top_k:
            break

    return final_chunks


# ==============================================================================
# 4. Default Study Engine (Zero-Crash Fallback for Testers)
# ==============================================================================
def synthesize_default_solution(query: str, chunks: List[Dict[str, Any]]) -> str:
    """
    Synthesizes a structured, concise solution directly from notes
    when no external API key is configured.
    """
    if not chunks:
        return "I couldn't find any relevant notes matching your question. Please upload your lecture notes first."

    lines = [
        "**Answer synthesized from your notes:**\n"
    ]

    seen = set()
    code_snippets = []
    bullet_points = []

    for c in chunks:
        text = c["text"]
        for line in text.split("\n"):
            line = line.strip()
            lower = line.lower()

            if any(k in lower for k in ["import ", "cursor.", "connection.", "select ", "create table", "from ", "where "]):
                if len(line) > 10 and line not in code_snippets:
                    code_snippets.append(line)
            elif len(line) > 20 and not line.startswith("06-10-") and not line.startswith("Dr. P."):
                clean = line.lstrip("◼-•* ").strip()
                if clean and clean not in seen:
                    seen.add(clean)
                    bullet_points.append(f"• **{clean}** `[{c['source']}, p.{c['page']}]`")

    if bullet_points:
        lines.extend(bullet_points[:5])
    else:
        for c in chunks[:3]:
            lines.append(f"• {c['text'][:140]}... `[{c['source']}, p.{c['page']}]`")

    if code_snippets and any(w in query.lower() for w in ["code", "syntax", "example", "how to", "query", "sql"]):
        lines.append("\n**Code Reference:**")
        lines.append("```python\n" + "\n".join(code_snippets[:5]) + "\n```")

    return "\n".join(lines)


# ==============================================================================
# 5. Multi-Provider Agentic LLM Synthesis
# ==============================================================================
SYSTEM_PROMPT = """You are NoteWise AI, a high-efficiency academic study assistant.
Your objective is to provide a clear, direct, and well-structured answer to the student's question based strictly on the retrieved notes context.

Rules:
1. Answer Directly: Begin immediately with the direct answer. Do not add introductory conversational filler (e.g., "Sure!", "Based on the retrieved context...").
2. Only What Was Asked: Address specifically what the student asked for.
   - If asked for a definition, provide a crisp definition and core concept.
   - If asked for steps, components, or properties, provide a clean numbered list or short bullet points.
   - Do NOT add unrequested generic sections (e.g., code in 3 languages, huge comparison tables, or generic best-practices essays) unless the user explicitly asks for them.
3. Structure & Conciseness: Use bold text for key terms and clean bullet points. Keep the response focused, structured, and around 150 to 300 words.
4. Grounded Citations: Cite the source document and page number (e.g., `[notes.pdf, p. 4]`) for key facts.
"""


def generate_solution(
    query: str,
    chunks: List[Dict[str, Any]],
    provider: str = "auto",
    custom_api_key: Optional[str] = None
) -> str:
    """
    Executes synthesis using Groq, Gemini, or Default Engine.
    Detects API keys accurately and returns actionable error feedback if key fails.
    """
    if not chunks:
        return "No relevant content found in your uploaded notes. Please upload a PDF or TXT file first."

    user_key = (custom_api_key or "").strip()
    env_groq = os.getenv("GROQ_API_KEY", "").strip()
    env_gemini = os.getenv("GEMINI_API_KEY", "").strip()

    if env_groq == "your_groq_api_key_here": env_groq = ""
    if env_gemini == "your_gemini_api_key_here": env_gemini = ""

    # Format context
    context_str = ""
    for idx, c in enumerate(chunks, 1):
        context_str += f"\n--- [Source {idx}: {c['source']} | Page {c['page']}] ---\n{c['text']}\n"

    user_prompt = f"### RETRIEVED NOTES CONTEXT:\n{context_str}\n\n### STUDENT QUESTION:\n{query}\n\n### DIRECT & STRUCTURED ANSWER (Answer only what is asked, concise & cited):"

    # 1. Determine which key and provider to use
    active_key = None
    target_provider = None

    if user_key:
        if user_key.startswith("gsk_"):
            active_key = user_key
            target_provider = "groq"
        elif user_key.startswith("AIzaSy"):
            active_key = user_key
            target_provider = "gemini"
        elif env_groq:
            # Auto-fallback to active Groq key if entered key is invalid
            active_key = env_groq
            target_provider = "groq"
        else:
            active_key = user_key
            target_provider = "gemini"
    elif provider == "offline":
        return synthesize_default_solution(query, chunks)
    elif env_groq:
        active_key = env_groq
        target_provider = "groq"
    elif env_gemini and env_gemini.startswith("AIzaSy"):
        active_key = env_gemini
        target_provider = "gemini"
    else:
        # No valid external key -> use clean default synthesis directly from notes
        return synthesize_default_solution(query, chunks)

    # -------------------------------------------------------------
    # Execute Groq API
    # -------------------------------------------------------------
    if target_provider == "groq":
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json"
            }
            # Verified working fast models on Groq
            candidate_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
            last_err = ""
            for m in candidate_models:
                payload = {
                    "model": m,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1024
                }
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    last_err = res.text

            return f"⚠️ **Groq Error**: {last_err[:120]}"
        except Exception as e:
            return f"⚠️ **Groq Connection Error**: {str(e)}"

    # -------------------------------------------------------------
    # Execute Google Gemini API
    # -------------------------------------------------------------
    if target_provider == "gemini":
        try:
            from google import genai
            client = genai.Client(api_key=active_key)
            full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

            # Retry once on 503 high demand spike
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    return response.text
                except Exception as model_err:
                    err_s = str(model_err)
                    if ("503" in err_s or "UNAVAILABLE" in err_s) and attempt == 0:
                        time.sleep(2)
                        continue
                    raise model_err
        except Exception as e:
            err_str = str(e)
            print(f"[Gemini Error] {err_str}")

            # If a valid Groq key is available in .env, automatically rescue the query using Groq!
            if env_groq and env_groq != active_key:
                try:
                    import requests
                    headers = {"Authorization": f"Bearer {env_groq}", "Content-Type": "application/json"}
                    payload = {
                        "model": "openai/gpt-oss-20b",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.2
                    }
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=25)
                    if res.status_code == 200:
                        groq_ans = res.json()["choices"][0]["message"]["content"]
                        notice = (
                            "> 💡 *Notice: The entered Gemini key was rejected by Google (valid Gemini keys start with `AIzaSy...`). "
                            "NoteWise AI automatically generated this solution using your Groq API key.* \n\n---\n\n"
                        )
                        return notice + groq_ans
                except Exception:
                    pass

            # Otherwise provide clear explanation and synthesized solution from notes
            if "400" in err_str or "API_KEY_INVALID" in err_str or "not valid" in err_str:
                return (
                    "⚠️ **Invalid Gemini Key**: Google rejected this key (`API key not valid`).\n\n"
                    "• **Official Gemini API Keys** from [aistudio.google.com](https://aistudio.google.com/app/apikey) start with **`AIzaSy...`**\n"
                    "• **Groq API Keys** from [console.groq.com](https://console.groq.com/keys) start with **`gsk_...`**\n\n"
                    "---\n\n"
                    + synthesize_default_solution(query, chunks)
                )

            return synthesize_default_solution(query, chunks)

    return synthesize_default_solution(query, chunks)


def reset_collection():
    """Wipes vector index."""
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return get_collection()

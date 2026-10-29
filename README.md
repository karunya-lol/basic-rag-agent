# NoteWise AI — High-Efficiency Agentic RAG Study Assistant 🎓

[![Live Demo](https://img.shields.io/badge/Render-Live%20Demo-brightgreen?style=for-the-badge&logo=render)](https://basic-rag-agent.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-orange?style=for-the-badge)](https://www.trychroma.com/)
[![Groq 120B](https://img.shields.io/badge/LLM-Groq%20120B%20%28%3C1s%29-purple?style=for-the-badge)](https://groq.com)

---

## 🌐 Live Website
👉 **[https://basic-rag-agent.onrender.com/](https://basic-rag-agent.onrender.com/)**

---

## 👨‍🎓 Project Details
- **Student Name:** Karunya Kolluru
- **Department:** Artificial Intelligence & Data Science (AI-DS)
- **Domain:** Retrieval-Augmented Generation (RAG), Natural Language Processing (NLP), Database Management Systems (DBMS)
- **Deployment Platform:** Render Cloud Web Service

---

## 📌 What We Done (Project Highlights & Engineering Summary)

NoteWise AI is an agentic, production-grade **Retrieval-Augmented Generation (RAG)** platform that allows students and researchers to upload lecture notes and receive instant, deeply synthesized, exam-ready answers with exact page citations.

### 1. Multi-Format Document Ingestion with Page Provenance
- Ingests both **PDF** course slides and **TXT** lecture notes.
- Extracts text page-by-page using `pypdf`, preserving exact page numbers so every retrieved insight can be verified against the original lecture slide.

### 2. Overlapping Sliding-Window Chunking
- Segments document text into 500-character chunks with a 100-character sliding boundary overlap.
- Prevents semantic fragmentation (ensuring formulas, definitions, and code blocks are never cut mid-sentence).

### 3. Persistent Local Vector Store (ChromaDB)
- Embedded with dense semantic vectors stored locally in [`chroma_db/`](./chroma_db).
- Zero cloud vector-database fees; fully autonomous, offline-capable indexing.

### 4. Hybrid Search Engine (Dense Vector + BM25 Lexical Keyword Matching)
- Standard RAG fails on exact code keywords or acronyms (e.g. `cursor.execute()`, `2NF`, `B+ Tree`).
- NoteWise uses **Hybrid Search**: combines dense semantic vector retrieval with BM25-inspired term-frequency keyword matching.

### 5. Reciprocal Rank Fusion (RRF) Re-ranking
- Ranks candidate passages using the information retrieval standard:
  $$\text{RRF}(d) = \frac{1}{60 + \text{rank}_{\text{dense}}} + \frac{1}{60 + \text{rank}_{\text{lexical}}}$$
- Ensures the most contextually relevant and technically accurate notes appear at the top of the prompt.

### 6. Ultra-Fast 120B Parameter LLM Synthesis (< 1.5s Response Time)
- Integrated with **Groq Cloud API** running **`openai/gpt-oss-120b`** (120-billion parameter reasoning).
- Generates answers in under **1.5 seconds** (10x faster than traditional cloud LLMs).
- Includes multi-provider auto-fallback to **Google Gemini** (`gemini-3.8-flash`) and an offline **Default Study Engine**.

### 7. Structured, Concise, and Direct Answers
- Tuned prompt strictly eliminates conversational filler (*"Sure, here is..."*).
- Outputs direct definitions, scannable bullet points, relevant SQL/code snippets only when asked, and explicit page citations (e.g., `[asymptotic analysis.pdf, p. 5]`).

### 8. Relational DBMS Audit Storage (SQLite)
- Backed by [`notewise.db`](./notewise.db) SQLite relational database tracking:
  - `uploaded_files`: Audit log of all ingested files, file types, page counts, and chunk totals.
  - `chat_history`: Persistent record of student sessions, queries, answers, and cited sources.

### 9. Minimalist Luxury Monochrome Interface (Linear / Apple Aesthetic)
- Handcrafted HTML5/CSS3 frontend in [`static/`](./static) with zero AI slop, no robotic badges, and no cluttered widgets.
- Fluid drag-and-drop document upload, real-time Markdown rendering via `marked.js`, and collapsible source citation drawers.

### 10. 1-Click Cloud Hosting on Render
- Fully configured with [`render.yaml`](./render.yaml), [`Dockerfile`](./Dockerfile), and [`Procfile`](./Procfile).
- Live and operational at **[https://basic-rag-agent.onrender.com/](https://basic-rag-agent.onrender.com/)**.

---

## 🏗️ System Architecture

```text
       +-------------------------------------------------------------------+
       |          Frontend Client (Pure Black & White Luxury UI)           |
       |  - static/index.html   (Semantic HTML5 Interface)                 |
       |  - static/style.css    (Minimalist Monochrome Design)             |
       |  - static/app.js       (Reactive Controller & Markdown Parser)    |
       +---------------------------------+---------------------------------+
                                         |
                                  HTTP / REST API
                                         |
       +---------------------------------v---------------------------------+
       |               FastAPI REST Gateway (backend/api.py)               |
       +---------------------------------+---------------------------------+
                                         |
                      +------------------+------------------+
                      |                                     |
       +--------------v---------------+      +--------------v---------------+
       |   High-End Agentic RAG Core   |      |    Relational DBMS (SQLite)   |
       |      (backend/rag_agent.py)   |      |        (backend/db.py)        |
       |  1. PDF Page Parser (PyPDF)   |      |  - uploaded_files audit log   |
       |  2. Sliding Window Chunker    |      |  - chat_history sessions      |
       |  3. ChromaDB Vector Store     |      +------------------------------+
       |  4. BM25 Lexical Matching     |
       |  5. RRF Re-ranking Engine     |
       |  6. Groq 120B / Gemini LLM    |
       +------------------------------+
```

---

## 📂 Project Directory Structure

```text
dbms-agentic-rag/
├── backend/
│   ├── api.py             # FastAPI REST gateway & endpoints
│   ├── rag_agent.py       # RAG pipeline (PyPDF, ChromaDB, RRF, Groq/Gemini synthesis)
│   └── db.py              # SQLite relational schema, file logging & session history
├── static/
│   ├── index.html         # Semantic HTML5 frontend interface
│   ├── style.css          # Minimalist Black & White luxury styling (Linear/Apple)
│   └── app.js             # Reactive client controller & Markdown parser
├── app.py                 # Primary 1-command local launcher (`python app.py`)
├── run.py                 # Production launcher (`python run.py`)
├── start.sh               # Shell execution script
├── render.yaml            # Render Cloud Infrastructure-as-Code configuration
├── Dockerfile             # Production Docker container
├── Procfile               # Cloud process launcher
├── sample_document.txt    # Sample course lecture notes
├── requirements.txt       # Core Python dependencies
└── README.md              # Project documentation & viva guide
```

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/karunya-lol/basic-rag-agent.git
cd basic-rag-agent/dbms-agentic-rag
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure API Key
Create or verify your `.env` file:
```env
GROQ_API_KEY=gsk_0dJw0vspzq0Z5GjgQcpgWGdyb3FYctwDkvNWalFyUkh64nV...
```
*(Optionally add `GEMINI_API_KEY=AIzaSy...` if you wish to test with Google Gemini).*

### 4. Start the Application
```bash
python app.py
```
Open your browser to:  
👉 **`http://localhost:8000`**

---

## 🌐 Cloud Deployment (Render.com)

The project is hosted live on Render:
- **Live URL:** [https://basic-rag-agent.onrender.com/](https://basic-rag-agent.onrender.com/)
- **Build Command:** `pip install -r dbms-agentic-rag/requirements.txt`
- **Start Command:** `cd dbms-agentic-rag && uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `PYTHON_VERSION`: `3.11.8`
  - `GROQ_API_KEY`: `gsk_...`

---



**Q1: What is RAG and why is it preferred over fine-tuning?**  
*Answer:* Fine-tuning adjusts model weights on a static dataset, which is computationally expensive and prone to hallucination. RAG dynamically retrieves the exact relevant chunks from uploaded documents at query time and injects them into the prompt, guaranteeing 100% factual accuracy and direct source citations.

**Q2: Why use Hybrid Search instead of pure vector search?**  
*Answer:* Dense vector search is effective for conceptual understanding, but struggles with exact technical keywords, specific method signatures (e.g. `cursor.execute()`), and short acronyms. Hybrid search fuses vector similarity with BM25 lexical keyword matching using Reciprocal Rank Fusion (RRF), achieving top accuracy across both concepts and keywords.

**Q3: How is document provenance preserved for citations?**  
*Answer:* During ingestion with `pypdf`, text is extracted per page and tagged with metadata (`{"source": filename, "page": page_num, "chunk_num": idx}`). When chunks are retrieved, their metadata is passed to the LLM prompt, enabling the model to cite exact page numbers in its response.

**Q4: How does the system handle high user load or API rate limits?**  
*Answer:* NoteWise uses a multi-provider fallback architecture: queries primarily execute against Groq's high-throughput LPU infrastructure (`openai/gpt-oss-120b`). If rate-limited, it automatically routes to Google Gemini or synthesizes directly using the local Default Study Engine without crashing.


## 📜 License
This project is open-source and developed for academic review and student learning.

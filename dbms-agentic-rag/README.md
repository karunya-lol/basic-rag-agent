# NoteWise AI — High-End Agentic RAG Study Assistant 🎓

**Student Name:** Karunya Kolluru  
**Department:** Artificial Intelligence & Data Science (AI-DS)  
**Domain:** Agentic Retrieval-Augmented Generation (RAG), Information Retrieval, Database Management Systems (DBMS)

---

## 📌 Project Overview
**NoteWise AI** is an advanced, production-grade **Agentic RAG** platform designed for college students and researchers. It allows users to upload course materials (PDF and TXT lecture notes), indexes them into a persistent vector store (**ChromaDB**), performs **Hybrid Dense + Lexical Keyword Search** with **Reciprocal Rank Fusion (RRF)**, and delivers comprehensive, structured academic solutions using state-of-the-art LLMs (**Groq Llama 3.3 70B** / **Google Gemini 3.8 Flash** / **Default Study Engine**) with exact document and page citations.

---

## 🚀 Key Architectural Innovations

1. **High-End Hybrid Search (Dense + Lexical)**:
   - Combines semantic vector similarity search from **ChromaDB** with BM25-inspired term-frequency lexical matching.
   - Ensures that conceptual questions and exact technical keywords (e.g. `cursor.execute()`, `3NF`, `B+ Trees`) are both retrieved with pinpoint accuracy.
2. **Reciprocal Rank Fusion (RRF) Re-ranking**:
   - Merges vector rankings and lexical rankings into a single optimal relevance score using the RRF formula:
     $$\text{RRF}(d) = \frac{1}{60 + \text{rank}_{\text{dense}}} + \frac{1}{60 + \text{rank}_{\text{lexical}}}$$
3. **Agentic Synthesis Engine**:
   - Generates structured, exam-ready answers:
     - 📌 **Executive Overview & Core Definition**
     - ⚙️ **Underlying Mechanism & Architecture**
     - 💻 **Syntax & Runnable Code Reference**
     - 🔒 **Best Practices & Security Rules (e.g. Preventing SQL Injection)**
     - 📄 **Source Citations with Page Provenance**
4. **Separate Pure Black & White (Monochrome) UI**:
   - Clean separation of concerns: Backend in `backend/`, and frontend in `static/` (`index.html`, `style.css`, `app.js`).
   - Luxury monochrome aesthetic inspired by **Linear.app** and **Vercel** (`#09090b` obsidian background, `#121214` surface cards, hairline borders).
5. **Tester & Evaluator Friendly (Bring Your Own Key or Default Answers)**:
   - Evaluators can paste their own free **Groq** or **Gemini** key right in the UI.
   - If left blank, it **never crashes**: it automatically activates the **Default Study Engine**, producing structured notes solutions and code snippets with exact citations!
6. **Pure Modern REST Architecture (No TCP Socket Baggage)**:
   - Built on **FastAPI** + **Uvicorn**, zero socket timeouts, 100% self-hostable.

---

## 🏗️ System Architecture

```text
       +-------------------------------------------------------------------+
       |       Frontend Client (Pure Black & White Luxury Web App)         |
       |  - static/index.html   (Semantic HTML5 Structure)                 |
       |  - static/style.css    (Pure Monochrome Design System)            |
       |  - static/app.js       (Reactive Client Controller)               |
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
       |  4. BM25 Lexical Keyword Match|
       |  5. RRF Re-ranking Engine     |
       |  6. Multi-Model Synthesis     |
       |     (Groq / Gemini / Default) |
       +------------------------------+
```

---

## 📂 Project Structure

```text
dbms-agentic-rag/
├── backend/
│   ├── api.py             # FastAPI REST gateway & endpoints (port 8000)
│   ├── rag_agent.py       # RAG Core (PyPDF parsing, ChromaDB, RRF re-ranking, Groq/Gemini)
│   └── db.py              # SQLite database (uploaded files log & chat history)
├── static/
│   ├── index.html         # Pure HTML5 interface (Ultra-clean Monochrome)
│   ├── style.css          # Minimalist Black & White luxury styling (Linear/Apple)
│   └── app.js             # Reactive client controller & Markdown parser
├── app.py                 # Primary 1-command launcher (`python app.py`)
├── run.py                 # Alternate launcher (`python run.py`)
├── start.sh               # Shell script launcher (`./start.sh`)
├── sample_document.txt    # Sample DBMS lecture notes
├── requirements.txt       # Dependencies (fastapi, uvicorn, chromadb, pypdf, requests)
├── Dockerfile             # Production container for cloud hosting
├── Procfile               # Cloud deployment config (Render / Railway)
└── README.md              # Project documentation & viva guide
```

---

## 🚀 How to Run (1 Single Command)

```bash
python app.py
```
*(Or `python run.py` / `./start.sh`)*

Open your browser to:
👉 **`http://localhost:8000`**

### What to Expect:
1. **Upload Notes**: Drag and drop any lecture notes (`.pdf` or `.txt`).
2. **Ask Any Question**: Type your DBMS question (e.g. *"What is a Cursor?"* or *"Explain ACID properties"*).
3. **Instant 120B Answer**: NoteWise automatically uses your pre-configured Groq API key (`openai/gpt-oss-120b`) to return an exam-ready, structured answer with exact page citations in under **2 seconds**.
4. **No API Key Required by Testers**: Evaluators can leave the API key box empty, and it works immediately without crashing!

---

## 🚀 Quick Setup & How to Run

### 1. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Your API Key (Optional)
Open `.env` and set your key (or leave blank to test with the Default Study Engine):
```env
# Option 1 (Recommended — 100% Free & Ultra-Fast): Groq Cloud
# Get free key in 10s at https://console.groq.com/keys
GROQ_API_KEY=gsk_...

# Option 2: Google Gemini
GEMINI_API_KEY=AIzaSy...
```

### 3. Launch with 1 Command:
```bash
python run.py
```
Open your browser at **`http://localhost:8000`**.

---

## 🌐 Self-Hosting Anywhere

### Deploying to Render (Free Cloud Service)
1. Push this repository to GitHub.
2. Go to **[dashboard.render.com](https://dashboard.render.com)** -> **New > Web Service**.
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
4. Set Environment Variable: `PORT = 8000`.
5. Deploy! Render gives you a public URL (e.g. `https://notewise-ai.onrender.com`).

### Deploying with Docker
```bash
docker build -t notewise-ai .
docker run -d -p 8000:8000 notewise-ai
```
Access at `http://YOUR_SERVER_IP:8000`.

---

## 👥 Evaluator & Review Mode
- **No Key Barrier**: Anyone can test immediately using the **Default Study Engine** without entering any key.
- **Bring Your Own Key**: Testers can paste their free Groq or Gemini key in the sidebar for live AI reasoning.
- **⚡ 1-Click Quick Prompts**: Click any sample button on the screen (*"What is a Cursor?"*, *"Explain Normalization"*, *"How do B+ Trees work?"*, *"ACID Properties"*) to test immediately.

# PDF AI Assistant

A web-based PDF knowledge application featuring **TWO COMPLETELY INDEPENDENT INTELLIGENCE SYSTEMS**:

1. **System 1: AI PDF Chatbot** (Retrieval-Augmented Generation / RAG pipeline powered by SQLite, ChromaDB, Sentence Transformers, and local Ollama LLM).
2. **System 2: Semantic Search Engine** (Independent PDF extraction, text chunking, embedding index, vector retrieval, and result ranking engine).

Both systems share the same uploaded PDF documents and receive queries from a single frontend search bar, but their processing, storage, vector databases, retrieval, and ranking algorithms remain 100% separate.

---

## 🏗 System Architecture

```
                                  USER
                                    |
                                    v
                                FRONTEND
                                    |
                          +---------+---------+
                          |                   |
                          v                   v
                     PDF UPLOAD          USER QUERY
                          |                   |
                          v                   v
                       API LAYER          API LAYER
                          |                   |
                 +--------+--------+          |
                 |                 |          |
                 v                 v          |
              CHATBOT       SEMANTIC SEARCH   |
              PIPELINE          PIPELINE      |
                 |                 |          |
                 v                 v          |
            CHATBOT DB       SEMANTIC DB      |
                 |                 |          |
                 v                 v          |
          CHATBOT VECTOR    SEARCH VECTOR     |
               DB                DB           |
                 |                 |          |
                 v                 v          |
             RETRIEVAL         SEARCH         |
                 |             + RANKING       |
                 v                 |          |
          CONTEXT BUILDER          |          |
                 |                 |          |
                 v                 |          |
              OLLAMA               |          |
                 |                 |          |
                 v                 |          |
            AI ANSWER              |          |
                 |                 |          |
                 +--------+--------+          |
                          |                   |
                          v                   |
                       API RESPONSE <---------+
                          |
                          v
                       FRONTEND
                          |
                 +--------+---------+
                 |                  |
                 v                  v
             AI ANSWER       SEMANTIC RESULTS
```

### Database Isolation Rule
- **Chatbot Subsystem**:
  - Metadata SQLite DB: `data/chatbot/chatbot.db`
  - Vector Database: `data/chatbot/vector_db/`
- **Semantic Search Subsystem**:
  - Metadata SQLite DB: `data/semantic_search/semantic_search.db`
  - Vector Database: `data/semantic_search/vector_db/`

These databases are strictly segregated. Neither subsystem accesses or modifies the other's storage.

---

## 📁 Folder Structure

```
project/
│
├── app/
│   ├── chatbot/
│   │   ├── processing/ (pdf_extractor.py, document_processor.py)
│   │   ├── embeddings/ (embedding.py)
│   │   ├── database/ (models.py, database.py, vector_store.py)
│   │   ├── retrieval/ (retrieval.py, context_builder.py)
│   │   └── llm/ (ollama_client.py, answer_generator.py)
│   ├── semantic_search/
│   │   ├── processing/ (pdf_extractor.py, document_processor.py)
│   │   ├── embeddings/ (embedding.py)
│   │   ├── database/ (models.py, database.py, vector_store.py)
│   │   └── search/ (semantic_search.py, ranking.py)
│   └── api/
│       ├── upload.py
│       ├── query.py
│       └── documents.py
│
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
│
├── data/
│   ├── chatbot/ (chatbot.db, vector_db/)
│   └── semantic_search/ (semantic_search.db, vector_db/)
│
├── uploads/
├── tests/
├── config.py
├── main.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

---

## 🚀 Quick Start Guide

### 1. Extract ZIP & Open Terminal
Extract `PDF_AI_Assistant.zip` and open a terminal in the root directory:
```bash
cd pdf_ai_assistant
```

### 2. Create & Activate Virtual Environment
- **Windows**:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Setup Ollama (Optional for AI Chatbot Answer Generation)
1. Download & install [Ollama](https://ollama.ai).
2. Start the local server:
   ```bash
   ollama serve
   ```
3. Pull your preferred small LLM (e.g. `qwen2.5:0.5b` or `qwen3:0.6b`):
   ```bash
   ollama pull qwen2.5:0.5b
   ```

### 5. Environment Configuration
Copy `.env.example` to `.env` (optional):
```bash
cp .env.example .env
```
Default configuration:
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=qwen2.5:0.5b`
- `EMBEDDING_MODEL=all-MiniLM-L6-v2`
- `TOP_K=5`
- `CHUNK_SIZE=500`
- `CHUNK_OVERLAP=50`

### 6. Run Application
```bash
python main.py
```
Or with Uvicorn directly:
```bash
uvicorn main:app --reload
```

Open your browser at:
`http://127.0.0.1:8000`

---

## 📡 API Endpoints

- `GET /health`: System status check.
- `POST /api/upload`: Upload and index PDF in both systems.
- `POST /api/query`: Unified query endpoint returning AI Chatbot answer + sources first, followed by ranked semantic search results.
- `GET /api/documents`: List uploaded document metadata.
- `DELETE /api/documents/{document_id}`: Remove document across both systems.

---

## 🧪 Testing

Run pytest across all chatbot, semantic search, and API tests:
```bash
pytest tests -v
```

---

## 🛠 Troubleshooting

- **Ollama LLM Notice in Chatbot Response**:
  Ensure Ollama is running (`ollama serve`) and the configured model is pulled (`ollama pull qwen2.5:0.5b`). If Ollama is not installed, the application will still perform retrieval and display document sources.
- **PyMuPDF / ChromaDB Install Issues**:
  Ensure Python version is 3.9 - 3.12.

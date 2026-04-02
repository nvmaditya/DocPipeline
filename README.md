# VectorLearn — Document Intelligence Platform

A full-stack AI tutoring platform. Upload documents or browse community knowledge bases, then ask grounded, source-cited questions via an SSE-streaming chat interface.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + TailwindCSS (Framer Motion) |
| API Proxy | Express.js (forwards auth, docs, search, ask, community) |
| Backend | FastAPI + Python |
| Pipeline | `docpipe` — extraction, chunking, embedding, FAISS, SQLite |
| Embeddings | Ollama `bge-large` (local, OpenAI-compatible API) |
| Vector Store | FAISS (flat index, per-user + per-book) |
| Metadata | SQLite (per-user + per-book) |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com) installed and running

```bash
# Pull the embedding model
ollama pull bge-large
```

### 2. Backend setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Launch (Windows)

```bash
start-dev.cmd
```

This opens two terminals: FastAPI on `http://localhost:8000`, frontend on `http://localhost:3000`.

Or start manually:

```bash
# Terminal 1 — backend
uvicorn backend.app.main:app --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

---

## Community Knowledge Bases

Books placed in `Books/` are automatically indexed into isolated per-book vector databases.

### Build indexes

```bash
.venv\Scripts\python.exe build_book_databases.py
```

Options:

```
--force                   Rebuild all indexes from scratch
--books History.pdf       Index a specific book only
--books-dir Books         Source folder (default: Books)
--output-dir store/community_books   Output root (default)
--config config.yaml      Base config (default)
```

The script:
1. Checks Ollama is reachable
2. Creates `store/community_books/<slug>/faiss.index` + `metadata.db`
3. Removes stores for books that were deleted from `Books/`
4. Writes `store/community_books/manifest.json` which the backend serves instantly

### Reflection

Adding or removing a book from `Books/` and re-running `build_book_databases.py` is all that's needed — the Community tab reflects the manifest automatically on next API call.

---

## Configuration

`config.yaml` — embedding and chunking settings:

```yaml
embedding:
  backend: github          # "github" = OpenAI-compatible (Ollama, GitHub Models)
  model: bge-large         # Ollama model name
  batch_size: 64
  github_endpoint: http://localhost:11434/v1
  github_token_env: OLLAMA_API_KEY   # set to any non-empty string for Ollama

chunking:
  strategy: recursive
  chunk_size: 380          # characters — tuned for bge-large's 512-token limit
  chunk_overlap: 50
```

Environment variables (set in `.env`):

| Variable | Purpose |
|---|---|
| `OLLAMA_API_KEY` | Dummy token for Ollama (any value, e.g. `ollama`) |
| `BACKEND_DOCPIPE_CONFIG` | Override config path |
| `BACKEND_USER_STORE_ROOT` | Override per-user store root |
| `BACKEND_COMMUNITY_STORE_ROOT` | Override community store root |
| `BACKEND_BOOKS_ROOT` | Override Books folder path |

---

## API Reference

Base path: `/api/v1`

| Route | Method | Auth | Description |
|---|---|---|---|
| `/auth/register` | POST | — | Register new user |
| `/auth/login` | POST | — | Login, returns JWT |
| `/auth/me` | GET | ✓ | Current user info |
| `/docs/upload` | POST | ✓ | Upload + ingest a document |
| `/docs/list` | GET | ✓ | List user's documents |
| `/docs/{id}` | DELETE | ✓ | Delete a document |
| `/search/semantic` | POST | ✓ | Semantic search (`?database_id=` for community) |
| `/search/ask/stream` | GET | ✓ | SSE ask stream (`?database_id=` for community) |
| `/community/databases` | GET | ✓ | List indexed community books |

---

## Testing

```bash
# Backend — all tests
.venv\Scripts\python.exe -m pytest backend/tests -q

# Backend — with coverage
.venv\Scripts\python.exe -m pytest backend/tests --cov=backend.app --cov-fail-under=80 --cov-report=term

# Domain pipeline tests
.venv\Scripts\python.exe -m pytest tests/ -q

# Frontend build check
cd frontend && npm run build
```

---

## Project Structure

```
document-pipeline/
├── Books/                        # Drop books here to index them
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app factory
│   │   ├── config.py             # Settings (env-driven)
│   │   ├── dependencies.py       # FastAPI dependency injectors
│   │   ├── api/                  # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── community.py
│   │   │   ├── documents.py
│   │   │   └── search.py
│   │   ├── services/             # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── community_service.py
│   │   │   ├── document_service.py
│   │   │   ├── rag_service.py
│   │   │   └── search_service.py
│   │   └── adapters/
│   │       └── pipeline_adapter.py
│   └── tests/
├── docpipe/                      # Core pipeline (extraction/chunk/embed/store)
├── frontend/
│   └── artifacts/
│       ├── api-server/           # Express proxy (Node.js)
│       └── doc-workspace/        # React Vite frontend
├── store/
│   ├── community_books/          # Per-book FAISS+SQLite stores + manifest.json
│   └── backend_users/            # Per-user FAISS+SQLite stores
├── tasks/
│   ├── todo.md                   # Task tracking
│   └── lessons.md                # Lessons learned
├── build_book_databases.py       # Book indexing script
├── config.yaml                   # Pipeline configuration
├── main.py                       # Legacy CLI
├── start-dev.cmd                 # One-command dev launcher (Windows)
└── requirements.txt
```

---

## CLI (Legacy)

The `main.py` CLI is kept for direct pipeline testing:

```bash
python main.py ingest --file Books/History.pdf
python main.py query "causes of World War 1"
python main.py query "atomic structure" --rag
python main.py stats
```

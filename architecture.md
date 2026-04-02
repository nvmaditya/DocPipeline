# Architecture — VectorLearn Document Intelligence Platform

## 1. Current State (Completed)

All phases are implemented and live. The system has been deployed as a full-stack web application.

### Completed Capabilities

- Multi-format document extraction (PDF, DOCX, PPTX, XLSX, CSV, HTML, TXT, MD)
- Recursive and semantic text chunking
- Embedding via Ollama `bge-large` (local, OpenAI-compatible API)
- FAISS flat-index vector retrieval (per-user + per-book)
- SQLite metadata persistence
- Per-user document isolation
- Community knowledge base system (per-book vector databases)
- FastAPI REST backend with JWT auth
- Express.js API proxy layer
- React Vite frontend (Dashboard, Documents, Search, Ask, Community pages)
- SSE streaming ask endpoint
- Book auto-indexing via `build_book_databases.py`
- Manifest-based community listing (no re-bootstrap on API call)

---

## 2. System Architecture

```
┌────────────────────────────────────────────────────────┐
│                  React Frontend (Vite)                  │
│                                                         │
│  Dashboard  Documents  Search  Ask  Community           │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/JSON + SSE
                       ▼
┌────────────────────────────────────────────────────────┐
│             Express API Proxy  (:3001)                  │
│                                                         │
│  /auth  /documents  /search  /ask  /community           │
│  Forwards requests + Bearer token to FastAPI            │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP → localhost:8000
                       ▼
┌────────────────────────────────────────────────────────┐
│              FastAPI Backend  (:8000)                   │
│                                                         │
│  api/auth  api/community  api/documents  api/search     │
│                                                         │
│  Services: Auth · Document · Search · RAG · Community   │
│  Adapter:  PipelineAdapter (wraps docpipe)              │
└──────────┬────────────────────────────┬─────────────────┘
           │                            │
           ▼                            ▼
  ┌─────────────────┐       ┌──────────────────────────┐
  │  Per-User Store │       │   Community Store         │
  │  FAISS + SQLite │       │   store/community_books/  │
  │  (one per user) │       │   <slug>/faiss.index      │
  └────────┬────────┘       │   <slug>/metadata.db      │
           │                │   manifest.json           │
           ▼                └──────────────────────────┘
  ┌───────────────────────────────┐
  │         docpipe               │
  │                               │
  │  Extractor → Cleaner →        │
  │  Chunker → Embedder → Store   │
  └───────────────────────────────┘
           │ embed calls
           ▼
  ┌───────────────────────────────┐
  │   Ollama  (:11434)            │
  │   model: bge-large            │
  │   OpenAI-compatible API       │
  └───────────────────────────────┘
```

---

## 3. Module Boundaries

### 3.1 Auth Module
- `backend/app/api/auth.py`
- `backend/app/services/auth_service.py`
- JWT-based, no external provider, in-memory token store

### 3.2 Document Module
- `backend/app/api/documents.py`
- `backend/app/services/document_service.py`
- Upload → ingest via `PipelineAdapter` → user-scoped FAISS+SQLite

### 3.3 Search + RAG Module
- `backend/app/api/search.py`
- `backend/app/services/search_service.py`
- `backend/app/services/rag_service.py`
- Semantic search with optional `database_id` scoping
- SSE ask stream: retrieve → build prompt → stream answer

### 3.4 Community Module
- `backend/app/api/community.py`
- `backend/app/services/community_service.py`
- `build_book_databases.py` (offline indexing script)
- `list_databases()` reads `manifest.json` for O(1) listing — no re-indexing at runtime
- `_read_manifest()` validates FAISS index exists before returning entries (stale entries filtered)

### 3.5 Pipeline Adapter
- `backend/app/adapters/pipeline_adapter.py`
- Bridges FastAPI services to `docpipe`
- Routes searches to user store or community store by `database_id`

### 3.6 Domain Pipeline (`docpipe`)
- `docpipe/extractors/` — PDF, DOCX, PPTX, XLSX, CSV, HTML, TXT/MD
- `docpipe/chunkers/` — recursive (default), semantic
- `docpipe/embedder.py` — local (SentenceTransformer) or OpenAI-compatible (Ollama/GitHub)
- `docpipe/store/` — FaissStore, SQLiteStore

---

## 4. Data Flow

### Upload flow
```
User uploads PDF
  → Express proxy → POST /api/v1/docs/upload
  → DocumentService.ingest()
  → PipelineAdapter → docpipe.ingest()
  → Extract text → Clean → Chunk → Embed (Ollama) → FAISS + SQLite
```

### Ask/Search flow (personal documents)
```
User asks question
  → Express /ask → FastAPI /api/v1/search/semantic  (no database_id)
  → PipelineAdapter.semantic_search(user_id, query)
  → user-scoped FAISS search → SQLite metadata join
  → /api/v1/search/ask/stream SSE
```

### Ask/Search flow (community book)
```
User selects book on Community page → navigates to Ask
  → ChatContext carries communityDatabaseId
  → Express /ask posts with databaseId
  → FastAPI /api/v1/search/semantic?database_id=<slug>
  → PipelineAdapter.community_semantic_search(database_id, query)
  → community FAISS search → community SQLite join → SSE answer
```

---

## 5. Embedding Configuration

| Aspect | Value |
|---|---|
| Backend | `github` (Ollama OpenAI-compatible shim) |
| Model | `bge-large` |
| Endpoint | `http://localhost:11434/v1` |
| Token env | `OLLAMA_API_KEY` (any non-empty value) |
| chunk_size | 380 chars (~95 tokens — safe below bge-large's 512-token limit) |
| chunk_overlap | 50 chars |
| FAISS index | Flat (FlatIP) — exact cosine, sufficient for per-book/per-user scale |

---

## 6. Repository Layout

```
document-pipeline/
├── Books/                         # Source books — drop PDFs here
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── community.py
│   │   │   ├── documents.py
│   │   │   └── search.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── community_service.py
│   │   │   ├── document_service.py
│   │   │   ├── rag_service.py
│   │   │   └── search_service.py
│   │   └── adapters/
│   │       └── pipeline_adapter.py
│   └── tests/
├── docpipe/
│   ├── extractors/
│   ├── chunkers/
│   ├── store/
│   ├── embedder.py
│   ├── cleaner.py
│   └── pipeline.py
├── frontend/
│   └── artifacts/
│       ├── api-server/            # Express proxy
│       │   └── src/routes/
│       │       ├── ask.ts
│       │       ├── auth.ts
│       │       ├── community.ts
│       │       ├── documents.ts
│       │       └── search.ts
│       └── doc-workspace/         # React Vite frontend
│           └── src/
│               ├── pages/         # Ask, Community, Dashboard, Documents, Search
│               ├── components/
│               ├── context/       # ChatContext, AuthContext
│               └── hooks/
├── store/
│   ├── community_books/           # Per-book indexes + manifest.json
│   └── backend_users/             # Per-user indexes
├── tasks/
│   ├── todo.md
│   └── lessons.md
├── build_book_databases.py        # Book index builder
├── config.yaml                    # Pipeline config
├── main.py                        # Legacy CLI
├── start-dev.cmd                  # Windows dev launcher
└── requirements.txt
```

---

## 7. Non-Goals (MVP)

- Multi-instance distributed vector storage
- Cross-region serving
- Enterprise SSO
- Multi-tenant admin controls

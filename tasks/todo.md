# VectorLearn — Task Board

## Status: All Core Phases Complete ✅

---

## Active Work

### Book Modules & Topic Extraction (Phase 12)

- [x] Create `docpipe/topic_extractor.py` (3-stage engine: PDF TOC → LLM → cosine similarity)
- [x] Add topics table + methods to `docpipe/store/sqlite_store.py`
- [x] Add `get_community_topics()` to `PipelineAdapter`
- [x] Add `GET /api/v1/community/databases/{id}/topics` endpoint
- [x] Add Express proxy route for topics
- [x] Update `Community.tsx` — "Ask Doubt" and "View Modules" buttons
- [x] Create `BookModules.tsx` page
- [x] Register `/book-modules/:databaseId` route in `App.tsx`

### Full-Stack Integration & Feature Testing (Phase 11)

- [x] Add `pytest-playwright` and `requests-mock` to `requirements.txt`
- [x] Update `backend/tests/conftest.py` config for `ollama` and `phi3`
- [x] Create `backend/tests/test_e2e_journeys.py` for comprehensive API flow testing
- [x] Create `web_extractor/tests/test_pipeline_integration.py`
- [x] Create frontend E2E tests in `tests/e2e/test_ui_flows.py`
- [x] Run all tests to verify integration across modules

### Persistent Authentication & Community Fixes (Phase 9)

- [x] Transition `AuthService` from in-memory to SQLite database (`store/backend_users/auth.db`)
- [x] Persist users and tokens to solve `401 Unauthorized` token wipes across restarts
- [x] Fix community vector databases failing to load (cascade from 401 bug or another issue)
- [x] Run backend tests and verify integration fixes

### Web Extractor UI Context (Phase 10)

- [x] Add `create_module(topic)` handler to `CommunityService` orchestrating the pipeline
- [x] Add `POST /api/v1/community/modules` to FastAPI router
- [x] Add Express proxy `POST /community/modules` route
- [x] Create UI view `CreateModule.tsx` for entering a topic 
- [x] Add "Create Module" action card to `Dashboard.tsx`
- [x] Add "Create Module" navigation link to `Sidebar.tsx`
- [x] Register `/create-module` route in `App.tsx`

### Community Vector DB Integration (Completed Mar 28, 2026)

- [x] Wire community router in `backend/app/main.py`
- [x] Optimize `list_databases()` to use manifest.json cache (no re-bootstrap on API calls)
- [x] Filter stale manifest entries when FAISS index is missing (books removed from Books/)
- [x] Rewrite `Community.tsx` — remove all 13 hardcoded mock subjects, fetch from real API
- [x] Update `ChatContext.tsx` to carry `communityDatabaseId`
- [x] Update `Ask.tsx` — pass `database_id` to backend, remove hardcoded plugin contexts
- [x] Update Express `ask.ts` and `search.ts` — forward `databaseId` to FastAPI
- [x] Add community isolation to conftest.py
- [x] Add community integration tests in `test_community_integration.py`
- [x] Add `build_book_databases.py` — per-book build script using docpipe directly
- [x] Add stale store cleanup to build script (removes indexes for books deleted from Books/)
- [x] Switch embedding to Ollama `bge-large` (local, OpenAI-compatible)
- [x] Fix chunk_size to 380 chars for bge-large's 512-token context limit
- [x] Add Ollama preflight check to build script

---

## Maintenance Tasks

### On adding a new book

1. Drop PDF into `Books/`
2. Run: `.venv\Scripts\python.exe build_book_databases.py`
3. Book appears in Community tab on next API call

### On removing a book

1. Delete PDF from `Books/`
2. Run: `.venv\Scripts\python.exe build_book_databases.py`
3. Old store cleaned, manifest updated, book disappears from Community tab

### On changing embedding model

1. Update `config.yaml` → `embedding.model` and `embedding.github_endpoint`
2. Run: `.venv\Scripts\python.exe build_book_databases.py --force` (rebuilds all incompatible indexes)

---

## Completed Phases Summary

| Phase | Description | Status |
|---|---|---|
| 1 | Core domain pipeline (extract, chunk, embed, store) | ✅ Done |
| 2 | CLI ingestion and query | ✅ Done |
| 3 | HNSW + semantic chunking + retrieval tuning | ✅ Done |
| 4 | RAG answer generation (SSE streaming) | ✅ Done |
| 5 | FastAPI backend + JWT auth + user isolation | ✅ Done |
| 6 | React frontend (Dashboard, Documents, Search, Ask) | ✅ Done |
| 7 | Express proxy + SSE integration + Community section | ✅ Done |
| 8 | Community vector DBs + Ollama embeddings + cleanup | ✅ Done |

---

## Known Limitations

- `bge-large` max context: 512 tokens → chunk_size capped at 380 chars
- OCR for scanned PDFs is best-effort (`ocr_engine: none` by default)
- No persistent chat history (session-only)
- Single backend instance (no horizontal scaling)

---

## Lessons Learned

See `tasks/lessons.md`

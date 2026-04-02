# VectorLearn — Project Idea

## What It Is

A local-first, privacy-preserving AI tutoring platform. Students upload their own documents or browse community-indexed textbooks, then ask grounded questions in a chat interface. Every answer is sourced from the actual indexed content — no hallucinations, no cloud data leakage.

## What Has Been Built

All planned phases are complete:

**Core pipeline** (`docpipe/`):
- Multi-format extraction (PDF, DOCX, PPTX, XLSX, HTML, TXT)
- Text cleaning and recursive/semantic chunking
- Embedding via Ollama `bge-large` (local, no API keys needed)
- FAISS vector indexing + SQLite metadata store

**Backend** (`backend/`):
- FastAPI REST API with JWT auth
- Per-user document isolation (upload, search, delete)
- Community knowledge base system — one FAISS+SQLite per book
- SSE streaming ask endpoint with source attribution

**Frontend** (`frontend/`):
- React Vite app with Dashboard, Documents, Search, Ask, Community pages
- Express proxy layer (auth forwarding, database scoping)
- Community page fetches live book list from backend manifest
- Ask page scoped to selected community database when coming from Community

## Key Design Decisions

- **Local-first embeddings**: Ollama `bge-large` runs entirely on device. No cloud API required for indexing.
- **Per-book vector databases**: Each book in `Books/` gets its own FAISS+SQLite. Plug-and-play — add a PDF, run the build script, it appears in the Community tab.
- **Manifest cache**: `build_book_databases.py` writes `manifest.json` after indexing. The backend reads this file directly for instant listing — no re-processing on every API call.
- **Stale cleanup**: Removing a book from `Books/` and re-running the build script removes its store and updates the manifest automatically.
- **SSE streaming**: Ask responses stream token-by-token via Server-Sent Events for a real-time feel.

## Principles

- **Privacy-first**: All data stays on the user's machine.
- **Cost-aware**: Zero paid API dependencies for core functionality.
- **Modular**: Embedding backend, LLM, and store paths are all config-driven and swappable.
- **Grounded answers**: Every response is tied to retrieved source chunks.

## Success Criteria (Achieved)

- ✅ User can register, login, upload documents, run semantic search, and receive streamed grounded answers
- ✅ Community books are indexed once and served from manifest — no per-request re-processing
- ✅ Adding/removing books auto-reflects in the Community tab on next build
- ✅ Tests pass for backend API, community integration, and domain pipeline

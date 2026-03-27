# Document Pipeline

Full-stack document intelligence platform for local-first ingestion, semantic retrieval, and grounded Q&A.

The repository currently contains:

- Core domain pipeline in `docpipe/`
- FastAPI backend in `backend/`
- Next.js frontend in `frontend/`
- Legacy CLI entrypoint in `main.py`

## Install

### Backend dependencies

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

### Frontend dependencies

```bash
cd frontend
npm install
```

## Quick Start (Full Stack)

### One-command launcher (Windows)

```bash
start-dev.cmd
```

This launches backend and frontend in two separate terminals.

### Backend server

```bash
cd backend
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URLs:

- API root: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`

### Frontend server

```bash
cd frontend
npm run dev
```

Frontend URL:

- App: `http://localhost:3000`

## Configure

Edit `config.yaml` for model and store paths.

Recommended environment variables:

- `HF_TOKEN` for Hugging Face rate-limit and auth behavior
- `BACKEND_DOCPIPE_CONFIG` for backend pipeline config path override
- `BACKEND_USER_STORE_ROOT` for backend per-user storage root override

Phase 3 retrieval options:

- `chunking.strategy`: `recursive` or `semantic`
- `chunking.semantic_threshold`: split sensitivity for semantic chunking
- `faiss.index_type`: `flat` or `hnsw`
- `embedding.model`: defaults to `BAAI/bge-large-en-v1.5`

## API Surface (Current)

Base path: `/api/v1`

- Auth
    - `POST /api/v1/auth/register`
    - `POST /api/v1/auth/login`
    - `POST /api/v1/auth/logout`
    - `GET /api/v1/auth/me`
- Documents
    - `POST /api/v1/docs/upload`
    - `GET /api/v1/docs/list`
    - `GET /api/v1/docs/{doc_id}`
    - `DELETE /api/v1/docs/{doc_id}`
- Search
    - `POST /api/v1/search/semantic`
    - `GET /api/v1/search/ask/stream`

## Testing

### Backend integration and feature verification

```bash
python -m pytest backend/tests -q
python -m pytest backend/tests --cov=backend.app.api --cov-fail-under=80 --cov-report=term
python -m pytest backend/tests --cov=backend.app.services --cov-fail-under=80 --cov-report=term
python -m pytest backend/tests --cov=backend.app.adapters --cov-fail-under=80 --cov-report=term
```

### Frontend integration and feature verification

```bash
cd frontend
npm run test
npm run test:cov
npm run build
```

## CLI (Legacy)

```bash
python main.py ingest --file path/to/file.pdf
python main.py ingest --dir path/to/docs
python main.py query "quarterly revenue"
python main.py query "quarterly revenue" --rag
python main.py stats
```

## Python API (Legacy)

```python
from docpipe import Pipeline

pipe = Pipeline(config="config.yaml")
pipe.ingest("./docs")
results = pipe.search("key findings", top_k=5)
print(results)
pipe.close()
```

## Current Limits

- OCR for scanned PDFs is optional and best-effort (`ocr_engine` can be `none`, `surya`, or `tesseract`)
- RAG requires local Ollama runtime when `--rag` is used

## Retrieval Modes

- Flat index: exact cosine search, best for smaller corpora
- HNSW index: approximate nearest-neighbor search for larger corpora
- Recursive chunking: faster, deterministic split
- Semantic chunking: sentence-similarity-driven split for better topical coherence

## RAG Mode (Phase 4)

- Command: `python main.py query "your question" --rag`
- Backend: configured by `query.llm_backend` (current implementation: `ollama`)
- Model: configured by `query.llm_model` (default `llama3.2`)
- Output: grounded answer + source list from retrieved chunks

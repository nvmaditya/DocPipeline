# architecture.md — Document Intelligence Pipeline

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGEST PIPELINE                          │
│                                                                 │
│  [File Input] → [Type Detection] → [Extractor] → [Cleaner]     │
│       ↓                                                         │
│  [Chunker] → [Embedder] → [FAISS Index] + [SQLite Store]        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        QUERY PIPELINE                           │
│                                                                 │
│  [Query] → [Embedder] → [FAISS Search] → [Metadata Lookup]     │
│       ↓                                                         │
│  [Ranked Chunks] → [Optional: LLM via Ollama] → [Answer]       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Decisions

### 1. Document Extraction Layer

| Format | Primary Library | Fallback | Notes |
|--------|----------------|----------|-------|
| PDF (text-based) | `PyMuPDF` (fitz) | `pdfplumber` | fitz preserves reading order, exposes font metadata for heading detection |
| PDF (scanned/image) | `surya-ocr` | `pytesseract` + `pdf2image` | Surya is newer and more accurate, especially multilingual |
| DOCX | `python-docx` | — | Handles paragraphs, tables, headers, footers natively |
| PPTX | `python-pptx` | — | Extracts slide text, notes, and shape text in order |
| XLSX / CSV | `openpyxl` + `pandas` | — | Converts tabular data to readable text representations |
| HTML | `beautifulsoup4` + `html2text` | — | Strips tags, preserves structure as readable text |
| TXT / MD | stdlib `open()` | — | Direct read, normalize line endings |
| File type detection | `python-magic` | `mimetypes` (stdlib) | Detect MIME type before routing, never trust extension alone |

**PDF detection logic:**

```python
# Detect if PDF page has extractable text or needs OCR
def is_page_scanned(page) -> bool:
    text = page.get_text("text")
    return len(text.strip()) < 50  # heuristic: fewer than 50 chars = likely scanned
```

Scanned pages are rasterized and passed to Surya. Text pages go directly through fitz. Mixed PDFs handle both per-page.

---

### 2. Text Cleaning Layer

After extraction, raw text passes through a cleaning pipeline:

```
raw_text
  → normalize unicode (unicodedata.normalize NFKC)
  → remove control characters
  → collapse excessive whitespace / blank lines
  → strip headers/footers (heuristic: repeated short lines near page boundaries)
  → normalize hyphenation (re-join split words across lines)
  → output: clean_text
```

Library: all stdlib + `ftfy` for fixing broken unicode/encoding issues.

---

### 3. Chunking Layer

**Default strategy: Recursive Character Splitting**

```python
# Hierarchy of split boundaries, tried in order
separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]
chunk_size = 512       # tokens (approximate via character count * 0.75)
chunk_overlap = 64     # token overlap between consecutive chunks
```

**Optional strategy: Semantic Chunking** (flag: `--semantic-chunks`)

1. Split text into sentences using `nltk.sent_tokenize`
2. Embed each sentence
3. Compute cosine similarity between consecutive sentences
4. Split where similarity drops below threshold (default: 0.5)
5. Merge small resulting groups up to max chunk size

Each chunk carries metadata:
```python
{
  "doc_id": "uuid",
  "file_path": "/path/to/file.pdf",
  "file_name": "file.pdf",
  "file_type": "pdf",
  "chunk_index": 3,
  "page_number": 2,       # where applicable
  "char_start": 1024,
  "char_end": 1536,
  "chunk_text": "...",
  "heading_context": "Section 2.1"  # nearest heading above this chunk, if detectable
}
```

---

### 4. Embedding Layer

**Library:** `sentence-transformers`

**Default model:** `BAAI/bge-large-en-v1.5` (335MB, 1024-dim, English, MTEB top-10)

**Swap options (config.yaml):**
- `BAAI/bge-m3` — multilingual, 570MB, supports hybrid retrieval
- `sentence-transformers/all-MiniLM-L6-v2` — 80MB, fast, lower quality
- Any HuggingFace sentence-transformer compatible model

**Batching:**
```python
embeddings = model.encode(
    chunks,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True  # required for cosine similarity via dot product
)
```

Normalization enables using `IndexFlatIP` (inner product = cosine similarity) instead of L2 distance, which is more semantically meaningful.

---

### 5. FAISS Index Layer

**Development / small corpus (< 50k chunks):**
```python
index = faiss.IndexFlatIP(embedding_dim)  # exact search, cosine via normalized vectors
```

**Production / large corpus (> 50k chunks):**
```python
# HNSW: no training required, excellent recall, fast query
index = faiss.IndexHNSWFlat(embedding_dim, 32)  # 32 = M parameter (neighbors per node)
index.hnsw.efConstruction = 200  # build quality (higher = better index, slower build)
index.hnsw.efSearch = 64         # query quality (tune at runtime)
```

**Persistence:**
```python
faiss.write_index(index, "store/faiss.index")
index = faiss.read_index("store/faiss.index")
```

FAISS index position (integer) maps to SQLite `chunk_id`. This is the critical join between vector store and metadata store.

---

### 6. Metadata Store (SQLite)

**Schema:**

```sql
CREATE TABLE documents (
    doc_id      TEXT PRIMARY KEY,
    file_path   TEXT NOT NULL,
    file_name   TEXT NOT NULL,
    file_type   TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    total_chunks INTEGER,
    metadata    TEXT  -- JSON blob for arbitrary extra fields
);

CREATE TABLE chunks (
    chunk_id       INTEGER PRIMARY KEY AUTOINCREMENT,  -- maps to FAISS index position
    doc_id         TEXT NOT NULL REFERENCES documents(doc_id),
    chunk_index    INTEGER NOT NULL,
    page_number    INTEGER,
    char_start     INTEGER,
    char_end       INTEGER,
    chunk_text     TEXT NOT NULL,
    heading_context TEXT,
    UNIQUE(doc_id, chunk_index)
);

CREATE INDEX idx_chunks_doc_id ON chunks(doc_id);
```

`chunk_id` (autoincrement integer starting at 0) must stay in sync with FAISS vector index position. Additions are append-only to preserve this mapping.

---

## Folder Structure

```
docpipe/
├── config.yaml                  # all tuneable parameters
├── main.py                      # CLI entrypoint
├── requirements.txt
├── README.md
│
├── docpipe/
│   ├── __init__.py
│   ├── pipeline.py              # orchestrates ingest + query
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseExtractor ABC
│   │   ├── pdf.py               # PyMuPDF + Surya OCR
│   │   ├── docx.py              # python-docx
│   │   ├── pptx.py              # python-pptx
│   │   ├── xlsx.py              # openpyxl + pandas
│   │   ├── html.py              # bs4 + html2text
│   │   ├── text.py              # plain text / markdown
│   │   └── router.py            # MIME detection → extractor dispatch
│   │
│   ├── cleaner.py               # text normalization pipeline
│   │
│   ├── chunkers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── recursive.py         # default recursive char splitter
│   │   └── semantic.py          # sentence embedding-based splitter
│   │
│   ├── embedder.py              # sentence-transformers wrapper + batching
│   │
│   ├── store/
│   │   ├── __init__.py
│   │   ├── faiss_store.py       # FAISS index CRUD
│   │   └── sqlite_store.py      # SQLite metadata CRUD
│   │
│   └── query.py                 # semantic search + optional RAG
│
├── store/                       # runtime data (gitignored)
│   ├── faiss.index
│   └── metadata.db
│
└── tests/
    ├── test_extractors.py
    ├── test_chunkers.py
    ├── test_pipeline.py
    └── fixtures/                # sample docs for testing
        ├── sample.pdf
        ├── sample_scanned.pdf
        ├── sample.docx
        └── sample.pptx
```

---

## Configuration (config.yaml)

```yaml
extraction:
  ocr_engine: surya          # surya | tesseract
  ocr_language: en
  scanned_threshold: 50      # chars below this = treat page as scanned

chunking:
  strategy: recursive        # recursive | semantic
  chunk_size: 512
  chunk_overlap: 64
  semantic_threshold: 0.5    # only for semantic strategy

embedding:
  model: BAAI/bge-large-en-v1.5
  batch_size: 32
  device: cpu                # cpu | cuda | mps
  normalize: true

faiss:
  index_type: flat           # flat | hnsw
  hnsw_m: 32
  hnsw_ef_construction: 200
  hnsw_ef_search: 64

store:
  faiss_path: store/faiss.index
  sqlite_path: store/metadata.db

query:
  top_k: 5
  score_threshold: 0.0       # minimum cosine similarity to return
  use_llm: false
  llm_backend: ollama        # ollama | llamacpp
  llm_model: llama3.2
```

---

## CLI Interface

```bash
# Ingest a single file
python main.py ingest --file report.pdf

# Ingest a directory recursively
python main.py ingest --dir ./documents

# Query semantically
python main.py query "What are the key findings on climate risk?"

# Query with RAG (requires Ollama running locally)
python main.py query "Summarize the financial risks" --rag

# Show index stats
python main.py stats

# Remove a document from the index
python main.py remove --file report.pdf
```

---

## Python API

```python
from docpipe import Pipeline

pipe = Pipeline(config="config.yaml")

# Ingest
pipe.ingest("./documents/")

# Search
results = pipe.search("quarterly revenue growth", top_k=5)
for r in results:
    print(r.score, r.file_name, r.page_number)
    print(r.chunk_text)
    print()

# RAG (optional)
answer = pipe.ask("What was the revenue in Q3?")
print(answer.response)
print(answer.sources)
```

---

## Dependencies (requirements.txt)

```
# Document extraction
pymupdf>=1.24.0
pdfplumber>=0.11.0
python-docx>=1.1.0
python-pptx>=0.6.23
openpyxl>=3.1.0
pandas>=2.0.0
beautifulsoup4>=4.12.0
html2text>=2024.2.26
python-magic>=0.4.27

# OCR
surya-ocr>=0.4.0
pytesseract>=0.3.10        # fallback OCR
pdf2image>=1.17.0          # for pytesseract path

# Text processing
ftfy>=6.2.0
nltk>=3.9.0

# Embeddings
sentence-transformers>=3.0.0
torch>=2.0.0               # CPU build acceptable

# Vector store
faiss-cpu>=1.8.0           # use faiss-gpu if CUDA available

# Storage
# sqlite3 is stdlib, no install needed

# Config + CLI
pyyaml>=6.0.1
click>=8.1.0

# Optional RAG
ollama>=0.2.0              # Python client for local Ollama server
```

---

## Data Flow (Detailed)

```
File on disk
    │
    ▼
router.py: python-magic MIME detection
    │
    ▼
Extractor (pdf/docx/pptx/xlsx/html/text)
    │  ─ PDF: check each page for scanned, route to fitz or surya
    │  ─ DOCX: extract paragraphs + tables, preserve heading hierarchy
    │  ─ PPTX: extract per-slide, include slide number in metadata
    │
    ▼
cleaner.py: unicode normalize → strip junk → fix encoding
    │
    ▼
chunker: split into overlapping chunks with metadata attached
    │
    ▼
embedder.py: batch encode → L2-normalize vectors
    │
    ▼
    ├──► faiss_store.py: index.add(vectors)   [position = chunk_id]
    │
    └──► sqlite_store.py: INSERT INTO chunks (chunk_id, chunk_text, ...)
```

```
Query string
    │
    ▼
embedder.py: encode query → normalize
    │
    ▼
faiss_store.py: index.search(query_vec, top_k) → [(score, faiss_id), ...]
    │
    ▼
sqlite_store.py: SELECT * FROM chunks WHERE chunk_id IN (faiss_ids)
    │
    ▼
Return: ranked list of {score, chunk_text, file_name, page_number, heading_context}
    │
    ▼ (optional)
Ollama / llama.cpp: generate answer grounded in retrieved chunks
```

---

## Key Design Decisions Summary

| Decision | Choice | Reason |
|---|---|---|
| PDF extraction | PyMuPDF (fitz) | Best reading order preservation, fast, widely used in production |
| OCR | Surya | Modern, pip-installable, no system deps, multilingual |
| Chunking default | Recursive character split | Fast, good quality, handles all text types |
| Embedding model | BAAI/bge-large-en-v1.5 | Top MTEB English, sentence-transformers compatible |
| FAISS index (dev) | IndexFlatIP | Exact search, zero config, fine under 50k chunks |
| FAISS index (prod) | IndexHNSWFlat | No training, high recall, fast, industry standard |
| Metadata store | SQLite | Zero dependencies, file-based, SQL, maps cleanly to FAISS positions |
| File detection | python-magic | MIME over extension, handles renamed/ambiguous files |
| Config | YAML | Human-readable, easy to swap models/strategies without code changes |
| CLI | Click | Clean, composable, testable |

---

## What to Build First (Phase Order)

**Phase 1 — Working pipeline for text-based PDFs + DOCX**
- `router.py` + `pdf.py` (fitz only) + `docx.py`
- `cleaner.py`
- `recursive.py` chunker
- `embedder.py` with MiniLM (fast download for dev)
- `faiss_store.py` + `sqlite_store.py` (FlatIP index)
- `main.py` CLI: ingest + query

**Phase 2 — Full format support**
- Add `pptx.py`, `xlsx.py`, `html.py`, `text.py`
- Add scanned PDF detection + Surya OCR

**Phase 3 — Production quality**
- Swap to bge-large model
- Add HNSW index option
- Add semantic chunking
- Add heading detection for better chunk context

**Phase 4 — RAG layer (optional)**
- Ollama integration
- Structured prompt with retrieved chunks
- Source citation in output

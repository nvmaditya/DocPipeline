# idea.md — Document Intelligence Pipeline with FAISS

## What Are We Actually Building?

A **local-first, fully open-source document ingestion and semantic search pipeline** in Python.

You throw any document at it — PDF, DOCX, PPTX, XLSX, HTML, plain text — and it:
1. Extracts and cleans the text accurately
2. Chunks it intelligently
3. Embeds it using a local model
4. Stores vectors in FAISS
5. Lets you query semantically across your entire document corpus

No OpenAI. No paid APIs. No cloud dependencies. Everything runs on your machine.

---

## Chain of Thought Reasoning

### Problem 1 — Document Extraction is the Hardest Part

Most tutorials gloss over extraction and go straight to embeddings. That's wrong. Garbage in, garbage out.

**What can go wrong:**
- PDFs can be text-based, image-based (scanned), or mixed
- Tables in PDFs lose structure when naively extracted
- DOCX files have nested formatting, headers, footers, embedded images
- Some PDFs are protected or have complex column layouts

**How to solve it:**

For text-based PDFs, `PyMuPDF` (fitz) is the industry standard. It's fast, accurate, preserves reading order better than most, and handles complex layouts. It also exposes font metadata which helps identify headings.

For scanned/image PDFs, we need OCR. `Surya` is the modern choice — it outperforms Tesseract on multilingual content and doesn't require system-level dependencies beyond pip. Tesseract remains a fallback since it's proven and stable.

For DOCX, `python-docx` is the only serious option. It handles paragraphs, tables, headings, and lists natively.

For PPTX, `python-pptx` for slide text extraction.

For XLSX/CSV, `openpyxl` + `pandas` — convert tabular data into readable text chunks.

For HTML, `BeautifulSoup4` with `html2text` for clean markdown-like output.

**Detection strategy:** Don't rely on file extensions. Use `python-magic` to detect MIME type, then route to the right extractor. This handles renamed or ambiguous files.

---

### Problem 2 — Chunking Strategy Matters More Than Embeddings

Most people obsess over the embedding model but the chunking strategy has a bigger impact on retrieval quality.

**Options:**

- **Fixed-size chunking** — Split every N characters. Fast, dumb, breaks sentences. Only acceptable for prototyping.
- **Recursive character splitting** — Split on paragraph > sentence > word boundaries, respecting hierarchy. Much better. This is what LangChain's `RecursiveCharacterTextSplitter` does.
- **Semantic chunking** — Embed each sentence, compare cosine similarity to neighbors, split when similarity drops. Produces the most coherent chunks but is slower.

**Decision:** Use recursive splitting as the default (fast, good enough). Offer semantic chunking as an optional flag for quality-critical workloads.

**Chunk size:** 512 tokens with 64-token overlap is a safe baseline. Adjust per document type — presentations can go smaller (256), long-form research docs can go larger (1024).

---

### Problem 3 — Embedding Model Selection

Must be local, free, and high quality.

**Best open-source options in 2024-25:**
- `BAAI/bge-m3` — Best-in-class multilingual, supports dense + sparse + colbert retrieval (multi-vector). Heavy at ~570MB.
- `BAAI/bge-large-en-v1.5` — Best English-only, good speed/quality tradeoff.
- `sentence-transformers/all-MiniLM-L6-v2` — Smallest (80MB), fast, decent quality. Good for resource-constrained environments.

**Decision:** Default to `BAAI/bge-large-en-v1.5` with an easy config swap. Use `sentence-transformers` library as the interface since it handles tokenization, batching, and device management cleanly.

---

### Problem 4 — FAISS Index Selection

FAISS has multiple index types and the wrong one will hurt performance at scale.

| Index | Best For | Tradeoff |
|---|---|---|
| `IndexFlatL2` | < 10k docs, exact search | Slow at scale, no memory savings |
| `IndexIVFFlat` | 10k-1M docs | Needs training, approximate |
| `IndexIVFPQ` | > 1M docs | Most compressed, some accuracy loss |
| `IndexHNSWFlat` | Fast ANN, no training | High memory, excellent recall |

**Decision:** `IndexFlatL2` for development and small corpora. `IndexHNSWFlat` for production (best recall/speed tradeoff, no training required, no IVF nlist tuning). Expose this as a config option.

---

### Problem 5 — Metadata and Document Store

FAISS stores vectors. It doesn't store document text, file names, page numbers, or chunk positions. We need a parallel store for this.

**Options:**
- SQLite — zero dependencies, file-based, SQL queryable. Perfect.
- JSON files — too slow for large corpora, no indexing.
- PostgreSQL — overkill for a local project.

**Decision:** SQLite via `sqlite3` (stdlib). Store: `doc_id`, `file_path`, `chunk_index`, `page_number`, `chunk_text`, `metadata_json`. Map FAISS vector index position → SQLite row.

---

### Problem 6 — Query Interface

The pipeline needs at least two modes:
1. **Semantic search** — Top-K most relevant chunks across all documents
2. **RAG query** — Use a local LLM to answer questions grounded in retrieved chunks

For RAG, the local LLM layer should use `ollama` (if available) or `llama.cpp` via Python bindings. This is optional — the pipeline is valuable even without a generative layer.

---

## What This Is NOT

- Not a replacement for Elasticsearch (no keyword BM25 by default, though we could add it)
- Not a multi-user server (single-user local tool)
- Not a UI (CLI + Python API only, UI can be added later)
- Not dependent on any paid API at any point

---

## Why This Is Worth Building

1. **Privacy** — documents never leave your machine
2. **Cost** — $0 to run after setup
3. **Control** — swap any component independently
4. **Practicality** — the most common real-world RAG problem is multi-format document ingestion, and no single clean open-source project does this well end-to-end

---

## Next Step

See `architecture.md` for the full system design, folder structure, component decisions, and implementation plan.

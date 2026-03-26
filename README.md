# Document Pipeline

Local-first document ingestion and semantic search for PDF, DOCX, PPTX, XLSX/CSV, HTML, and text files.

## Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configure

Edit `config.yaml` for model and store paths.

To avoid Hugging Face unauthenticated warnings and rate limits, set `HF_TOKEN` in `.env`.

Phase 3 options:
- `chunking.strategy`: `recursive` or `semantic`
- `chunking.semantic_threshold`: split sensitivity for semantic chunking
- `faiss.index_type`: `flat` or `hnsw`
- `embedding.model`: defaults to `BAAI/bge-large-en-v1.5`

## CLI

```bash
python main.py ingest --file path/to/file.pdf
python main.py ingest --dir path/to/docs
python main.py query "quarterly revenue"
python main.py stats
```

## Python API

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
- RAG generation is not implemented yet

## Retrieval Modes

- Flat index: exact cosine search, best for smaller corpora
- HNSW index: approximate nearest-neighbor search for larger corpora
- Recursive chunking: faster, deterministic split
- Semantic chunking: sentence-similarity-driven split for better topical coherence

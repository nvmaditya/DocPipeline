# Document Pipeline (Phase 1)

Local-first document ingestion and semantic search for text-based PDFs and DOCX files.

## Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configure

Edit `config.yaml` for model and store paths.

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

## Phase 1 Limits

- Supports only text-based PDF and DOCX extraction
- OCR/scanned PDF support is deferred to Phase 2
- Uses FlatIP FAISS index in Phase 1

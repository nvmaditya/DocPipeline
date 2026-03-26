# Concise Build Checklist By File (Phase 1)

## Root

- [ ] `requirements.txt`: add Phase 1 dependencies only (`pymupdf`, `python-docx`, `sentence-transformers`, `faiss-cpu`, `pyyaml`, `click`, `ftfy`, `pytest`)
- [ ] `config.yaml`: define extraction, chunking, embedding, faiss, store, and query sections with sane Phase 1 defaults
- [ ] `main.py`: implement CLI commands `ingest --file`, `ingest --dir`, `query`, `stats`
- [ ] `README.md`: document install, config, CLI usage, API usage, and known Phase 1 limits

## Package

- [ ] `docpipe/__init__.py`: export `Pipeline`
- [ ] `docpipe/pipeline.py`: wire ingest and search orchestration end to end
- [ ] `docpipe/cleaner.py`: implement text normalization pipeline
- [ ] `docpipe/embedder.py`: model load, batch encode, normalized embeddings
- [ ] `docpipe/query.py`: query embedding, FAISS top-k search, metadata join

## Extractors

- [ ] `docpipe/extractors/__init__.py`: expose extractor classes
- [ ] `docpipe/extractors/base.py`: define extractor interface
- [ ] `docpipe/extractors/router.py`: MIME detection and extractor routing
- [ ] `docpipe/extractors/pdf.py`: text-based PDF extraction via PyMuPDF with per-page metadata
- [ ] `docpipe/extractors/docx.py`: paragraph and table extraction with heading context

## Chunkers

- [ ] `docpipe/chunkers/__init__.py`: expose chunker classes
- [ ] `docpipe/chunkers/base.py`: define chunker interface
- [ ] `docpipe/chunkers/recursive.py`: recursive splitting with overlap and metadata propagation

## Stores

- [ ] `docpipe/store/__init__.py`: expose store classes
- [ ] `docpipe/store/sqlite_store.py`: create schema and CRUD for documents/chunks
- [ ] `docpipe/store/faiss_store.py`: create `IndexFlatIP`, add/search vectors, persist/load index

## Tests

- [ ] `tests/test_extractors.py`: PDF and DOCX extraction behavior
- [ ] `tests/test_chunkers.py`: chunk boundaries, overlap, metadata propagation
- [ ] `tests/test_pipeline.py`: ingest then query integration
- [ ] `tests/fixtures/sample.pdf`: text-based fixture
- [ ] `tests/fixtures/sample.docx`: heading plus table fixture

# Phase 1 Implementation Task Board

## Scope Lock

Phase 1 includes only: text-based PDF extraction, DOCX extraction, cleaning, recursive chunking, embedding, FlatIP FAISS, SQLite metadata, CLI ingest/query/stats, and tests.

## Board

| ID    | Task                                                | Depends On   | Status | Acceptance Criteria                                                         |
| ----- | --------------------------------------------------- | ------------ | ------ | --------------------------------------------------------------------------- |
| P1-01 | Scaffold repo files and package layout              | None         | Done   | All required files/folders exist and import paths resolve.                  |
| P1-02 | Add Phase 1 dependencies and config defaults        | P1-01        | Done   | `requirements.txt` and `config.yaml` load with no missing keys.             |
| P1-03 | Implement extractor and chunker base interfaces     | P1-01        | Done   | Abstract interfaces are stable and covered by basic tests.                  |
| P1-04 | Implement extractor router (MIME plus fallback)     | P1-03        | Done   | Correct extractor selected for PDF and DOCX; unknown types fail cleanly.    |
| P1-05 | Implement PDF text extractor (PyMuPDF)              | P1-04        | Done   | Text and page metadata extracted on sample PDF.                             |
| P1-06 | Implement DOCX extractor (paragraphs plus tables)   | P1-04        | Done   | Heading, paragraph, and table text extracted with metadata.                 |
| P1-07 | Implement text cleaner pipeline                     | P1-05, P1-06 | Done   | Unicode and whitespace normalization pass fixture tests.                    |
| P1-08 | Implement recursive chunker with overlap            | P1-07        | Done   | Chunk boundaries and overlap are deterministic and tested.                  |
| P1-09 | Implement embedding wrapper with normalization      | P1-08        | Done   | Batch embeddings generated with expected dimensions and normalized vectors. |
| P1-10 | Implement SQLite store and schema                   | P1-02        | Done   | Documents/chunks CRUD works and constraints are enforced.                   |
| P1-11 | Implement FAISS FlatIP store persistence/search     | P1-09        | Done   | Vector add/search/load/save validated with test vectors.                    |
| P1-12 | Implement pipeline orchestration (ingest + search)  | P1-10, P1-11 | Done   | End-to-end ingest and search returns ranked chunk results with metadata.    |
| P1-13 | Implement CLI commands (`ingest`, `query`, `stats`) | P1-12        | Done   | Commands run successfully on fixtures and show usable output.               |
| P1-14 | Add unit and integration tests                      | P1-13        | Done   | Extractor/chunker/pipeline tests pass locally.                              |
| P1-15 | Finalize README and Phase 1 known limits            | P1-14        | Done   | Setup and usage docs complete; out-of-scope limits documented.              |

## Execution Order

1. P1-01 to P1-04
2. P1-05 to P1-08
3. P1-09 to P1-12
4. P1-13 to P1-15

## Definition Of Done

- [x] All Phase 1 board items marked done
- [x] Tests pass for extractor, chunker, and pipeline flows
- [x] No open critical risks from `tasks/risk-register.md`
- [x] `tasks/todo.md` review section completed with evidence

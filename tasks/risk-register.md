# Risk List With Mitigation Steps (Before Coding)

| ID  | Risk                                                              | Likelihood | Impact   | Mitigation Before Coding Starts                                                                                                                      |
| --- | ----------------------------------------------------------------- | ---------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | FAISS vector position and SQLite `chunk_id` drift out of sync     | High       | Critical | Define append-only ingestion rule, document mapping contract, and add a startup integrity check (`faiss.ntotal == chunks count`) in design spec.     |
| R2  | Windows dependency friction (`python-magic`, OCR stack)           | High       | High     | Pin cross-platform alternatives in plan: use `mimetypes` fallback and defer OCR to Phase 2; add Windows setup notes in README from day one.          |
| R3  | Model bootstrap failures (download/cache/device mismatch)         | Medium     | High     | Decide explicit bootstrap behavior now: fail fast on model init failure, expose `device` in config, and add a smoke command/test for embedding init. |
| R4  | PDF extraction quality issues on complex layouts                  | Medium     | High     | Scope Phase 1 explicitly to text-based PDFs; define accepted limitations and regression fixtures; postpone scanned/complex OCR flows to Phase 2.     |
| R5  | Chunking parameter mismatch hurts retrieval quality               | Medium     | Medium   | Lock initial defaults (`chunk_size=512`, `overlap=64`), document tuning rules, and include chunk-quality tests before implementation.                |
| R6  | Metadata loss across cleaning/chunking stages                     | Medium     | High     | Standardize chunk metadata schema first (required vs optional fields) and validate schema in unit tests from first commit.                           |
| R7  | CLI UX errors and path handling issues (spaces, recursive ingest) | Medium     | Medium   | Define CLI contract and examples upfront; use Click path types and add explicit tests for quoted/spaced Windows paths.                               |
| R8  | Over-scoping Phase 1 delays working slice                         | Medium     | High     | Freeze Phase 1 scope to PDF text + DOCX + recursive chunker + FlatIP; track all extras as out-of-scope backlog.                                      |
| R9  | Test data too weak to catch regressions                           | Medium     | Medium   | Curate minimum fixture set before coding and define expected outputs for extract/chunk/search tests.                                                 |
| R10 | Unclear acceptance criteria causes rework                         | Medium     | High     | Attach measurable acceptance criteria to each Phase 1 task and require verification evidence in `tasks/todo.md` review.                              |

## Pre-Coding Gate

Start coding only when these are true:

- [x] Phase 1 scope frozen
- [x] Metadata mapping contract approved
- [x] Config defaults agreed
- [x] Fixture plan documented
- [x] Acceptance criteria attached to all board tasks

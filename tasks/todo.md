# Phase 1 Planning Todo

## Plan (Checkable)

- [x] Confirm requirements from `guidelines.md`, `architecture.md`, and `idea.md`
- [x] Check in on plan before implementation
- [x] Create concise build checklist by file
- [x] Create pre-coding risk list with mitigations
- [x] Create Phase 1 implementation task board
- [x] Verify deliverables for completeness and consistency
- [x] Add final review section

## Plan Check-In

Plan accepted and execution started based on the explicit user request to strictly follow `guidelines.md` and complete all three planning deliverables.

## Progress Notes

- Initialized task tracking and execution order.
- Added build checklist in `tasks/build-checklist.md`.
- Added risk register in `tasks/risk-register.md`.
- Added Phase 1 board in `tasks/phase1-task-board.md`.

## Review

### Deliverables Completed

- Concise build checklist by file: `tasks/build-checklist.md`
- Risk list with mitigation steps before coding: `tasks/risk-register.md`
- Phase 1 implementation task board: `tasks/phase1-task-board.md`

### Verification Notes

- Scope alignment checked against Phase 1 definition in `architecture.md`.
- Risks focus on pre-coding controls and explicit gating criteria.
- Task board includes dependencies, acceptance criteria, and definition of done.
- Artifacts are implementation-ready and maintain minimal-impact planning boundaries.

---

# Phase 1 Implementation Todo

## Plan (Checkable)

- [x] Freeze Phase 1 scope and confirm pre-coding gate items
- [x] Scaffold package, config, and dependency files
- [x] Implement extractors, cleaner, and recursive chunker
- [x] Implement embedder, FAISS store, and SQLite store
- [x] Implement pipeline orchestration and CLI commands
- [x] Add unit and integration tests with fixtures
- [x] Execute verification commands and capture results
- [x] Update task board statuses and final review

## Plan Check-In

Implementation plan approved and started in strict sequence with verification steps.

## Progress Notes

- Implemented Phase 1 modules under `docpipe/` including extractors, cleaner, chunker, embedder, stores, query, and pipeline.
- Implemented CLI in `main.py` with `ingest`, `query`, and `stats` commands.
- Added configuration in `config.yaml` and dependency manifest in `requirements.txt`.
- Added tests in `tests/test_extractors.py`, `tests/test_chunkers.py`, and `tests/test_pipeline.py`.
- Installed dependencies and executed test suite via VS Code task.

## Review

### Verification Evidence

- Static diagnostics: no remaining editor errors.
- Automated tests: `4 passed, 1 warning in 25.08s` from `pytest -q`.
- Warning observed is external package-compatibility warning from `requests` dependency stack and does not block project tests.

### Scope Compliance

- Implemented only Phase 1 scope (PDF text + DOCX + recursive chunking + FlatIP + SQLite + CLI + tests).
- Deferred OCR/scanned PDF and RAG features to later phases as planned.

---

# Phase 2 + Testing + Commits Todo

## Plan (Checkable)

- [ ] Update lessons for new user correction/request
- [ ] Initialize git repository and create initial baseline commit
- [ ] Implement Phase 2 format support (PPTX, XLSX/CSV, HTML, TXT/MD)
- [ ] Implement scanned PDF OCR path with optional engines
- [ ] Add/extend feature and integration tests for Phase 2 paths
- [ ] Run full test verification and capture output evidence
- [ ] Create one commit per completed todo step
- [ ] Attempt GitHub remote setup/push and report outcome
- [ ] Update final review section with proof

## Plan Check-In

Plan for this user request is verified and execution started in strict sequence.

## Progress Notes

- Pending.

## Review

Pending.

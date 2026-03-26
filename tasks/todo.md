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

- [x] Update lessons for new user correction/request
- [x] Initialize git repository and create initial baseline commit
- [x] Implement Phase 2 format support (PPTX, XLSX/CSV, HTML, TXT/MD)
- [x] Implement scanned PDF OCR path with optional engines
- [x] Add/extend feature and integration tests for Phase 2 paths
- [x] Run full test verification and capture output evidence
- [x] Create one commit per completed todo step
- [x] Attempt GitHub remote setup/push and report outcome
- [x] Update final review section with proof

## Plan Check-In

Plan for this user request is verified and execution started in strict sequence.

## Progress Notes

- Updated `tasks/lessons.md` for this correction/request pattern.
- Initialized git and created baseline commit.
- Implemented Phase 2 extractors and OCR path.
- Added and updated integration/feature tests.
- Ran pytest for feature + integration coverage.
- Created multiple focused commits and pushed to GitHub remote.

## Review

### Verification Evidence

- Feature/integration test run completed with final result: `8 passed, 1 warning in 26.92s`.
- Warning is `RequestsDependencyWarning` and non-blocking for project tests.

### Commit Evidence (Per Todo Progress)

- `761c972` chore: initial baseline commit
- `f5dcb2e` chore: ignore generated artifacts
- `aace720` feat: add phase2 extractors and scanned-pdf OCR path
- `a5b3bd3` chore: update phase2 dependencies and configuration
- `32f89a0` test: add phase2 feature and integration coverage

### Remote Push Evidence

- Remote: `https://github.com/nvmaditya/DocPipeline.git`
- Branch: `main`
- Push status: successful (`main -> main`)

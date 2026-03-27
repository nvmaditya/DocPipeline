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

---

# Phase 3 Implementation + Testing + Commits Todo

## Plan (Checkable)

- [x] Implement Phase 3 features (semantic chunking, HNSW option, stronger model defaults, heading context improvements)
- [x] Add feature and integration tests for Phase 3 paths
- [x] Run verification tests and capture evidence
- [x] Create one commit per todo item and push to GitHub
- [x] Update review section with outcomes and proof

## Plan Check-In

Plan validated. Execution will proceed in ordered steps with verification before completion.

## Progress Notes

- Implemented semantic chunking and strategy selection in pipeline.
- Added HNSW index option and tuning parameters in FAISS store and config.
- Added PDF heading-context detection heuristic.
- Added feature and integration tests for semantic chunking, HNSW, and heading context.
- Ran Phase 3 test suite and captured pass result.
- Created todo-based commits and pushed to GitHub.

## Review

### Verification Evidence

- Command: `python -m pytest tests/test_extractors.py tests/test_chunkers.py tests/test_pipeline.py -q`
- Result: `10 passed, 1 warning in 26.65s`
- Warning: `RequestsDependencyWarning` from external dependency stack, non-blocking.

### Todo Commit Mapping

- Phase 3 implementation: `1da4e20` feat: implement phase3 semantic chunking and hnsw retrieval
- Testing todo: `18e9122` test: add phase3 feature and integration coverage
- Workflow/docs/push todo: included in follow-up commit with review updates

### Push Status

- Remote: `https://github.com/nvmaditya/DocPipeline.git`
- Branch: `main`
- Status: pushed successfully

---

# Phase 6 Frontend Scaffold + Integration Verification Todo

## Plan (Checkable)

- [x] Re-run backend integration and feature tests to lock live API contracts
- [ ] Scaffold Phase 6 frontend workspace (Next.js + TypeScript) against current backend contracts
- [ ] Implement frontend API client and baseline auth/docs/search/ask-stream pages
- [ ] Add frontend feature/integration tests and run verification commands
- [ ] Create one git commit per completed todo item and push to GitHub

## Plan Check-In

Plan verified. Implementation started with backend contract verification and coverage gate re-check.

## Progress Notes

- Re-ran backend integration/features suite and confirmed contract stability for auth, docs, semantic search, and SSE ask stream.
- Re-ran backend package coverage gates with `--cov-fail-under=80` for API/services/adapters and confirmed all pass.

## Review

### Verification Evidence

- `python -m pytest backend/tests -q` -> pass (integration/features suite)
- `python -m pytest backend/tests --cov=backend.app.api --cov-fail-under=80 --cov-report=term` -> pass (91.76%)
- `python -m pytest backend/tests --cov=backend.app.services --cov-fail-under=80 --cov-report=term` -> pass (93.27%)
- `python -m pytest backend/tests --cov=backend.app.adapters --cov-fail-under=80 --cov-report=term` -> pass (92.66%)

### Todo Commit Mapping

- Pending implementation.

### Push Status

- Pending implementation.

---

# Phase 6 Frontend Scaffold + Integration Verification Todo

## Plan (Checkable)

- [ ] Re-run backend integration and feature tests to lock live API contracts
- [ ] Scaffold Phase 6 frontend workspace (Next.js + TypeScript) against current backend contracts
- [ ] Implement frontend API client and baseline auth/docs/search/ask-stream pages
- [ ] Add frontend feature/integration tests and run verification commands
- [ ] Create one git commit per completed todo item and push to GitHub

## Plan Check-In

Plan verified. Implementation starts with backend contract verification, then Phase 6 frontend scaffold and tests.

## Progress Notes

- Started implementation cycle and locked commit scope to only new Phase 6 artifacts.

## Review

### Verification Evidence

- Pending implementation.

### Todo Commit Mapping

- Pending implementation.

### Push Status

- Pending implementation.

---

# Phase 4 Implementation + Testing + Commits Todo

## Plan (Checkable)

- [x] Implement Phase 4 RAG layer (local LLM answer generation with retrieved chunk grounding)
- [x] Run integration and feature tests for Phase 4 changes
- [x] Create one GitHub commit per todo and push

## Plan Check-In

Plan verified and approved. Implementation will proceed in sequence with verification before finalization.

## Progress Notes

- Implemented RAG prompt and source helpers plus pipeline `ask()` flow.
- Added CLI `--rag` mode and Phase 4 query config options.
- Added integration and feature tests for RAG helpers and `ask()` with mocked LLM client.
- Executed test suite and captured verification output.
- Created todo-mapped commits and pushed to GitHub.

## Review

### Verification Evidence

- Command: `python -m pytest tests/test_extractors.py tests/test_chunkers.py tests/test_pipeline.py -q`
- Result: `12 passed, 1 warning in 29.30s`
- Warning: `RequestsDependencyWarning` from dependency stack, non-blocking.

### Todo Commit Mapping

- Phase 4 implementation todo: `f6da72f` feat: implement phase4 rag answer generation with ollama backend
- Testing todo: `40c4b8c` test: add phase4 rag integration and helper coverage
- Push/workflow todo: included in follow-up commit with tracking updates

### Push Status

- Remote: `https://github.com/nvmaditya/DocPipeline.git`
- Branch: `main`
- Status: pushed successfully

---

# Website Pivot Documentation Sync Todo

## Plan (Checkable)

- [x] Replace `architecture.md` with website-first target architecture and module gates
- [x] Replace `idea.md` with web product direction and locked MVP assumptions
- [x] Add future phase sections to task artifacts (`todo`, checklist, risks, board, lessons)
- [x] Run cross-doc consistency pass for terminology and assumptions
- [x] Preserve historical Phase 1-4 records while adding future roadmap

## Plan Check-In

Execution started after planning handoff. Scope is documentation-only sync for the website pivot.

## Progress Notes

- Updated architecture narrative from CLI-first to FastAPI + Next.js website direction.
- Reframed idea document around productized study workflow delivery.
- Added future roadmap sections to all task support files.

## Review

### Verification Evidence

- Contradictory forward-looking statements about single-user CLI-only direction were removed from core vision docs.
- Locked assumptions are now explicit across docs: single instance backend, SSE-first ask flow, hybrid frontend persistence, and package coverage gates.
- Historical implementation evidence for Phase 1-4 is retained.

---

# Phase 5 Backend Foundation Todo

## Plan (Checkable)

- [x] Create `backend/app/main.py` FastAPI application entrypoint
- [x] Add API routers: `auth`, `documents`, `search`
- [x] Add services for auth, document orchestration, and semantic search
- [x] Add adapter layer to reuse existing `docpipe` pipeline modules
- [x] Add endpoint tests for `/api/v1/auth/*`, `/api/v1/docs/*`, `/api/v1/search/semantic`
- [x] Add SSE endpoint test for `/api/v1/search/ask/stream`
- [ ] Meet package-level test gate (>=80%) for backend packages

## Plan Check-In

Implementation started. Initial backend scaffold and smoke tests are in place.

## Progress Notes

- Created `backend/app/main.py`, dependency wiring, and API router modules.
- Added in-memory service layer for auth, document metadata, search, and ask stream.
- Added backend smoke tests in `backend/tests/test_api_smoke.py`.
- Installed backend API dependencies in project venv.
- Verified backend smoke tests and full suite pass after scaffold.
- Added `PipelineAdapter` and rewired document/search services to use live `docpipe` ingest and search.
- Extended SQLite store with document query and soft-delete support to keep deleted docs out of list/search responses.

## Review

### Verification Evidence

- Backend API tests: `python -m pytest backend/tests/test_api_smoke.py -q` -> `5 passed`.
- Full project tests: `python -m pytest -q` -> `17 passed`.
- Adapter integration status: live `docpipe` ingest/search path is active behind backend services.
- Remaining open item: package coverage gate report and enforcement (`>=80%` per package).

---

# W5-06 Coverage Rollout + Integration Testing Todo

## Plan (Checkable)

- [x] Add/expand backend integration and feature tests for auth, documents, search, and adapter behavior
- [x] Add pytest-cov configuration and generate baseline coverage report for backend packages
- [x] Enforce coverage gate (`>=80%`) per backend package and verify gating commands pass
- [x] Create one git commit per completed todo item and push to GitHub

## Plan Check-In

Plan created per `guidelines.md`. Implementation starts now with test expansion, then coverage baseline, then gate enforcement.

## Progress Notes

- Added `backend/tests/conftest.py` with shared runtime fixtures and dummy embedder.
- Added feature/integration test modules for auth, documents, and search flows.
- Verified backend integration test run passes.
- Added `pytest-cov` dependency in `requirements.txt` and coverage configuration in `pyproject.toml`.
- Generated baseline package coverage report in `tasks/w5-06-coverage-baseline.md`.
- Executed per-package gate commands with `--cov-fail-under=80` for API, services, and adapters.
- Created dedicated commits for each completed checklist item and pushed to GitHub `main`.

## Review

### Verification Evidence

- Command: `python -m pytest backend/tests -q`
- Result: `14 passed, 3 warnings`
- Baseline coverage commands rerun:
    - `python -m pytest backend/tests --cov=backend.app.api --cov-report=term-missing` -> `TOTAL 91.8%`
    - `python -m pytest backend/tests --cov=backend.app.services --cov-report=term-missing` -> `TOTAL 93.3%`
    - `python -m pytest backend/tests --cov=backend.app.adapters --cov-report=term-missing` -> `TOTAL 92.7%`
- Coverage gate enforcement commands:
    - `python -m pytest backend/tests --cov=backend.app.api --cov-fail-under=80 --cov-report=term` -> `Required test coverage of 80% reached (91.76%)`
    - `python -m pytest backend/tests --cov=backend.app.services --cov-fail-under=80 --cov-report=term` -> `Required test coverage of 80% reached (93.27%)`
    - `python -m pytest backend/tests --cov=backend.app.adapters --cov-fail-under=80 --cov-report=term` -> `Required test coverage of 80% reached (92.66%)`

### Todo Commit Mapping

- Integration/features tests todo: `ff15166` test: add backend integration and feature test suite
- Coverage baseline todo: `c4c6249` test: add w5-06 coverage config and baseline report
- Coverage gate todo: `2025091` test: enforce w5-06 per-package coverage gate
- Todo commit/push tracking todo: pending current commit

### Push Status

- Remote: `https://github.com/nvmaditya/DocPipeline.git`
- Branch: `main`
- Status: pushed successfully

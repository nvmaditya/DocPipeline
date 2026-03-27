# W5-06 Coverage Gate Enforcement

## Goal

Enforce package-level coverage threshold of >=80% for backend API, services, and adapters.

## Gate Commands

1. python -m pytest backend/tests --cov=backend.app.api --cov-fail-under=80 --cov-report=term
2. python -m pytest backend/tests --cov=backend.app.services --cov-fail-under=80 --cov-report=term
3. python -m pytest backend/tests --cov=backend.app.adapters --cov-fail-under=80 --cov-report=term

## Results

- backend.app.api: Required test coverage of 80% reached. Total coverage: 91.76%
- backend.app.services: Required test coverage of 80% reached. Total coverage: 93.27%
- backend.app.adapters: Required test coverage of 80% reached. Total coverage: 92.66%

## Enforcement Status

Coverage gate is active and passing for all required backend package groups.

## Notes

- Command output includes non-gating SWIG deprecation warnings.
- Command output includes sqlite3 unclosed connection ResourceWarnings; gate status remains pass.

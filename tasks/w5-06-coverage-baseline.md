# W5-06 Coverage Baseline Report

## Scope

Baseline measurements for backend package-level coverage before enforcing the hard gate (>=80%).

## Environment

- Python: 3.14.0
- Test command root: backend/tests
- Coverage tool: pytest-cov

## Baseline Commands and Results

1. python -m pytest backend/tests --cov=backend.app.api --cov-report=term-missing
- Result: 14 passed
- Package total coverage: 91.8%

2. python -m pytest backend/tests --cov=backend.app.services --cov-report=term-missing
- Result: 14 passed
- Package total coverage: 93.3%

3. python -m pytest backend/tests --cov=backend.app.adapters --cov-report=term-missing
- Result: 14 passed
- Package total coverage: 92.7%

## Baseline Conclusion

All backend package groups are already above the target threshold of 80%. The gate can be enforced without expected regressions on the current branch.

## Notes

- Test output includes non-gating deprecation warnings related to SWIG types.
- Test output still reports sqlite3 unclosed connection ResourceWarnings; coverage thresholds are unaffected, but warning hygiene should be tracked separately.

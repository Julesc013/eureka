# Validation

- JSON contracts and inventory: pass.
- CLI help for summarizer, harness, validator, and failed-test rerunner: pass.
- Focused harness tests: pass.
- `python scripts/eureka_test_select.py --changed --failed-first --json`: pass.
- `python scripts/check_architecture_boundaries.py`: pass.
- AIDE doctor, validate, test, selftest: pass.
- AIDE verify: warn-only with 0 errors.
- Full unittest discovery: NOT_RUN_BY_POLICY.

Generated artifact cleanliness flags the new audit pack before commit because
the guard reads `git status`; rerun after commit is required for the final clean
working-tree signal.

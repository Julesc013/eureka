# Validation

Validation run:

- `git diff --check` - pass
- JSON syntax checks for LOCAL-09 policies, inventories, and audit report - pass
- `python scripts/validate_local_worker_runner.py` - pass with warning for pre-existing leakage
- focused local worker tests - pass
- current-generation LOCAL validators - pass with leakage warnings
- older phase-pinned LOCAL validators - fail on expected queue/forbidden-path assertions from their original phase
- `python scripts/check_architecture_boundaries.py` - pass
- `python scripts/audit_runtime_architecture_leakage.py --check --json` - fail with pre-existing 1030 findings
- `python scripts/validate_runtime_architecture_leakage.py` - fail with pre-existing leakage findings
- `python -m unittest discover -s tests -t .` - timed out after 10 minutes

Known warning: the runtime leakage gate still fails with pre-existing findings outside LOCAL-09.

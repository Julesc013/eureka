# Validation Matrix

All LOCAL validators were rerun. Stale queue-position checks were repaired and the LOCAL validators now pass with only the known leakage warning class.

Global gates:

- `git diff --check`: pass
- `check_generated_artifact_cleanliness.py --check --json`: pass
- `check_architecture_boundaries.py`: pass
- `audit_runtime_architecture_leakage.py --check --json`: fail, 1030 known findings
- `validate_runtime_architecture_leakage.py`: fail, audit check mode failed
- `python -m unittest discover -s tests -t .`: fail

AIDE checks passed or warned only: doctor, validate, test, selftest, verify, review-pack.

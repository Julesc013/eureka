# Validation Matrix

All LOCAL validators were rerun. Stale queue-position checks were repaired and the LOCAL validators now pass with only the known leakage warning class.

Global gates:

- `git diff --check`: pass
- `check_generated_artifact_cleanliness.py --check --json`: pass
- `check_architecture_boundaries.py`: pass
- `build_public_search_index.py --rebuild`: pass, repaired stale `site/dist/data/public_index` checksum drift
- `check_generated_artifact_drift.py --json`: pass after public search index rebuild
- `audit_runtime_architecture_leakage.py --check --json`: fail, 1030 known findings
- `validate_runtime_architecture_leakage.py`: fail, audit check mode failed
- `python -m unittest discover -s tests -t .`: fail, runtime leakage gate

AIDE checks passed or warned only: doctor, validate, test, selftest, verify, review-pack.

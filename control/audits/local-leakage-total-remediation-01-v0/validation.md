# Validation

- `git diff --check`: pass.
- `python -m unittest discover -s tests -t .`: pass, 4314 tests.
- `python scripts/check_architecture_boundaries.py`: pass.
- `python scripts/audit_runtime_architecture_leakage.py --check --json`: pass with warnings, zero new findings.
- `python scripts/validate_runtime_architecture_leakage.py`: pass.
- AIDE doctor/validate/test/selftest: pass.
- AIDE verify/review-pack: warning-only stale context/diff-scope findings.

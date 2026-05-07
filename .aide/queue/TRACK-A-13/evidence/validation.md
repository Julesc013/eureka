# TRACK-A-13 Validation Evidence

- `git diff --check`: PASS, LF-to-CRLF notices only.
- `python -m json.tool control/audits/track-a-13-static-searchpage-projection-dry-run-v0/projection_dry_run_report.json`: PASS.
- `python -m json.tool control/audits/track-a-13-static-searchpage-projection-dry-run-v0/generated/search_handoff.json`: PASS.
- `python scripts/validate_track_a_contracts.py`: PASS.
- `python scripts/audit_static_searchpage_projection.py --check`: PASS, expected WARN audit status with zero critical boundary violations.
- `python scripts/validate_static_searchpage_projection_plan.py`: PASS.
- `python scripts/generate_static_searchpage_projection.py --check`: PASS.
- `python scripts/validate_static_searchpage_projection_dry_run.py`: PASS.
- `python -m unittest tests.operations.test_static_searchpage_projection_dry_run`: PASS, 11 tests.
- `python -m unittest discover -s tests -t .`: PASS, 1742 tests.
- `python scripts/check_architecture_boundaries.py`: PASS, 479 Python files checked.
- Generated site artifact status: PASS, no generated site artifacts changed.
- AIDE Lite `doctor`, `validate`, `test`, `selftest`, `eval list`, `eval run`, and `adapter validate`: PASS.
- AIDE Lite `verify`: WARN with zero errors.
- AIDE Lite `review-pack`: WARN because the embedded verifier result is WARN with zero errors.

The AIDE verifier warnings are diff-scope and optional imported reference
warnings. They are WARN-only with zero verifier errors.

# TRACK-A-14 Validation

Observed validation for the object/source/need/candidate projection audit:

- `git status --short`: PASS before commit, expected A14 changed files only.
- `git diff --check`: PASS, LF-to-CRLF notices only.
- `python -m json.tool control/inventory/publication/object_source_need_candidate_projection_map.json`: PASS.
- `python -m json.tool control/audits/track-a-14-object-source-need-candidate-projection-v0/projection_audit_report.json`: PASS.
- `python scripts/validate_track_a_contracts.py`: PASS.
- `python scripts/audit_static_searchpage_projection.py --check`: PASS, WARN-only mapping gaps with zero critical violations.
- `python scripts/validate_static_searchpage_projection_plan.py`: PASS.
- `python scripts/validate_static_searchpage_projection_dry_run.py`: PASS.
- `python scripts/audit_object_source_need_candidate_projection.py --check`: PASS, WARN-only projection gaps with zero critical violations.
- `python -m unittest tests.operations.test_object_source_need_candidate_projection_audit`: PASS, 11 tests.
- `python -m unittest discover -s tests -t .`: PASS, 1753 tests.
- `python scripts/check_architecture_boundaries.py`: PASS, 479 Python files checked.
- AIDE Lite `doctor`, `validate`, `test`, `selftest`, `eval list`, `eval run`, and `adapter validate`: PASS.
- AIDE Lite `verify`: WARN with zero errors.
- AIDE Lite `review-pack`: WARN because the embedded verifier result is WARN with zero errors.

The AIDE verifier warnings are optional imported review-reference warnings and
diff-scope warnings from the compact local task packet. No verifier errors were
reported.

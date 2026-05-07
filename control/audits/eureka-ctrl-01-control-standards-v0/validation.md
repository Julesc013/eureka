# EUREKA-CTRL-01 Validation

Observed validation for the control standards bundle:

- `git diff --check`: PASS, with LF-to-CRLF notices only.
- `python -m json.tool control/audits/eureka-ctrl-01-control-standards-v0/eureka_ctrl_01_report.json`: PASS.
- `python scripts/validate_eureka_control_policy.py`: PASS.
- `python scripts/preview_eureka_changelog.py --message-file examples/commit_messages/valid_structured_commit.txt`: PASS.
- `python -m unittest tests.operations.test_eureka_control_policy tests.operations.test_eureka_changelog_preview`: PASS, 15 tests.
- `python -m unittest discover -s tests -t .`: PASS, 1731 tests.
- `python scripts/check_architecture_boundaries.py`: PASS, 479 Python files checked.
- `python scripts/validate_track_a_contracts.py`: PASS.
- `git check-ignore .aide.local/`: PASS.
- Strict secret scan over changed paths: PASS, 34 files.
- ASCII scan over changed paths: PASS, 34 files.
- Generated site artifact status: PASS, no generated site artifacts changed.
- AIDE Lite `doctor`, `validate`, `test`, `selftest`, `eval list`, `eval run`, and `adapter validate`: PASS.
- AIDE Lite `verify`: WARN with zero errors.
- AIDE Lite `review-pack`: WARN because the embedded verifier result is WARN with zero errors.

AIDE verifier warnings are generic diff-scope metadata for the new control paths
and optional AIDE status references. They are WARN-only with zero verifier
errors.

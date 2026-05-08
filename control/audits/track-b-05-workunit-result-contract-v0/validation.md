# TRACK-B-05 Validation

Validation commands for this milestone:

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/nodes/workunit_result_policy.json`
- `python -m json.tool control/inventory/nodes/workunit_result_status_registry.json`
- `python -m json.tool control/inventory/nodes/workunit_result_output_policy.json`
- `python -m json.tool control/inventory/nodes/workunit_result_review_policy.json`
- `python -m json.tool control/inventory/nodes/workunit_result_recovery_policy.json`
- `python -m json.tool control/audits/track-b-05-workunit-result-contract-v0/track_b_05_report.json`
- `python scripts/validate_eureka_workunit_result.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`

This validation is read-only and does not run WorkUnits.

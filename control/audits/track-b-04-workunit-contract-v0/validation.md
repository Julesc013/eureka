# TRACK-B-04 Validation

Validation commands for this milestone:

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/nodes/workunit_type_registry.json`
- `python -m json.tool control/inventory/nodes/workunit_policy.json`
- `python -m json.tool control/inventory/nodes/workunit_idempotency_policy.json`
- `python -m json.tool control/inventory/nodes/workunit_action_policy.json`
- `python -m json.tool control/inventory/nodes/workunit_input_output_policy.json`
- `python -m json.tool control/inventory/nodes/workunit_review_gate_policy.json`
- `python -m json.tool control/audits/track-b-04-workunit-contract-v0/track_b_04_report.json`
- `python scripts/validate_eureka_node_manifest.py`
- `python scripts/validate_eureka_node_policy.py`
- `python scripts/validate_eureka_node_capability.py`
- `python scripts/validate_eureka_workunit.py`
- `python -m unittest discover -s tests -t .`
- `python scripts/check_architecture_boundaries.py`

This validation is read-only and does not execute WorkUnits.

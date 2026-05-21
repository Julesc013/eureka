# Validation

Planned validation lanes:

- JSON shape checks for policies, inventories, result, next-task decision, and audit report.
- `python scripts/validate_workbench_result_lanes.py`
- `python scripts/validate_workbench_foundation.py`
- `python scripts/validate_search_interaction_contract.py`
- `python scripts/validate_contract_taxonomy.py`
- `python scripts/validate_repo_structure_canon.py`
- CLI operator/public/native projections.
- Focused runtime, operation, and script tests.
- Architecture boundaries.
- Generated artifact cleanliness after commit.
- AIDE doctor/validate/test/selftest/verify/review-pack/commit check.

Full unittest discovery is recommended because runtime view-model code was added. This task records PASS_WITH_WARNINGS if full discovery is not rerun.

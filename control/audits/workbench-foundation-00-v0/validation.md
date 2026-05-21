# Validation

Focused validator/test lanes plus architecture, generated artifact cleanliness, and AIDE checks are required. Full unittest discovery is optional for this planning-only task and was not required by scope.

Pre-commit validation completed:

- `git diff --check`: PASS
- `python scripts/validate_workbench_foundation.py`: PASS
- focused Workbench foundation tests: PASS
- `python scripts/validate_contract_taxonomy.py`: PASS
- `python scripts/validate_repo_structure_canon.py`: PASS with existing known debt
- `python scripts/check_architecture_boundaries.py`: PASS
- AIDE `doctor`, `validate`, `test`, `selftest`, `verify`, and `review-pack`: PASS after regenerating schema-complete AIDE packets

`python scripts/check_generated_artifact_cleanliness.py --check --json` reported the expected pre-commit audit-generated drift for `control/audits/workbench-foundation-00-v0/`. It must be rerun after commit, when the generated audit evidence is tracked.

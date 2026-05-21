# Validation

Planned validation:

- `python -m json.tool control/inventory/contract_taxonomy_input_state.json`
- `python -m json.tool control/inventory/contract_taxonomy_root_inventory.json`
- `python -m json.tool control/inventory/contract_taxonomy_authority_matrix.json`
- `python -m json.tool control/inventory/contract_taxonomy_duplicate_authority_report.json`
- `python -m json.tool control/inventory/contract_taxonomy_control_schemas_decision.json`
- `python -m json.tool control/inventory/contract_taxonomy_migration_backlog.json`
- `python scripts/validate_repo_structure_canon.py`
- `python scripts/validate_contract_taxonomy.py`
- `python -m unittest tests.operations.test_contract_taxonomy`
- `python -m unittest tests.scripts.test_validate_contract_taxonomy`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- AIDE Lite checks.

Focused command outcomes:

- JSON parse checks: PASS
- `python scripts/validate_contract_taxonomy.py --json`: PASS
- `python -m unittest tests.operations.test_contract_taxonomy tests.scripts.test_validate_contract_taxonomy -v`: PASS

Full discovery is not rerun in R0-03 because this task adds control-plane
classification, docs, validator, and focused tests only. The prior full suite
pass after `81198714` was `4740` tests, OK.

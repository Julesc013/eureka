# Validation

## Pre-Commit Results

- `git diff --check`: PASS (line-ending normalization warnings only; no whitespace errors)
- `python -m json.tool control/inventory/r0_03b_1_migration_result.json`: PASS
- `python -m json.tool control/inventory/r0_03b_1_reference_update_report.json`: PASS
- `python -m json.tool control/inventory/r0_03b_1_compatibility_shim_report.json`: PASS
- `python -m json.tool control/audits/r0-03b-1-contract-taxonomy-migration-v0/r0_03b_1_report.json`: PASS
- `python scripts/execute_contract_taxonomy_migration.py --dry-run --json`: PASS_WITH_WARNINGS (current tree has 13 blocked moves remaining)
- `python scripts/execute_contract_taxonomy_migration.py --apply --output control/audits/r0-03b-1-contract-taxonomy-migration-v0/generated/sample_migration_result.json --summary-output control/audits/r0-03b-1-contract-taxonomy-migration-v0/generated/sample_summary.md`: PASS_WITH_WARNINGS (idempotent post-migration apply)
- `python scripts/validate_contract_taxonomy_migration.py`: PASS
- `python scripts/audit_contract_taxonomy.py --check --json`: PASS_WITH_WARNINGS
- `python scripts/validate_contract_taxonomy_plan.py`: PASS
- `python -m unittest tests.operations.test_contract_taxonomy_migration`: PASS
- `python -m unittest tests.operations.test_contract_taxonomy_plan`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `python scripts/validate_runtime_architecture_leakage.py`: PRE-COMMIT WARN (dirty tree reports intended `contracts/` moves as forbidden product-path modifications; rerun required after commit)
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS_WITH_WARNINGS (stale review-packet references)
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN (expected diff-scope warnings for large schema migration; no errors)
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS (generated packet restored because `.aide/context/latest-review-packet.md` is outside this task write set)

## Post-Commit Results

- `git status --short`: PASS (clean tree)
- `python scripts/validate_runtime_architecture_leakage.py`: PASS
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS
- `python -m unittest discover -s tests -t .`: PASS (3815 tests)

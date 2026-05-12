# Validation

Validation commands recorded for R0-10:

- `git status --short`: PASS, only R0-10 allowed paths changed before commit
- `git diff --check`: PASS
- `python -m json.tool` on all R0-10 inventory outputs and report: PASS
- `python scripts/audit_r0_production_review.py --check --json`: PASS, status `blocked`
- `python scripts/audit_r0_production_review.py --output ...`: PASS
- `python scripts/prepare_dev_to_main_promotion.py --output control/inventory/dev_to_main_promotion_plan.json --json`: PASS
- `python scripts/validate_r0_production_review.py --json`: PASS
- `python scripts/validate_one_source_live_test.py`: PASS
- `python scripts/validate_reviewed_public_index.py`: PASS
- `python scripts/validate_review_queue_store.py`: PASS
- `python scripts/validate_evidence_ledger_store.py`: PASS
- `python scripts/validate_source_cache_store.py`: PASS
- `python scripts/validate_source_observation_seam.py`: WARN, existing contract taxonomy debt
- `python scripts/validate_runtime_architecture_leakage.py`: PASS
- `python scripts/validate_product_contract_tree.py`: WARN, existing contract-tree warning
- `python scripts/validate_contract_taxonomy_migration.py`: PASS
- `python -m unittest tests.operations.test_r0_production_review`: PASS
- `python -m unittest tests.operations.test_dev_to_main_promotion_plan`: PASS
- `python -m unittest discover -s tests -t .`: PASS, 3980 tests
- `python scripts/check_architecture_boundaries.py`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing review-packet reference warnings
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, stale active task packet path-scope warnings plus existing review-packet reference warnings
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS with verifier warnings; generated review packet was restored

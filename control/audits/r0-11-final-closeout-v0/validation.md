# Validation

Validation commands recorded for R0-11:

- `git status --short`: PASS, only R0-11 allowed paths changed before commit
- `git diff --check`: PASS
- `python -m json.tool` on all R0-11 final inventories and report: PASS
- `python scripts/audit_r0_final_closeout.py --check --json`: PASS, closeout status `blocked`
- `python scripts/repair_r0_safe_gaps.py --dry-run --json`: PASS, no safe bounded fixes found
- `python scripts/repair_r0_safe_gaps.py --apply --output ... --json`: PASS, no product/branch/index mutation
- `python scripts/summarize_r0_closeout.py --output ...`: PASS
- `python scripts/validate_r0_final_closeout.py`: PASS, includes all R0 validators, full unittest discovery, and architecture boundary checks
- `python scripts/validate_r0_production_review.py`: PASS with known R0 warnings
- `python scripts/validate_contract_taxonomy_plan.py`: PASS
- `python -m unittest tests.operations.test_r0_final_closeout`: PASS
- `python -m unittest tests.operations.test_r0_safe_gap_repair`: PASS
- `python -m unittest tests.operations.test_r0_future_task_gate`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing review-packet reference warnings
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, stale active-task path-scope warnings plus existing review-packet reference warnings
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS with verifier warnings; generated review packet was restored

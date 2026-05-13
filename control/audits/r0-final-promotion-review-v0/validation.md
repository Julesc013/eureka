# Validation

Validation status: `pass_with_warnings`.

No branch mutation, deployment, source sync, package installation, or site/dist regeneration was performed.

## Git And JSON

- `git status --short`: scoped review files only before commit.
- `git diff --check`: pass.
- `python -m json.tool` for all final promotion inventories and `promotion_review_report.json`: pass.

## Promotion Review

- `python scripts/audit_r0_final_promotion.py --check --json`: pass.
- `python scripts/audit_r0_final_promotion.py --output ... --git-state-output ... --summary-output ...`: pass.
- `python scripts/prepare_r0_dev_to_main_merge.py --output ... --json`: pass, plan-only, no branch mutation.
- `python scripts/validate_r0_final_promotion.py`: pass.

## R0 Validators

- `python scripts/check_generated_artifact_cleanliness.py --check --json`: pass on clean committed tree.
- `python scripts/validate_generated_artifact_drift.py`: pass on clean committed tree.
- `python scripts/validate_legacy_runtime_leakage_remediation.py`: pass.
- `python scripts/validate_runtime_architecture_leakage.py`: pass.
- `python scripts/validate_contract_taxonomy_remediation.py`: pass with expected product-contract-tree warning.
- `python scripts/validate_product_contract_tree.py`: valid with warnings, 0 errors.
- `python scripts/validate_r0_final_closeout.py`: pass with expected product-contract-tree / production-review warnings.
- `python scripts/validate_r0_production_review.py`: pass with expected product-contract-tree warning.
- `python scripts/validate_one_source_live_test.py`: pass.
- `python scripts/validate_reviewed_public_index.py`: pass.
- `python scripts/validate_review_queue_store.py`: pass.
- `python scripts/validate_evidence_ledger_store.py`: pass.
- `python scripts/validate_source_cache_store.py`: pass.
- `python scripts/validate_source_observation_seam.py`: pass.

## Tests And Boundaries

- `python -m unittest tests.operations.test_r0_final_promotion`: pass, 9 tests.
- `python -m unittest tests.operations.test_r0_dev_to_main_merge_plan`: pass, 3 tests.
- `python -m unittest discover -s tests -t .`: pass, 4044 tests.
- `python scripts/check_architecture_boundaries.py`: pass, 623 Python files checked.

## AIDE

- `py -3 .aide/scripts/aide_lite.py doctor`: pass.
- `py -3 .aide/scripts/aide_lite.py validate`: pass with known review-packet reference warnings.
- `py -3 .aide/scripts/aide_lite.py test`: pass.
- `py -3 .aide/scripts/aide_lite.py selftest`: pass.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 18 warnings, 0 errors; warnings are optional report-reference and active-task diff-scope warnings for this explicit R0 review prompt.
- `py -3 .aide/scripts/aide_lite.py review-pack`: pass, wrote `.aide/context/latest-review-packet.md`.

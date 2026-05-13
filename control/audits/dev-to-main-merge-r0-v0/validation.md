# Validation

Pre-merge required gates:

- `python scripts/validate_r0_final_promotion.py`: pass.
- `python scripts/validate_r0_final_closeout.py`: pass with expected warning-only product-contract-tree / production-review warnings.
- `python scripts/validate_generated_artifact_drift.py`: pass.
- `python scripts/validate_legacy_runtime_leakage_remediation.py`: pass.
- `python scripts/validate_contract_taxonomy_remediation.py`: pass with expected product-contract-tree warning.
- `python scripts/validate_reviewed_public_index.py`: pass.
- `python scripts/validate_review_queue_store.py`: pass.
- `python scripts/validate_evidence_ledger_store.py`: pass.
- `python scripts/validate_source_cache_store.py`: pass.
- `python scripts/validate_source_observation_seam.py`: pass.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: pass.
- `python scripts/check_architecture_boundaries.py`: pass.
- `python -m unittest discover -s tests -t .`: pass, 4044 tests.

Post-evidence validation is recorded in the final task response and in the commit body for this audit evidence.

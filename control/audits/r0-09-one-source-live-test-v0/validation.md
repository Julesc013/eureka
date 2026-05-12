# Validation

Validation commands recorded for the final R0-09 verification run:

- `git diff --check`: PASS
- `python -m json.tool` on R0-09 contracts, policies, inventory outputs, and report: PASS
- `python scripts/run_one_source_live_test.py ... --json`: PASS, dry-run made no network request
- `python scripts/run_one_source_live_test.py --live ... --json`: PASS, one PyPI JSON metadata request completed
- `python scripts/validate_one_source_live_test.py --require-live --json`: PASS
- `python -m unittest tests.runtime.test_pypi_json_metadata_source`: PASS
- `python -m unittest tests.runtime.test_one_source_live_test`: PASS
- `python -m unittest discover -s tests -t .`: PASS, 3961 tests
- `python scripts/validate_reviewed_public_index.py`: PASS
- `python scripts/validate_review_queue_store.py`: PASS
- `python scripts/validate_evidence_ledger_store.py`: PASS
- `python scripts/validate_source_cache_store.py`: PASS
- `python scripts/validate_source_observation_seam.py`: WARN, existing contract-taxonomy warning only
- `python scripts/validate_runtime_architecture_leakage.py`: PASS
- `python scripts/validate_product_contract_tree.py`: WARN, existing contract-tree warning only
- `python scripts/validate_contract_taxonomy_migration.py`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing review-packet reference warnings
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, existing review-packet reference warnings
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS with verifier warnings
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS

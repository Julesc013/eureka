# Validation

R0-08 validation was run in two groups: behavior checks while the working tree contained the R0-08 changes, and clean-tree compatibility checks after commit.

Pre-commit behavior checks:

- `git diff --check`: PASS
- `python -m json.tool` on all public index store contracts: PASS
- `python -m json.tool` on R0-08 inventory and report JSON: PASS
- `python scripts/init_public_index_store.py --db control/audits/r0-08-reviewed-public-index-rebuild-v0/generated/public_index_demo.sqlite --check --json`: PASS
- `python scripts/demo_reviewed_public_index.py ... --output control/audits/r0-08-reviewed-public-index-rebuild-v0/generated/sample_demo_output.json --json`: PASS
- `python scripts/rebuild_reviewed_public_index.py ... --dry-run --json`: PASS
- `python scripts/validate_reviewed_public_index.py`: PASS
- `python -m unittest tests.runtime.test_public_index_store tests.runtime.test_public_index_rebuild tests.runtime.test_public_index_search_absence tests.runtime.test_public_index_integration`: PASS
- `python scripts/validate_review_queue_store.py`: PASS
- `python scripts/validate_evidence_ledger_store.py`: PASS
- `python scripts/validate_source_cache_store.py`: PASS
- `python scripts/validate_source_observation_seam.py`: PASS_WITH_WARNINGS, existing R0-03B-2 contract taxonomy debt
- `python scripts/check_architecture_boundaries.py`: PASS

Clean-tree compatibility checks are recorded in the final task response. The reviewed index validator imports the new runtime package, runs in-memory and file-backed rebuild checks, validates JSON contracts, confirms accepted and rejected decision behavior, checks that input stores are not mutated, and scans the runtime package for forbidden imports and reserved vocabulary.

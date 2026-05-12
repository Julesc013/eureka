# Validation

R0-05 validation status: `pass_with_warnings`.

The durable source cache behavior passed. Warnings are inherited governance warnings from earlier R0 contract taxonomy debt and AIDE optional referenced paths; they do not indicate live calls, evidence acceptance, review decisions, or public/master index mutation.

| Command | Result |
| --- | --- |
| `git status --short` | PASS |
| `git diff --check` | PASS |
| `python -m json.tool contracts/stores/source_cache_store.v0.json` | PASS |
| `python -m json.tool contracts/stores/source_cache_entry.v0.json` | PASS |
| `python -m json.tool contracts/stores/source_cache_migration.v0.json` | PASS |
| `python -m json.tool contracts/stores/source_cache_status.v0.json` | PASS |
| `python -m json.tool control/inventory/source_cache_store_inventory.json` | PASS |
| `python -m json.tool control/inventory/source_cache_store_gap_register.json` | PASS |
| `python -m json.tool control/inventory/r0_05_next_task_decision.json` | PASS |
| `python -m json.tool control/audits/r0-05-durable-source-cache-store-v0/r0_05_report.json` | PASS |
| `python scripts/init_source_cache_store.py --db control/audits/r0-05-durable-source-cache-store-v0/generated/source_cache_demo.sqlite --check --json` | PASS |
| `python scripts/demo_source_cache_store.py --db control/audits/r0-05-durable-source-cache-store-v0/generated/source_cache_demo.sqlite --output control/audits/r0-05-durable-source-cache-store-v0/generated/sample_demo_output.json --json` | PASS |
| `python scripts/validate_source_cache_store.py` | PASS |
| `python scripts/validate_source_observation_seam.py` | WARN |
| `python scripts/validate_runtime_architecture_leakage.py` | PASS |
| `python scripts/validate_product_contract_tree.py` | WARN |
| `python scripts/validate_contract_taxonomy_migration.py` | PASS |
| `python -m unittest tests.runtime.test_source_cache_store` | PASS |
| `python -m unittest tests.runtime.test_source_cache_migrations` | PASS |
| `python -m unittest tests.runtime.test_source_cache_integration` | PASS |
| `python -m unittest tests.runtime.test_source_observation_seam` | PASS |
| `python -m unittest discover -s tests -t .` | PASS |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `py -3 .aide/scripts/aide_lite.py test` | PASS |
| `py -3 .aide/scripts/aide_lite.py selftest` | PASS |
| `py -3 .aide/scripts/aide_lite.py verify` | WARN |
| `py -3 .aide/scripts/aide_lite.py review-pack` | WARN |

Warnings:

- `validate_source_observation_seam.py` and `validate_product_contract_tree.py` still surface known R0-03B-2 contract taxonomy debt.
- AIDE verify/review-pack reported pre-existing optional referenced-path warnings. Final post-commit verify had `changed_files: 0`.
- F0 and dev-to-main remain blocked.

# Validation

R0-06 validation status: `pass_with_warnings`.

The durable evidence ledger behavior passed. Warnings are inherited governance warnings from earlier R0 contract taxonomy debt and AIDE optional referenced paths; they do not indicate live calls, review queue writes, evidence acceptance, or public/master index mutation.

| Command | Result |
| --- | --- |
| `git status --short` | PASS |
| `git diff --check` | PASS |
| `python -m json.tool contracts/stores/evidence_ledger_store.v0.json` | PASS |
| `python -m json.tool contracts/stores/evidence_candidate_record.v0.json` | PASS |
| `python -m json.tool contracts/stores/evidence_event.v0.json` | PASS |
| `python -m json.tool contracts/stores/evidence_conflict.v0.json` | PASS |
| `python -m json.tool contracts/stores/evidence_review_status.v0.json` | PASS |
| `python -m json.tool contracts/stores/evidence_ledger_migration.v0.json` | PASS |
| `python -m json.tool control/inventory/evidence_ledger_store_inventory.json` | PASS |
| `python -m json.tool control/inventory/evidence_ledger_store_gap_register.json` | PASS |
| `python -m json.tool control/inventory/r0_06_next_task_decision.json` | PASS |
| `python -m json.tool control/audits/r0-06-durable-evidence-ledger-store-v0/r0_06_report.json` | PASS |
| `python scripts/init_evidence_ledger_store.py --db control/audits/r0-06-durable-evidence-ledger-store-v0/generated/evidence_ledger_demo.sqlite --check --json` | PASS |
| `python scripts/demo_evidence_ledger_store.py --source-cache-db control/audits/r0-06-durable-evidence-ledger-store-v0/generated/source_cache_demo.sqlite --evidence-db control/audits/r0-06-durable-evidence-ledger-store-v0/generated/evidence_ledger_demo.sqlite --output control/audits/r0-06-durable-evidence-ledger-store-v0/generated/sample_demo_output.json --json` | PASS |
| `python scripts/validate_evidence_ledger_store.py` | PASS |
| `python scripts/validate_source_cache_store.py` | PASS |
| `python scripts/validate_source_observation_seam.py` | WARN |
| `python scripts/validate_runtime_architecture_leakage.py` | PASS |
| `python scripts/validate_product_contract_tree.py` | WARN |
| `python scripts/validate_contract_taxonomy_migration.py` | PASS |
| `python -m unittest tests.runtime.test_evidence_ledger_store` | PASS |
| `python -m unittest tests.runtime.test_evidence_ledger_migrations` | PASS |
| `python -m unittest tests.runtime.test_evidence_ledger_integration` | PASS |
| `python -m unittest tests.runtime.test_source_cache_store` | PASS |
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
- AIDE verify/review-pack reported pre-existing optional referenced-path warnings. Generated SQLite validation files were removed before commit, and final verify had `changed_files: 0`.
- F0 and dev-to-main remain blocked.

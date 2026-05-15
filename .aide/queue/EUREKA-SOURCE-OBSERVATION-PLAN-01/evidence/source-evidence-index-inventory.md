# Source / Evidence / Index Inventory

## Files Inspected

Q57 inspected these systems read-only:

- `runtime/source_observation/**`
- `runtime/source_cache/**`
- `runtime/evidence_ledger/**`
- `runtime/review_queue/**`
- `runtime/local_review/**`
- `runtime/public_index/**`
- `runtime/local_foundry/**` source/evidence bridge modules
- `contracts/source_cache/**`
- `contracts/evidence_ledger/**`
- `contracts/stores/*source_cache*`
- `contracts/stores/*evidence_ledger*`
- `contracts/stores/*review*`
- `contracts/stores/*public_index*`
- `contracts/master_index/**`
- `contracts/search/**`
- `contracts/query/*absence*`
- `contracts/views/**`
- `contracts/pages/**`
- `examples/source_cache_records/**`
- `examples/evidence_ledger_records/**`
- `examples/source_cache/dry_run/**`
- `examples/evidence_ledger/dry_run/**`
- `examples/source_cache_to_evidence/**`
- `examples/review_queue_entries/**`
- `examples/work_unit_results/**`
- `scripts/demo_source_observation_seam.py`
- `scripts/demo_source_cache_store.py`
- `scripts/demo_evidence_ledger_store.py`
- `scripts/demo_review_queue_store.py`
- `scripts/demo_reviewed_public_index.py`
- source/evidence/index validators under `scripts/validate_*`
- relevant tests under `tests/runtime/**`, `tests/operations/**`, and `tests/contracts/**`

## Relevant Modules

- Source observation: `runtime/source_observation/records.py`, `policy.py`, `requests.py`, `responses.py`, `observations.py`, `normalization.py`, `evidence.py`, `review.py`, `validation.py`.
- Source cache: `runtime/source_cache/store.py`, `records.py`, `dry_run.py`, `validation.py`.
- Evidence ledger: `runtime/evidence_ledger/store.py`, `records.py`, `dry_run.py`, `validation.py`.
- Review queue and decisions: `runtime/review_queue/store.py`, `runtime/review_queue/records.py`, `runtime/local_review/decisions.py`, `runtime/local_review/rebuild.py`.
- Reviewed public index: `runtime/public_index/rebuild.py`, `runtime/public_index/search.py`, `runtime/public_index/absence.py`, `runtime/public_index/store.py`, `runtime/public_index/validation.py`.

## Relevant Contracts

- `contracts/runtime/source_observation.v0.json`
- `contracts/source_cache/source_cache_record.v0.json`
- `contracts/evidence_ledger/evidence_ledger_record.v0.json`
- `contracts/stores/source_cache_entry.v0.json`
- `contracts/stores/evidence_ledger_store.v0.json`
- `contracts/stores/review_item_record.v0.json`
- `contracts/stores/review_decision.v0.json`
- `contracts/stores/public_index_record.v0.json`
- `contracts/stores/public_index_search_result.v0.json`
- `contracts/stores/public_index_absence_report.v0.json`
- `contracts/master_index/reviewed_public_index_rebuild.v0.json`
- `contracts/query/known_absence_record.v0.json`
- `contracts/views/search_page.v0.json`, `contracts/views/source_page.v0.json`, `contracts/views/review_page.v0.json`, `contracts/views/absence_page.v0.json`

## Relevant Tests

- `tests/runtime/test_source_observation_seam.py`
- `tests/runtime/test_source_cache_integration.py`
- `tests/runtime/test_evidence_ledger_integration.py`
- `tests/runtime/test_review_queue_store.py`
- `tests/runtime/test_public_index_rebuild.py`
- `tests/runtime/test_public_index_integration.py`
- `tests/runtime/test_public_index_search_absence.py`
- `tests/runtime/test_local_source_cache_runtime.py`
- `tests/runtime/test_local_evidence_ledger_runtime.py`
- `tests/operations/test_local_source_cache_runtime_scripts.py`
- `tests/operations/test_local_evidence_ledger_runtime_scripts.py`
- `tests/operations/test_source_cache_to_evidence_bridge_scripts.py`

## Relevant Examples / Fixtures

- `examples/source_cache_records/source_metadata_record_v0.json`
- `examples/source_cache_records/minimal_source_cache_record_v0.json`
- `examples/evidence_ledger_records/metadata_claim_record_v0.json`
- `examples/evidence_ledger_records/minimal_evidence_record_v0.json`
- `examples/source_cache/dry_run/minimal_package_metadata_summary/SOURCE_CACHE_CANDIDATE.json`
- `examples/source_cache/dry_run/minimal_internet_archive_metadata_summary/SOURCE_CACHE_CANDIDATE.json`
- `examples/evidence_ledger/dry_run/minimal_package_metadata_observation/EVIDENCE_LEDGER_CANDIDATE.json`
- `examples/evidence_ledger/dry_run/minimal_source_metadata_observation/EVIDENCE_LEDGER_CANDIDATE.json`
- `examples/source_cache_to_evidence/minimal_bridge_case_v0.json`
- `examples/review_queue_entries/source_cache_bridge_needs_review_v0.json`

## Disabled / Live Gates

- `runtime/source_observation/policy.py` blocks `live_network_request`, `source_sync`, `download`, `upload`, `execution`, `private_source_access`, `registry_mutation`, and `public_index_write` by default.
- Source cache and evidence ledger dry-run candidates require hard booleans such as `live_source_called: false`, `external_calls_performed: false`, `source_cache_mutated: false`, `evidence_ledger_mutated: false`, and `public_index_mutated: false`.
- Validation modules reject hidden/private roots and product roots for store paths.
- Demo scripts refuse forbidden output roots such as `runtime`, `contracts`, `site`, `.git`, `.aide.local`, `.local`, and `.cache`.

## Current Data Paths

Canonical product stores are not selected for Q58. The safe next implementation may write only temporary or Q58 evidence-local SQLite stores:

- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/source-cache.sqlite`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/evidence-ledger.sqlite`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/review-queue.sqlite`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/public-index.sqlite`

These are evidence-local generated outputs, not product truth.

## Fixture / Preview / Contract-Only Notes

- Committed source and evidence examples are fixture-only or candidate-only.
- Internet Archive, PyPI, GitHub Releases, Wayback, and other source-family examples are represented by disabled fixture/dry-run paths; Q57 does not select them for live use.
- Search/result/absence contracts exist; local `runtime/public_index` can search records and produce absence reports, while UI/object rendering remains outside Q58.

# Source / Evidence / Index Inventory

## Files Inspected

Q57 inspected these systems read-only:

- `runtime/source/observation/**`
- `runtime/source/cache/**`
- `runtime/evidence/ledger/**`
- `runtime/review/queue/**`
- `runtime/local/review/**`
- `runtime/index/public/**`
- `runtime/local/foundry/**` source/evidence bridge modules
- `contracts/source/cache/**`
- `contracts/evidence/ledger/**`
- `contracts/stores/*source_cache*`
- `contracts/stores/*evidence_ledger*`
- `contracts/stores/*review*`
- `contracts/stores/*public_index*`
- `contracts/index/master/**`
- `contracts/search/**`
- `contracts/query/*absence*`
- `contracts/view/pages/**`
- `contracts/surface/pages/**`
- `examples/sources/cache/records/**`
- `examples/evidence/ledger/records/**`
- `examples/sources/cache/dry_run/dry_run/**`
- `examples/evidence/ledger/dry_run/dry_run/**`
- `examples/sources/cache/to_evidence/**`
- `examples/review/queue_entries/**`
- `examples/work_units/results/**`
- `scripts/demo_source_observation_seam.py`
- `scripts/demo_source_cache_store.py`
- `scripts/demo_evidence_ledger_store.py`
- `scripts/demo_review_queue_store.py`
- `scripts/demo_reviewed_public_index.py`
- source/evidence/index validators under `scripts/validate_*`
- relevant tests under `tests/runtime/**`, `tests/operations/**`, and `tests/contracts/**`

## Relevant Modules

- Source observation: `runtime/source/observation/records.py`, `policy.py`, `requests.py`, `responses.py`, `observations.py`, `normalization.py`, `evidence.py`, `review.py`, `validation.py`.
- Source cache: `runtime/source/cache/store.py`, `records.py`, `dry_run.py`, `validation.py`.
- Evidence ledger: `runtime/evidence/ledger/store.py`, `records.py`, `dry_run.py`, `validation.py`.
- Review queue and decisions: `runtime/review/queue/store.py`, `runtime/review/queue/records.py`, `runtime/local/review/decisions.py`, `runtime/local/review/rebuild.py`.
- Reviewed public index: `runtime/index/public/rebuild.py`, `runtime/index/public/search.py`, `runtime/index/public/absence.py`, `runtime/index/public/store.py`, `runtime/index/public/validation.py`.

## Relevant Contracts

- `contracts/runtime/source/observation.v0.json`
- `contracts/source/cache/source_cache_record.v0.json`
- `contracts/evidence/ledger/evidence_ledger_record.v0.json`
- `contracts/stores/source_cache_entry.v0.json`
- `contracts/stores/evidence_ledger_store.v0.json`
- `contracts/stores/review_item_record.v0.json`
- `contracts/stores/review_decision.v0.json`
- `contracts/stores/public_index_record.v0.json`
- `contracts/stores/public_index_search_result.v0.json`
- `contracts/stores/public_index_absence_report.v0.json`
- `contracts/index/master/reviewed_public_index_rebuild.v0.json`
- `contracts/query/known_absence_record.v0.json`
- `contracts/view/pages/search_page.v0.json`, `contracts/view/pages/source_page.v0.json`, `contracts/view/pages/review_page.v0.json`, `contracts/view/pages/absence_page.v0.json`

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

- `examples/sources/cache/records/source_metadata_record_v0.json`
- `examples/sources/cache/records/minimal_source_cache_record_v0.json`
- `examples/evidence/ledger/records/metadata_claim_record_v0.json`
- `examples/evidence/ledger/records/minimal_evidence_record_v0.json`
- `examples/sources/cache/dry_run/dry_run/minimal_package_metadata_summary/SOURCE_CACHE_CANDIDATE.json`
- `examples/sources/cache/dry_run/dry_run/minimal_internet_archive_metadata_summary/SOURCE_CACHE_CANDIDATE.json`
- `examples/evidence/ledger/dry_run/dry_run/minimal_package_metadata_observation/EVIDENCE_LEDGER_CANDIDATE.json`
- `examples/evidence/ledger/dry_run/dry_run/minimal_source_metadata_observation/EVIDENCE_LEDGER_CANDIDATE.json`
- `examples/sources/cache/to_evidence/minimal_bridge_case_v0.json`
- `examples/review/queue_entries/source_cache_bridge_needs_review_v0.json`

## Disabled / Live Gates

- `runtime/source/observation/policy.py` blocks `live_network_request`, `source_sync`, `download`, `upload`, `execution`, `private_source_access`, `registry_mutation`, and `public_index_write` by default.
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
- Search/result/absence contracts exist; local `runtime/index/public` can search records and produce absence reports, while UI/object rendering remains outside Q58.

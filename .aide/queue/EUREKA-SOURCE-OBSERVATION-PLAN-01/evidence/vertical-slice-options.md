# Vertical Slice Options

## Option A - Fixture Observation/Evidence/Review/Index/Search Loop

Status: selected.

Required files:

- `runtime/source_observation/**`
- `runtime/source_cache/**`
- `runtime/evidence_ledger/**`
- `runtime/review_queue/**`
- `runtime/public_index/**`
- `scripts/demo_source_cache_store.py`
- `scripts/demo_review_queue_store.py`
- `scripts/demo_reviewed_public_index.py`
- `tests/runtime/test_public_index_integration.py`

Risk: medium local-fixture-only. Store writes are allowed only to temp or Q58 evidence-local SQLite files.

Validation:

- Add/run a Q58 vertical-slice test.
- Run existing source observation, source cache, evidence ledger, review queue, public index, search/absence tests.
- Run architecture boundaries and AIDE validation.

Expected output:

- Source observation and normalized observation from synthetic metadata.
- Source cache entry.
- Evidence candidate record.
- Local review item and local accept decision.
- Reviewed public index record in isolated temp/evidence DB.
- Search result for `demo project`.
- Scoped absence report for a missing query.
- Evidence report proving no live/network/provider/product-state mutation.

Why selected:

It exercises the whole intended vertical path using existing local runtime seams, avoids live source ambiguity, and can be implemented as a small harness/test without contract or runtime architecture changes.

## Option B - Committed Source Cache Fixture To Evidence Candidate

Status: rejected for Q58 as too narrow.

Required files:

- `examples/source_cache_records/source_metadata_record_v0.json`
- `scripts/bridge_source_cache_to_evidence.py`
- `runtime/local_foundry/source_cache_to_evidence.py`
- `tests/operations/test_source_cache_to_evidence_bridge_scripts.py`

Risk: low.

Validation:

- Existing bridge script tests and validator.

Expected output:

- Source-cache fixture bridge report and evidence candidate JSON.

Why rejected:

It does not prove source observation, local review decision, reviewed index projection, search result, or absence output in one behavioral loop.

## Option C - Internet Archive Metadata Fixture

Status: rejected for first slice.

Required files:

- `examples/source_cache/dry_run/minimal_internet_archive_metadata_summary/SOURCE_CACHE_CANDIDATE.json`
- `examples/evidence_ledger/dry_run/minimal_source_metadata_observation/EVIDENCE_LEDGER_CANDIDATE.json`
- Internet Archive connector validators.

Risk: medium/high due live-source branding despite fixture hard booleans.

Validation:

- Dry-run source cache and evidence ledger validators only.

Expected output:

- Fixture-only IA source cache/evidence dry-run report.

Why rejected:

The next product slice should avoid any source family that could be confused with live access. IA fixtures remain useful after the generic local loop is proven.

## Option D - PyPI Metadata Fixture

Status: rejected for first slice.

Required files:

- `examples/source_cache/dry_run/minimal_package_metadata_summary/SOURCE_CACHE_CANDIDATE.json`
- `examples/evidence_ledger/dry_run/minimal_package_metadata_observation/EVIDENCE_LEDGER_CANDIDATE.json`
- PyPI connector approval/runtime validators.

Risk: medium/high due package-registry/live-source ambiguity.

Validation:

- Dry-run source cache and evidence ledger validators only.

Expected output:

- Fixture-only PyPI metadata source/evidence candidate report.

Why rejected:

It is useful later, but the first Q58 implementation should prove the local loop with synthetic fixture data and no connector branding.

# Selected Slice Plan

Selected option: Fixture Observation/Evidence/Review/Index/Search Loop.

Next task title: `Q58 Eureka Fixture Source Observation Vertical Slice v0`.

## Exact Vertical Path

1. Create or load one synthetic/local metadata source record.
2. Build one metadata request and metadata response without network access.
3. Build a source observation.
4. Normalize the observation.
5. Build a source cache entry and persist it only to an isolated temp or Q58 evidence-local SQLite store.
6. Build an evidence candidate and persist it only to an isolated temp or Q58 evidence-local SQLite store.
7. Enqueue one local review item and record one explicit local-only accept decision in an isolated review queue store.
8. Rebuild one reviewed public index record into an isolated public-index SQLite store.
9. Search the isolated reviewed index for `demo project`.
10. Build a scoped absence report for a missing query.
11. Emit structured evidence proving no live/source/provider/product-state mutation occurred.

## Risk Class

`medium_local_fixture_only`

Risk is medium because Q58 may write local SQLite stores, but those stores must be temp or evidence-local outputs and must not be product truth.

## Source Data Choice

Use synthetic/local fixture data from the existing source observation/source cache demo path, not IA/PyPI/GitHub/Wayback branded fixtures.

Preferred input refs:

- `scripts/demo_source_cache_store.py::build_demo_objects`
- `runtime/source/observation/**`
- Optional comparison fixture: `examples/sources/cache/records/source_metadata_record_v0.json`

## What Remains Disabled

- Live probes.
- Crawling, downloading, scraping.
- Provider/model calls.
- Source sync.
- Registry mutation.
- Canonical source-cache writes.
- Canonical evidence-ledger writes.
- Canonical/public index writes outside the isolated Q58 store.
- Site deploy and static/public artifact mutation.
- Hosted public search.
- Connector execution.
- Branch/remote/tag/GitHub mutation.

## Q58 Allowed Paths

- `.aide/queue/EUREKA-SOURCE-SLICE-01/**`
- `.aide/reports/eureka-fixture-source-observation-slice.md`
- `runtime/local/foundry/fixture_source_observation_slice.py`
- `scripts/validate_fixture_source_observation_vertical_slice.py`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py`

Q58 should avoid contracts unless implementation proves an unavoidable gap. Any contract change should split into a separate reviewed task.

## Q58 Forbidden Paths

- `.git/**`, `.github/**`, `.env`, `secrets/**`, `.aide.local/**`
- `contracts/**` unless Q58 is explicitly split for contract work
- `surfaces/**`, `site/**`, `snapshots/**`, `native/**`, `crates/**`, `examples/**`, `evals/**`
- product source/evidence/index data roots
- connector live/probe runtime files
- release/deploy/build outputs

## Validation Plan

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 scripts/check_architecture_boundaries.py`
- `py -3 scripts/validate_fixture_source_observation_vertical_slice.py --json`
- `py -3 -m unittest tests.runtime.test_fixture_source_observation_vertical_slice`
- targeted existing tests for source observation, source cache, evidence ledger, review queue, public index rebuild, and search/absence.
- `git diff --check`
- targeted secret/local-state scan.

## Evidence Plan

Q58 must write:

- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/changed-files.md`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/validation.md`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run-report.json`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/product-boundary-preservation.md`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/remaining-risks.md`

If persistent fixture stores are written, they must be under `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/` or a temp directory, and they must be treated as evidence only.

## Expected Implementation Size

One-shot if limited to one small runtime harness, one validator script, and tests. Split if contracts, UI/surface, connector family, or site changes appear necessary.

## Why This Is The Safest Useful Slice

It proves behavior across the intended local product chain while avoiding live source ambiguity, external calls, source/evidence/index product-state mutation, and UI/deploy scope.

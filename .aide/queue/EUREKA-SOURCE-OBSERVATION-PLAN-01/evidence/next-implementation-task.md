# Next Implementation Task

Task ID: `EUREKA-SOURCE-SLICE-01`

Title: `Q58 Eureka Fixture Source Observation Vertical Slice v0`

Task class: product vertical-slice implementation.

Risk class: `medium_local_fixture_only`.

Sizing: one-shot, split only if contracts or UI/surface changes become necessary.

## Objective

Implement a small, deterministic, fixture/local-only vertical-slice harness that proves:

source observation -> normalized observation -> source cache entry -> evidence candidate -> local review decision -> reviewed public index record -> search result -> scoped absence report.

## Why

Eureka has many scaffolds and audits. Q58 should prove real local behavior across the chain without claiming production readiness, using no live sources and no product-state mutation.

## Exact Allowed Paths

- `.aide/queue/EUREKA-SOURCE-SLICE-01/**`
- `.aide/reports/eureka-fixture-source-observation-slice.md`
- `runtime/local_foundry/fixture_source_observation_slice.py`
- `scripts/validate_fixture_source_observation_vertical_slice.py`
- `tests/runtime/test_fixture_source_observation_vertical_slice.py`
- `tests/operations/test_fixture_source_observation_vertical_slice_script.py`

## Exact Forbidden Paths

- `.git/**`
- `.github/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `contracts/**` unless Q58 is split and separately reviewed
- `surfaces/**`
- `site/**`
- `snapshots/**`
- `native/**`
- `crates/**`
- `examples/**`
- `evals/**`
- connector live/probe runtime files
- source-cache/evidence-ledger/public-index canonical product state
- deploy/release/build output directories

## Implementation Outline

1. Add a runtime-local harness that composes existing source observation, source cache, evidence ledger, review queue, public index, search, and absence APIs.
2. Default to temp directory stores; support an explicit evidence output root only under `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/`.
3. Use synthetic package metadata fixture/local data and no connector/live source.
4. Persist source cache, evidence ledger, review queue, and public index only in isolated fixture stores.
5. Record a local-only review accept decision with explicit local limitation text.
6. Search the isolated public index for `demo project` and produce a scoped absence report for a missing query.
7. Emit a JSON report with hard booleans proving no live/network/provider/source-sync/product-state mutation occurred.
8. Add tests that monkeypatch/block network where practical and assert no canonical product roots are written.
9. Add a validator script that runs the harness and checks the report.

## Validation Commands

- `py -3 scripts/validate_fixture_source_observation_vertical_slice.py --json`
- `py -3 -m unittest tests.runtime.test_fixture_source_observation_vertical_slice`
- `py -3 -m unittest tests.operations.test_fixture_source_observation_vertical_slice_script`
- `py -3 -m unittest tests.runtime.test_source_observation_seam tests.runtime.test_source_cache_integration tests.runtime.test_evidence_ledger_integration tests.runtime.test_review_queue_store tests.runtime.test_public_index_rebuild tests.runtime.test_public_index_search_absence`
- `py -3 scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `git diff --check`
- targeted secret/local-state scan

## Acceptance Criteria

- Fixture vertical-slice report exists and validates.
- The report includes source observation, normalized observation, source cache entry, evidence candidate, review item, review decision, public index record, search result, and absence report.
- Search for `demo project` returns one local reviewed-index result.
- Missing-query absence report is scoped and does not claim global absence.
- All persistent stores are temp or Q58 evidence-local only.
- No live source, network, provider/model, source sync, registry, download, site deploy, or release action occurs.
- No canonical source cache, evidence ledger, public index, master index, site/dist, product docs, or product fixtures are mutated.
- Architecture check and targeted tests pass or failures are recorded honestly.

## Evidence Files

- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/changed-files.md`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/validation.md`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run-report.json`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/product-boundary-preservation.md`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/remaining-risks.md`

## Non-Goals

- No live source implementation.
- No connector runtime execution.
- No provider/model calls.
- No source sync.
- No canonical product-state mutation.
- No public/hosted search launch.
- No UI/surface/site work.
- No contract/schema changes unless split.
- No release or CI work.

## Rollback / Revert Notes

Q58 should be revertible by removing the new harness, validator script, tests, and Q58 `.aide` evidence. It must not leave canonical stores or product-generated state behind.

## Final Output Format

Return `STATUS`, `SUMMARY`, `COMMITS`, `SLICE RESULT`, `PRESERVATION`, `VALIDATION`, `RISKS`, and `NEXT`.

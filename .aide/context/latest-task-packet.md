# AIDE Latest Task Packet

## PHASE

SEED-BATCH-MANUALS-SCANS-00 - add manuals and scanned-documents discovery batch

## GOAL

Add `manuals_docs_scans` as the third discovery domain using the existing query
planner, candidate index, SCOUT, review batch, snapshot handoff, public-alpha
reassess, and public search UX model lanes.

## WHY

`PUBLIC-ALPHA-REASSESS-03` kept public launch deferred. The limited reviewed
projection count is 4, which improves internal demo/review usefulness but is
below launch threshold. Manuals and scanned documents are a safer third-domain
corpus wedge before driver/support-media work.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_reassess_03_result.json`
- `runtime/seed_batches/frontier_media.py`
- `runtime/seed_batches/legacy_software.py`
- `scripts/validate_seed_batch_frontier_media.py`
- `scripts/validate_seed_batch_legacy_software.py`
- `examples/seed_batches/frontier_media/`
- `examples/seed_batches/legacy_software/`

## CURRENT_STATE

- `dev == origin/dev` at task start.
- latest prior commit: `8ba7c760 feat(task): reassess alpha after local apply`
- public alpha launch recommended: false
- total limited reviewed projection count: 4
- next needed domain: `manuals_docs_scans`

## ALLOWED_PATHS

- `.aide/queue/SEED-BATCH-MANUALS-SCANS-00/**`
- `.aide/queue/SEED-BATCH-DRIVER-SUPPORT-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-04/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-04/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/seed_batches/**`
- `contracts/candidates/**`
- `contracts/scout/**`
- `contracts/review/**`
- `contracts/search/query_plan/**`
- `runtime/seed_batches/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/scout/**`
- `runtime/review/batch/**`
- `runtime/public_alpha/**`
- `scripts/eureka_seed_batch_manuals_scans.py`
- `scripts/eureka_seed_batch_run.py`
- `scripts/eureka_seed_batch_report.py`
- `scripts/validate_seed_batch_manuals_scans.py`
- `scripts/validate_seed_batch_frontier_media.py`
- `scripts/validate_seed_batch_legacy_software.py`
- `tests/runtime/test_*manuals_scans*.py`
- `tests/operations/test_seed_batch_manuals_scans_scripts.py`
- `tests/scripts/test_validate_seed_batch_manuals_scans.py`
- `examples/seed_batches/manuals_scans/**`
- `examples/query_plans/manuals_scans/**`
- `examples/candidates/manuals_scans/**`
- `examples/scout/manuals_scans/**`
- `examples/review_batch/manuals_scans/**`
- `examples/public_alpha/manuals_scans/**`
- `control/policies/seed_batch_manuals_scans*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/seed_batch_manuals_scans*.json`
- `docs/architecture/SEED_BATCH_MANUALS_SCANS.md`
- `docs/operations/SEED_BATCH_MANUALS_SCANS_RUNBOOK.md`
- `docs/operations/POST_SEED_BATCH_MANUALS_SCANS_PLAN.md`
- `docs/reference/MANUALS_SCANS_QUERY_SET.md`
- `docs/reference/MANUALS_SCANS_SUPPRESSIONS.md`
- `control/audits/seed-batch-manuals-scans-00-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `../instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- raw live source responses
- raw IA responses
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## NON_GOALS

- No deployment, publication, public launch, or readiness claim.
- No accepted truth, reviewed/master/public index mutation, or operator instance mutation.
- No live source calls, downloads, file fetches, OCR, extraction, model/provider calls, or raw live responses.
- No rights-clearance, scan-completeness, or OCR-quality claims.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add `runtime/seed_batches/manuals_scans.py`.
- Add dedicated and generic CLI support.
- Add manuals/scans policies, docs, examples, inventory, audit evidence, validator, and focused tests.
- Keep all outputs metadata-only, review-required, candidate-only, and public-alpha reassess input only.

## VALIDATION

- `git diff --check`
- `python scripts/validate_seed_batch_manuals_scans.py`
- related public-alpha, snapshot, existing seed-batch, review-batch, SCOUT,
  candidate-index, query-planner, public-search UX, public-alpha readonly,
  source-action, architecture, and generated-artifact validators
- focused manuals/scans unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- fixture seed batch passes
- 16 required manuals/scans queries are present
- required suppressions are present
- source families are bounded metadata/descriptor/source-pack only
- candidate index, SCOUT, review, snapshot handoff, public-alpha input, docs,
  inventory, and audit evidence exist
- no downloads, file fetches, OCR, extraction, source calls, mutation, readiness,
  rights-clearance, scan-completeness, or OCR-quality claims
- next recommended task: `SEED-BATCH-DRIVER-SUPPORT-00`

## EVIDENCE

- `control/inventory/seed_batch_manuals_scans_result.json`
- `examples/seed_batches/manuals_scans/`
- `control/audits/seed-batch-manuals-scans-00-v0/`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses `STATUS`, `SUMMARY`, `SEED_BATCH_MANUALS_SCANS`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.

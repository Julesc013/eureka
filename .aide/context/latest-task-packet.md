# AIDE Latest Task Packet

## PHASE

SEED-BATCH-DRIVER-SUPPORT-00 - add driver and support-media discovery batch

## GOAL

Add `driver_support_media` as a repeatable discovery seed batch using the
existing query planner, candidate index, SCOUT, review batch, snapshot handoff,
public-alpha reassess, and public search UX model lanes.

## WHY

`PUBLIC-ALPHA-REASSESS-03` kept public launch deferred. Manuals/scans is now
complete, and the next needed discovery domain is driver/support media. This
domain is useful but higher risk, so it remains metadata-only and review-only.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_reassess_03_result.json`
- `control/inventory/seed_batch_manuals_scans_result.json`
- `runtime/seed_batches/manuals_scans.py`
- `runtime/seed_batches/driver_support.py`
- `scripts/validate_seed_batch_manuals_scans.py`
- `scripts/validate_seed_batch_driver_support.py`

## CURRENT_STATE

- `dev == origin/dev` at task start.
- latest prior commit: `4f51968a feat(seed): add manuals scans discovery batch`
- public alpha launch recommended: false
- current limited reviewed projection count: 4
- target domain: `driver_support_media`

## ALLOWED_PATHS

- `.aide/queue/SEED-BATCH-DRIVER-SUPPORT-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-04/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-04/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
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
- `scripts/eureka_seed_batch_driver_support.py`
- `scripts/eureka_seed_batch_run.py`
- `scripts/eureka_seed_batch_report.py`
- `scripts/validate_seed_batch_driver_support.py`
- `tests/runtime/test_*driver_support*.py`
- `tests/operations/test_seed_batch_driver_support_scripts.py`
- `tests/scripts/test_validate_seed_batch_driver_support.py`
- `examples/seed_batches/driver_support/**`
- `examples/query_plans/driver_support/**`
- `examples/candidates/driver_support/**`
- `examples/scout/driver_support/**`
- `examples/review_batch/driver_support/**`
- `examples/public_alpha/driver_support/**`
- `control/policies/seed_batch_driver*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/seed_batch_driver_support*.json`
- `docs/architecture/SEED_BATCH_DRIVER_SUPPORT.md`
- `docs/operations/SEED_BATCH_DRIVER_SUPPORT_RUNBOOK.md`
- `docs/operations/POST_SEED_BATCH_DRIVER_SUPPORT_PLAN.md`
- `docs/reference/DRIVER_SUPPORT_QUERY_SET.md`
- `docs/reference/DRIVER_SUPPORT_SUPPRESSIONS.md`
- `control/audits/seed-batch-driver-support-00-v0/**`

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
- No live source calls, downloads, file fetches, extraction, install/execution,
  model/provider calls, or raw live responses.
- No malware-clean, compatibility, rights-clearance, crack/keygen/serial, or
  driver-updater support claims.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add `runtime/seed_batches/driver_support.py`.
- Add dedicated and generic CLI support.
- Add driver/support policies, docs, examples, inventory, audit evidence,
  validator, and focused tests.
- Keep all outputs metadata-only, review-required, candidate-only, and
  public-alpha reassess input only.

## VALIDATION

- `git diff --check`
- `python scripts/validate_seed_batch_driver_support.py`
- related seed-batch, public-alpha, snapshot, review-batch, SCOUT,
  candidate-index, query-planner, public-search UX, public-alpha readonly,
  source-action, architecture, and generated-artifact validators
- focused driver/support unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- fixture seed batch passes
- 16 required driver/support queries are present
- required suppressions are present
- source families are bounded metadata/descriptor/source-pack only
- candidate index, SCOUT, review, snapshot handoff, public-alpha input, docs,
  inventory, and audit evidence exist
- no downloads, file fetches, extraction, install/execution, source calls,
  mutation, readiness, safety, compatibility, or rights-clearance claims
- next recommended task: `SNAPSHOT-REFRESH-04`

## EVIDENCE

- `control/inventory/seed_batch_driver_support_result.json`
- `examples/seed_batches/driver_support/`
- `control/audits/seed-batch-driver-support-00-v0/`

## TOKEN_ESTIMATE

medium

## OUTPUT_SCHEMA

Final report uses `STATUS`, `SUMMARY`, `SEED_BATCH_DRIVER_SUPPORT`,
`VALIDATION`, `BOUNDARIES`, and `NEXT_TASK`.

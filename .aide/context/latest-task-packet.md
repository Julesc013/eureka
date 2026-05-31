# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-REASSESS-01 - reassess alpha after live metadata snapshot refresh

## GOAL

Produce an evidence-based public-alpha product decision after the live metadata
pilot and `SNAPSHOT-REFRESH-01`.

## WHY

The snapshot is more useful for internal demo and review because it now includes
live-metadata-derived candidates, but the public search corpus still has only
one reviewed record. The reassessment must keep that distinction explicit.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/snapshot_refresh_01_result.json`
- `control/inventory/live_metadata_pilot_result.json`
- `control/inventory/public_alpha_reassess_result.json`
- `control/inventory/public_search_ux_model_result.json`

## CURRENT_STATE

- reviewed records: 1
- fixture candidates: 28
- live metadata candidates: 8
- total candidates: 36
- known needs: 28
- bounded absences: 2
- public launch track: deferred for discovery coverage

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-REASSESS-01/**`
- `.aide/queue/REVIEW-LIVE-METADATA-CANDIDATES-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-02/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-02/**`
- `.aide/queue/SEED-BATCH-MANUALS-SCANS-00/**`
- `.aide/queue/SEED-BATCH-DRIVER-SUPPORT-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/publication/**`
- `contracts/snapshot/**`
- `contracts/relay/**`
- `contracts/capabilities/**`
- `contracts/seed_batches/**`
- `contracts/candidates/**`
- `contracts/scout/**`
- `contracts/discovery/**`
- `contracts/review/**`
- `contracts/search/query_plan/**`
- `contracts/view/models/public_search/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `runtime/public_alpha/**`
- `runtime/gateway/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/capabilities/**`
- `runtime/seed_batches/**`
- `runtime/candidate_index/**`
- `runtime/scout/**`
- `runtime/review/batch/**`
- `runtime/local_eval/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `surfaces/web/workbench/**`
- `surfaces/files/**`
- `surfaces/text/**`
- `surfaces/lite/**`
- `scripts/eureka_public_alpha_reassess.py`
- `scripts/eureka_public_alpha_reassess_report.py`
- `scripts/eureka_public_alpha_route_smoke.py`
- `scripts/validate_public_alpha_reassess.py`
- `scripts/validate_snapshot_refresh.py`
- `scripts/validate_live_metadata_pilot_batch.py`
- `scripts/validate_public_search_ux_model.py`
- `scripts/validate_seed_batch_frontier_media.py`
- `scripts/validate_seed_batch_legacy_software.py`
- `scripts/validate_review_batch.py`
- `scripts/validate_candidate_index_runtime.py`
- `scripts/validate_public_alpha_readonly.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_public_alpha_reassess.py`
- `tests/runtime/test_public_alpha_reassess_metrics.py`
- `tests/runtime/test_public_alpha_reassess_routes.py`
- `tests/runtime/test_public_alpha_reassess_decision.py`
- `tests/runtime/test_public_alpha_reassess_live_metadata.py`
- `tests/runtime/test_public_alpha_reassess_public_search_view_models.py`
- `tests/runtime/test_public_alpha_reassess_boundaries.py`
- `tests/operations/test_public_alpha_reassess_scripts.py`
- `tests/scripts/test_validate_public_alpha_reassess.py`
- `examples/public_alpha/reassess/**`
- `examples/snapshots/refresh/**`
- `examples/snapshots/refresh/live_metadata/**`
- `examples/relay/refresh/**`
- `examples/seed_batches/frontier_media/**`
- `examples/seed_batches/legacy_software/**`
- `examples/live_metadata_pilot/**`
- `examples/view_models/public_search/**`
- `control/policies/public_alpha_reassess_policy.json`
- `control/policies/public_alpha_reassess_threshold_policy.json`
- `control/policies/public_alpha_reassess_route_smoke_policy.json`
- `control/policies/public_alpha_reassess_live_metadata_policy.json`
- `control/policies/public_alpha_reassess_non_claim_policy.json`
- `control/policies/public_alpha_reassess_next_work_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_reassess_01_*.json`
- `docs/architecture/PUBLIC_ALPHA_REASSESS_01.md`
- `docs/operations/PUBLIC_ALPHA_REASSESS_01_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md`
- `docs/operations/POST_PUBLIC_ALPHA_REASSESS_01_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md`
- `docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md`
- `docs/reference/PUBLIC_ALPHA_LIVE_METADATA_REASSESSMENT.md`
- `control/audits/public-alpha-reassess-01-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
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

- No deployment or publication.
- No public launch or production readiness claim.
- No live source calls.
- No downloads, extraction, model calls, execution, or install behavior.
- No reviewed, master, or public index mutation.
- No candidate promotion or accepted truth creation.
- No raw live response commit.
- No full unittest discovery inside AI.

## IMPLEMENTATION

- Add live metadata reassessment contracts and policy.
- Build v1 runtime metrics, blocker, decision, boundary, and next-work packets.
- Generate public-safe examples, inventory packets, and audit evidence.
- Validate public search view-model coverage and route/API smoke from examples.
- Keep live metadata candidates review-only and launch recommendation false.

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_reassess.py`
- `python scripts/validate_snapshot_refresh.py`
- `python scripts/validate_live_metadata_pilot_batch.py`
- `python scripts/validate_public_search_ux_model.py`
- seed, review, SCOUT, candidate, planner, relay, public-readonly, source validators
- focused public alpha reassess unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- Counts are recorded: 1 reviewed, 28 fixture candidates, 8 live metadata
  candidates, 28 needs, 2 absences.
- Launch remains not recommended.
- Internal demo/review is recommended.
- Live candidate review and a later snapshot refresh are recommended.
- Boundary reports keep all mutation, deployment, extraction, download, model,
  live-source, and readiness flags false.
- Focused validators and tests pass.

## OUTPUT_SCHEMA

Final report uses the user-requested PUBLIC_ALPHA_REASSESS_01 format with
validation and boundary summaries.

## TOKEN_ESTIMATE

medium

## EVIDENCE

- `examples/public_alpha/reassess/live_metadata/`
- `control/inventory/public_alpha_reassess_01_result.json`
- `control/audits/public-alpha-reassess-01-v0/`

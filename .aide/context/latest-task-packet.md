# AIDE Latest Task Packet

## PHASE

SNAPSHOT-REFRESH-01 - refresh snapshots after bounded live metadata pilot

## GOAL

Package existing reviewed records, seed-batch candidates, and redacted live
metadata candidates into read-only snapshot, relay, public-search view-model,
and public-alpha reassessment packets.

## WHY

The bounded live metadata pilot produced real source-backed candidate
summaries. They need to be visible in the snapshot layer without being promoted
to reviewed truth or public index material.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/live_metadata_pilot_result.json`
- `control/inventory/snapshot_refresh_result.json`
- `control/inventory/public_search_ux_model_result.json`
- `control/inventory/public_alpha_reassess_result.json`

## CURRENT_STATE

- Live metadata source family: internet_archive_metadata
- Selected live pilot queries: 8
- Total live metadata requests: 16
- Existing reviewed records: 1
- Seed fixture candidates: 28
- Live metadata candidates: 8
- Known needs: 28
- Bounded absences: 2

## ALLOWED_PATHS

- `.aide/queue/SNAPSHOT-REFRESH-01/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/snapshot/**`
- `contracts/relay/**`
- `contracts/capabilities/**`
- `contracts/seed_batches/**`
- `contracts/candidates/**`
- `contracts/scout/**`
- `contracts/discovery/**`
- `contracts/review/**`
- `contracts/search/query_plan/**`
- `contracts/source/action/**`
- `contracts/view/models/public_search/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/capabilities/**`
- `runtime/seed_batches/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/candidates/**`
- `runtime/scout/**`
- `runtime/discovery/**`
- `runtime/review/batch/**`
- `runtime/review/queue/**`
- `runtime/source/action/**`
- `runtime/local_eval/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/gateway/**`
- `runtime/public_alpha/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `surfaces/web/workbench/**`
- `surfaces/files/**`
- `surfaces/text/**`
- `surfaces/lite/**`
- `scripts/eureka_snapshot_refresh.py`
- `scripts/eureka_snapshot_refresh_report.py`
- `scripts/eureka_relay_project.py`
- `scripts/eureka_snapshot_validate.py`
- `scripts/validate_snapshot_refresh.py`
- `scripts/validate_live_metadata_pilot_batch.py`
- `scripts/validate_public_search_ux_model.py`
- `scripts/validate_public_alpha_reassess.py`
- `scripts/validate_seed_batch_frontier_media.py`
- `scripts/validate_seed_batch_legacy_software.py`
- `scripts/validate_review_batch.py`
- `scripts/validate_scout_runtime.py`
- `scripts/validate_candidate_index_runtime.py`
- `scripts/validate_snapshot_relay.py`
- `scripts/validate_public_alpha_readonly.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_snapshot_refresh.py`
- `tests/runtime/test_snapshot_refresh_seed_handoffs.py`
- `tests/runtime/test_snapshot_refresh_candidate_sections.py`
- `tests/runtime/test_snapshot_refresh_live_metadata_section.py`
- `tests/runtime/test_snapshot_refresh_needs_absences.py`
- `tests/runtime/test_snapshot_refresh_review_queue_summary.py`
- `tests/runtime/test_snapshot_refresh_relay_projection.py`
- `tests/runtime/test_snapshot_refresh_public_search_view_models.py`
- `tests/runtime/test_snapshot_refresh_boundaries.py`
- `tests/operations/test_snapshot_refresh_scripts.py`
- `tests/scripts/test_validate_snapshot_refresh.py`
- `examples/snapshots/refresh/**`
- `examples/relay/refresh/**`
- `examples/live_metadata_pilot/**`
- `examples/candidates/live_metadata/**`
- `examples/scout/live_metadata/**`
- `examples/review_batch/live_metadata/**`
- `examples/public_alpha/reassess/**`
- `control/policies/snapshot_refresh_policy.json`
- `control/policies/snapshot_refresh_reviewed_record_policy.json`
- `control/policies/snapshot_refresh_candidate_policy.json`
- `control/policies/snapshot_refresh_live_metadata_policy.json`
- `control/policies/snapshot_refresh_need_absence_policy.json`
- `control/policies/snapshot_refresh_relay_policy.json`
- `control/policies/snapshot_refresh_non_claim_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/snapshot_refresh_01_*.json`
- `docs/architecture/SNAPSHOT_REFRESH_01.md`
- `docs/architecture/SNAPSHOT_LIVE_METADATA_HANDOFFS.md`
- `docs/architecture/LIVE_METADATA_CANDIDATE_SNAPSHOT_SECTION.md`
- `docs/operations/SNAPSHOT_REFRESH_01_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_REFRESH_01_PLAN.md`
- `docs/reference/SNAPSHOT_LIVE_METADATA_SECTION.md`
- `control/audits/snapshot-refresh-01-v0/**`

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

- Add a live metadata candidate snapshot section.
- Keep reviewed records, seed candidates, and live metadata candidates separate.
- Build relay, public search view-model, and public alpha reassessment packets.
- Write inventory and audit evidence.
- Preserve all no-mutation and no-launch boundaries.

## VALIDATION

- `git diff --check`
- `python scripts/validate_snapshot_refresh.py`
- `python scripts/validate_live_metadata_pilot_batch.py`
- `python scripts/validate_public_search_ux_model.py`
- `python scripts/validate_public_alpha_reassess.py`
- seed, review, SCOUT, candidate, planner, relay, public-readonly, source validators
- focused snapshot refresh unittest modules
- AIDE Lite doctor, validate, test, selftest, verify, review-pack, and commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- Live metadata pilot output is integrated into snapshot refresh 01.
- Live metadata candidates are distinct from fixture candidates and reviewed records.
- Public search view-model projection marks live metadata results as candidates.
- Boundary reports keep all mutation, deployment, extraction, download, and readiness flags false.
- Focused validators and tests pass.

## OUTPUT_SCHEMA

Final report uses the user-requested SNAPSHOT_REFRESH_01 format with validation
and boundary summaries.

## TOKEN_ESTIMATE

medium

## EVIDENCE

- `examples/snapshots/refresh/live_metadata/`
- `control/inventory/snapshot_refresh_01_result.json`
- `control/audits/snapshot-refresh-01-v0/`

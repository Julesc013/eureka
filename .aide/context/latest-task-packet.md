# AIDE Latest Task Packet

## PHASE

SNAPSHOT-REFRESH-06 - refresh snapshots after review batch apply

## GOAL

Project the temp-only `REVIEW-BATCH-APPLY-NEXT-00` outputs into snapshot, relay,
public-search, and public-alpha reassessment handoffs without creating artifact,
download, safety, compatibility, OCR, rights, public index, deployment, or launch
claims.

## WHY

The reviewed-corpus loop produced limited reviewed metadata/source-lead records,
reviewed known needs, and reviewed bounded absences. Snapshot refresh packages
that evidence so the next product decision can reassess alpha usefulness without
treating limited records as verified artifacts.

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `614f5232 feat(review): apply next review batch`
- public launch: deferred
- snapshot refresh 05: pass
- review batch apply next: pass
- previous limited reviewed projection count: 4
- previous candidate count: 68

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/inventory/review_batch_apply_next_result.json`
- `control/inventory/snapshot_refresh_05_result.json`
- `control/inventory/public_search_ux_mvp_result.json`
- `examples/review_batch/apply_next/`
- `runtime/snapshots/refresh_06.py`
- `scripts/validate_snapshot_refresh.py`

## ALLOWED_PATHS

- `contracts/snapshot/**`
- `contracts/relay/**`
- `contracts/review/**`
- `contracts/view/models/public_search/**`
- `runtime/snapshots/**`
- `runtime/relay/**`
- `runtime/public_search/**`
- `scripts/eureka_snapshot_refresh.py`
- `scripts/eureka_snapshot_refresh_report.py`
- `scripts/validate_snapshot_refresh.py`
- `tests/runtime/test_snapshot_refresh*.py`
- `tests/operations/test_snapshot_refresh_scripts.py`
- `tests/scripts/test_validate_snapshot_refresh.py`
- `examples/snapshots/refresh/review_batch_apply/**`
- `examples/relay/refresh/review_batch_apply_refreshed_relay_projection.json`
- `examples/public_alpha/reassess/review_batch_apply/**`
- `control/policies/snapshot_refresh*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/snapshot_refresh_06*.json`
- `control/audits/snapshot-refresh-06-v0/**`
- `docs/architecture/SNAPSHOT_REFRESH_06.md`
- `docs/architecture/SNAPSHOT_REVIEW_BATCH_APPLY_PROJECTION.md`
- `docs/architecture/SNAPSHOT_LIMITED_REVIEWED_RECORDS.md`
- `docs/architecture/SNAPSHOT_REVIEWED_NEEDS_ABSENCES.md`
- `docs/operations/SNAPSHOT_REFRESH_06_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_REFRESH_06_PLAN.md`
- `docs/reference/SNAPSHOT_REVIEW_BATCH_APPLY_SECTION.md`
- `docs/reference/SNAPSHOT_LIMITED_REVIEWED_RECORD_SECTION.md`
- `docs/reference/SNAPSHOT_REVIEWED_NEED_ABSENCE_SECTION.md`
- `.aide/queue/SNAPSHOT-REFRESH-06/**`
- `.aide/queue/PUBLIC-ALPHA-REASSESS-06/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `../instances/**`
- `.aide.local/**`
- `../eureka-test-runs/**`
- `secrets/**`
- `.env`
- raw live source responses
- raw IA responses
- raw full-discovery stdout/stderr logs
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## NON_GOALS

- No deployment, publishing, public launch, or readiness claim.
- No operator instance mutation.
- No reviewed/master/public index mutation.
- No artifact verification, verified download, malware-clean, rights-clearance,
  compatibility guarantee, scan-completeness, or OCR-quality claim.
- No live source calls, file fetches, OCR, extraction, execution, install,
  model/provider calls, source probes, or full unittest discovery.

## IMPLEMENTATION

- Add snapshot refresh 06 contracts and policies.
- Add runtime and CLI over deterministic examples only.
- Project 4 new limited metadata records and 4 new source leads.
- Project 2 reviewed known needs and 2 reviewed bounded absences.
- Project 60 remaining review-only candidates.
- Produce result-card, no-results, relay, public-alpha handoff, inventory, and
  audit evidence.

## VALIDATION

- `git diff --check`
- `python scripts/validate_snapshot_refresh.py`
- existing review-batch apply, public-alpha, UX MVP/model, readonly, relay,
  architecture, and generated-artifact validators
- focused `tests.runtime.test_snapshot_refresh*` modules for refresh 06
- focused operations/script validator tests
- AIDE doctor/validate/test/selftest/verify/review-pack/commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- `previous_total_limited_reviewed_record_projection_count`: 4
- `new_limited_reviewed_metadata_records`: 4
- `new_limited_reviewed_source_leads`: 4
- `new_reviewed_record_delta_count`: 8
- `total_limited_reviewed_record_projection_count`: 12
- `reviewed_known_need_count`: 2
- `reviewed_bounded_absence_count`: 2
- `previous_total_candidate_count`: 68
- `candidate_count_after_apply`: 60
- all boundary flags remain false

## EVIDENCE

- `control/inventory/snapshot_refresh_06_result.json`
- `control/inventory/snapshot_refresh_06_validation_matrix.json`
- `control/audits/snapshot-refresh-06-v0/`
- `examples/snapshots/refresh/review_batch_apply/`
- `.aide/queue/SNAPSHOT-REFRESH-06/README.md`

## OUTPUT_SCHEMA

Final response follows the task prompt shape:

- `STATUS`
- `SUMMARY`
- `SNAPSHOT_REFRESH_06`
- `VALIDATION`
- `BOUNDARIES`
- `NEXT_TASK`

## TOKEN_ESTIMATE

- method: compact manual task packet
- approx_tokens: under 1800
- budget_status: PASS
- full_discovery: NOT_RUN_BY_POLICY

## NEXT

`PUBLIC-ALPHA-REASSESS-06 - Reassess alpha after review batch apply snapshot refresh`

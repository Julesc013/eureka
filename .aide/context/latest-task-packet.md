# AIDE Latest Task Packet

## PHASE

REVIEW-BATCH-APPLY-NEXT-00 - apply next eligible review batches to grow reviewed corpus

## GOAL

Apply the next conservative set of eligible review-batch outputs through a temp
explicit local-apply proof, producing limited reviewed records, reviewed known
needs, and reviewed bounded absences without public/master/operator mutation or
artifact/download/safety/rights claims.

## WHY

Public alpha remains launch-deferred because reviewed corpus depth is still too
low. Candidate discovery and the no-JS public search UX are now useful enough
that the next product improvement is governed reviewed-corpus growth.

## CURRENT_STATE

- branch: `dev`
- latest prior commit: `54be6850 feat(task): reassess alpha after UX MVP`
- public launch: deferred
- public alpha reassess 05: pass
- candidate count: 68
- limited reviewed projection count before this task: 4
- public search UX MVP: implemented, no-JS, read-only
- recommended task before this packet: `REVIEW-BATCH-APPLY-NEXT-00`

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_reassess_05_result.json`
- `control/inventory/snapshot_refresh_05_result.json`
- `control/inventory/public_search_ux_mvp_result.json`
- `examples/seed_batches/*/review_batch_packet.json`
- `examples/review/live_metadata/review_packet.json`
- `runtime/local_apply/review_batch_apply_next.py`
- `scripts/validate_review_batch_apply_next.py`

## ALLOWED_PATHS

- `contracts/review/**`
- `contracts/local_apply/**`
- `runtime/local_apply/**`
- `runtime/review/batch/**`
- `scripts/eureka_review_batch_apply_next.py`
- `scripts/eureka_review_batch_apply_report.py`
- `scripts/eureka_review_batch_apply_validate.py`
- `scripts/validate_review_batch_apply_next.py`
- `tests/runtime/test_review_batch_apply*.py`
- `tests/operations/test_review_batch_apply_next_scripts.py`
- `tests/scripts/test_validate_review_batch_apply_next.py`
- `examples/review_batch/apply_next/**`
- `examples/local_apply/review_batch/**`
- `control/policies/review_batch_apply*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/review_batch_apply_next*.json`
- `control/audits/review-batch-apply-next-00-v0/**`
- `docs/architecture/REVIEW_BATCH_APPLY*.md`
- `docs/architecture/LIMITED_REVIEWED_RECORD_MODEL.md`
- `docs/operations/REVIEW_BATCH_APPLY_NEXT_RUNBOOK.md`
- `docs/operations/POST_REVIEW_BATCH_APPLY_NEXT_PLAN.md`
- `docs/reference/REVIEW_BATCH_APPLY*.md`
- `docs/reference/LIMITED_REVIEWED_RECORD.md`
- `.aide/queue/REVIEW-BATCH-APPLY-NEXT-00/**`
- `.aide/queue/SNAPSHOT-REFRESH-06/**`
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

- Add review-batch apply contracts and policies.
- Add runtime and CLI over deterministic examples only.
- Apply 8 candidate-derived limited reviewed records in temp proof.
- Apply 2 reviewed known needs and 2 reviewed bounded absences in temp proof.
- Produce non-applied candidate report for the remaining 60 candidates.
- Produce snapshot and public-alpha handoffs.
- Produce inventory and audit evidence.

## VALIDATION

- `git diff --check`
- `python scripts/validate_review_batch_apply_next.py`
- existing public-alpha, snapshot, UX MVP, review-batch, candidate-index, SCOUT,
  query-planner, architecture, and generated-artifact validators
- focused `tests.runtime.test_review_batch_apply*`
- focused operations/script validator tests
- AIDE doctor/validate/test/selftest/verify/review-pack/commit check

Full unittest discovery is not run by policy.

## ACCEPTANCE

- `total_candidates_considered`: 68
- `eligible_apply_count`: 12
- `limited_reviewed_metadata_records_created`: 4
- `limited_reviewed_source_leads_created`: 4
- `reviewed_known_needs_created`: 2
- `reviewed_bounded_absences_created`: 2
- `reviewed_record_delta_count`: 8
- `non_applied_count`: 60
- temp instance apply passes
- rollback plan exists
- public launch remains deferred
- all boundary flags remain false

## EVIDENCE

- `control/inventory/review_batch_apply_next_result.json`
- `control/inventory/review_batch_apply_next_validation_matrix.json`
- `control/audits/review-batch-apply-next-00-v0/`
- `examples/review_batch/apply_next/`
- `.aide/queue/REVIEW-BATCH-APPLY-NEXT-00/README.md`

## OUTPUT_SCHEMA

Final response follows the task prompt shape:

- `STATUS`
- `SUMMARY`
- `REVIEW_BATCH_APPLY_NEXT`
- `VALIDATION`
- `BOUNDARIES`
- `NEXT_TASK`

## TOKEN_ESTIMATE

- method: compact manual task packet
- approx_tokens: under 1600
- budget_status: PASS
- full_discovery: NOT_RUN_BY_POLICY

## NEXT

`SNAPSHOT-REFRESH-06 - Refresh snapshots after review batch apply`

# AIDE Latest Task Packet

## PHASE

WORKBENCH-REVIEW-PROMOTE-01

## GOAL

Add the local/operator review and promotion-preview flow for candidates produced by existing local, IA-HUNT, IA live metadata lane mock/dry-run, and fixture/example pipelines.

## WHY

This batch proves the review gate between candidate material and reviewed local projection without creating automatic truth, mutating an operator instance, or touching master/public index artifacts.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/queue/AIDE-BATCH-WORKBENCH-REVIEW-PROMOTE-01/task.yaml`
- `control/inventory/workbench_review_promote_result.json`
- `control/audits/workbench-review-promote-01-v0/README.md`

## ALLOWED_PATHS

- `.aide/queue/AIDE-BATCH-WORKBENCH-REVIEW-PROMOTE-01/**`
- `.aide/queue/WORKBENCH-REVIEW-PROMOTE-01/**`
- `.aide/queue/LOCAL-APPLY-GATE-01/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/review/**`
- `contracts/candidates/**`
- `contracts/evidence/**`
- `contracts/public_index/**`
- `contracts/resolution_run/**`
- `contracts/search_interaction/**`
- `contracts/workbench/**`
- `contracts/view_models/**`
- `contracts/projections/**`
- `runtime/review_queue/**`
- `runtime/candidate_index/**`
- `runtime/candidate_store/**`
- `runtime/evidence_ledger/**`
- `runtime/public_index/**`
- `runtime/resolution_run/**`
- `runtime/local_service/**`
- `surfaces/web/workbench/local_html/**`
- `runtime/local_eval/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/source_cache/**`
- `surfaces/web/workbench/**`
- `surfaces/api/**`
- `surfaces/web/**`
- `scripts/eureka_workbench_review_promote.py`
- `scripts/eureka_review_queue.py`
- `scripts/eureka_workbench_live_run.py`
- `scripts/validate_workbench_review_promote.py`
- `scripts/validate_ia_live_metadata_lane.py`
- `scripts/validate_workbench_live_run.py`
- `scripts/validate_resolution_run_kernel.py`
- `scripts/eureka_test_select.py`
- `tests/runtime/test_workbench_review_promote.py`
- `tests/runtime/test_review_queue_flow.py`
- `tests/runtime/test_promotion_preview_flow.py`
- `tests/runtime/test_reviewed_index_refresh_flow.py`
- `tests/runtime/test_workbench_review_boundaries.py`
- `tests/operations/test_workbench_review_promote_scripts.py`
- `tests/operations/test_workbench_review_promote_smoke.py`
- `tests/scripts/test_validate_workbench_review_promote.py`
- `examples/workbench/review_promote/**`
- `examples/review_queue/**`
- `examples/promotion_preview/**`
- `examples/reviewed_index_refresh/**`
- `control/policies/workbench_review_promote_policy.json`
- `control/policies/review_queue_operator_policy.json`
- `control/policies/promotion_preview_policy.json`
- `control/policies/reviewed_index_refresh_policy.json`
- `control/policies/workbench_review_promote_non_claim_policy.json`
- `control/inventory/workbench_review_promote_*.json`
- `control/inventory/workbench_reviewed_index_refresh_matrix.json`
- `docs/architecture/WORKBENCH_REVIEW_PROMOTE.md`
- `docs/architecture/REVIEW_TO_PROMOTION_PREVIEW_MODEL.md`
- `docs/architecture/REVIEWED_LOCAL_INDEX_REFRESH.md`
- `docs/operations/WORKBENCH_REVIEW_PROMOTE_RUNBOOK.md`
- `docs/operations/POST_WORKBENCH_REVIEW_PROMOTE_PLAN.md`
- `docs/reference/WORKBENCH_REVIEW_PROMOTE_ROUTES.md`
- `docs/reference/WORKBENCH_REVIEW_PROMOTE_API.md`
- `control/audits/workbench-review-promote-01-v0/**`

## NON_GOALS

- No master/public index mutation.
- No operator instance mutation by default.
- No fake evidence or fake verified records.
- No live IA call, source probe, download, extraction, model/provider call, deployment, production readiness claim, or public launch claim.
- No Local Apply Gate yet.

## FORBIDDEN_PATHS

- `.git/**`
- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `site/dist/**`
- `site/dist/data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Keep runtime behavior in `runtime/local_service/workbench_review_promote.py`.
- Keep Workbench/API seams in `runtime/local_service/routes.py`.
- Keep policies, matrices, examples, docs, tests, and audit evidence in their governed task paths.
- Use temp instances only for refresh proof.

## VALIDATION

- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/validate_workbench_review_promote.py`
- focused Workbench review/promote unittest modules
- adjacent foundation validators
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- AIDE Lite doctor/validate/test/selftest/verify/review-pack
- `python -m unittest discover -s tests -t .`

## EVIDENCE

- `control/inventory/workbench_review_promote_result.json`
- `control/inventory/workbench_review_promote_validation_matrix.json`
- `control/audits/workbench-review-promote-01-v0/**`
- final commit and validation output

## ACCEPTANCE

- Candidate can become a review item.
- Operator token is required for recorded decisions.
- Public/native projections are read-only.
- Accepted local review creates a promotion preview.
- Explicit temp-instance refresh proof updates a temp reviewed local index and search result.
- Boundaries remain false.

## NEXT

LOCAL-APPLY-GATE-01 — Explicit operator-instance apply, backup, audit, and rollback gate.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `WORKBENCH_REVIEW_PROMOTE`, `VALIDATION`, `PUSH`, `BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS

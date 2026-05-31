# AIDE Latest Task Packet

## PHASE

SNAPSHOT-REFRESH-00

## GOAL

Refresh reviewed/candidate snapshot projection material from completed
frontier-media and legacy-software seed-batch handoffs without converting
candidates into reviewed truth.

## WHY

Public-alpha reassessment needs compact, public-safe snapshot material that
separates reviewed records, review-only candidates, unresolved needs, bounded
absences, and review queue summaries.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `control/inventory/seed_batch_frontier_media_result.json`
- `control/inventory/seed_batch_legacy_software_result.json`
- `control/inventory/snapshot_refresh_result.json`
- `control/audits/snapshot-refresh-00-v0/`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`

## ALLOWED_PATHS

- `.aide/queue/SNAPSHOT-REFRESH-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/snapshot/**`
- `runtime/snapshots/**`
- `scripts/eureka_snapshot_refresh.py`
- `scripts/eureka_snapshot_refresh_report.py`
- `scripts/validate_snapshot_refresh.py`
- `tests/runtime/test_snapshot_refresh*.py`
- `tests/operations/test_snapshot_refresh_scripts.py`
- `tests/scripts/test_validate_snapshot_refresh.py`
- `examples/snapshots/refresh/**`
- `examples/relay/refresh/**`
- `examples/public_alpha/reassess/**`
- `control/policies/snapshot_refresh*.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/snapshot_refresh*.json`
- `control/audits/snapshot-refresh-00-v0/**`
- `docs/architecture/SNAPSHOT_REFRESH.md`
- `docs/architecture/SNAPSHOT_SEED_BATCH_HANDOFFS.md`
- `docs/architecture/CANDIDATE_SNAPSHOT_SECTION.md`
- `docs/operations/SNAPSHOT_REFRESH_RUNBOOK.md`
- `docs/operations/POST_SNAPSHOT_REFRESH_PLAN.md`
- `docs/reference/SNAPSHOT_REFRESH_PLAN.md`
- `docs/reference/SNAPSHOT_CANDIDATE_SECTION.md`
- `docs/reference/SNAPSHOT_NEED_ABSENCE_SECTION.md`

## FORBIDDEN_PATHS

- deployment output roots
- public index roots
- local instance roots
- private AIDE local-state roots
- secret and environment files
- raw live source responses
- provider credentials
- private local files

## IMPLEMENTATION

- Added snapshot refresh runtime projection helpers.
- Added CLI, report CLI, validator, contracts, policies, examples, docs,
  inventory packets, audit evidence, and focused tests.
- Updated the queue handoff to `PUBLIC-ALPHA-REASSESS-00`.

## VALIDATION

- `python scripts/validate_snapshot_refresh.py`
- existing seed, review, SCOUT, candidate, query planner, snapshot relay,
  public alpha read-only, source-action, and source-wave validators
- focused snapshot refresh unittest modules
- AIDE Lite doctor/validate/test/selftest/verify/review-pack

## COMMITS

Commit as `feat(snapshot): refresh seed batch snapshots` after focused
validation passes.

## EVIDENCE

- `control/inventory/snapshot_refresh_result.json`
- `control/inventory/snapshot_refresh_validation_matrix.json`
- `control/audits/snapshot-refresh-00-v0/`
- `examples/snapshots/refresh/`

## NON_GOALS

No deployment, public launch, production-readiness claim, public-launch claim,
candidate acceptance, reviewed/master/public index mutation, operator instance
mutation, deployment-output write, live source call, source probe, broad crawl,
download, extraction, execution, install, model/provider call, or full unittest
discovery inside this AI session.

## ACCEPTANCE

- Candidate sections exist and keep `accepted_truth: false`.
- Reviewed record section uses existing reviewed records only.
- Need/absence and review queue sections are projected.
- Relay projection is read-only.
- Public alpha reassess input exists.
- Boundary flags remain false.
- Focused validators and tests pass.

## OUTPUT_SCHEMA

Return a compact final report with STATUS, SUMMARY, SNAPSHOT_REFRESH,
VALIDATION, BOUNDARIES, and NEXT_TASK.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- budget_status: PASS
- warnings:
  - none

## NEXT

`PUBLIC-ALPHA-REASSESS-00`

# Latest Task Packet

## PHASE

PLAY-02 — Demo Query / Absence / Hunt Smoke Pack is the current recommended
next task. PLAY-01 completed as PASS.

## GOAL

Use the PLAY-01 operator play-session proof as the starting point for the next
local-only demo query, absence, and Hunt smoke pack.

## WHY

PLAY-01 made the PLAY-00 seed corpus repeatable through a dry-run-default
operator command, explicit apply mode, smoke reporting, validator coverage,
docs, inventories, and audit evidence.

## CONTEXT_REFS

- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/play_01_result.json`
- `control/inventory/play_01_next_task_decision.json`
- `control/audits/play-01-operator-play-session-v0/play_01_report.json`
- `docs/operations/PLAY_SESSION_RUNBOOK.md`

## ALLOWED_PATHS

- `examples/play/**`
- `docs/operations/PLAY_MODE_RUNBOOK.md`
- `docs/operations/LOCAL_WORKBENCH_DEMO_QUERIES.md`
- `docs/operations/PLAY_SEED_CORPUS_POLICY.md`
- `docs/operations/PLAY_SESSION_RUNBOOK.md`
- `scripts/eureka_play_session.py`
- `scripts/eureka_play_smoke.py`
- `scripts/eureka_seed_play_demo.py`
- `scripts/validate_play_session.py`
- `scripts/validate_play_seed_pack.py`
- `tests/operations/test_play_session.py`
- `tests/operations/test_play_smoke.py`
- `tests/operations/test_play_session_report.py`
- `tests/runtime/test_play_seed_pack.py`
- `runtime/local_eval/**`
- `runtime/local_service/**`
- `runtime/local_workbench/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/public_index/**`
- `control/policies/play_seed_corpus_policy.json`
- `control/policies/play_session_policy.json`
- `control/inventory/play_01_input_state.json`
- `control/inventory/play_session_command_matrix.json`
- `control/inventory/play_session_result_schema.json`
- `control/inventory/play_session_smoke_matrix.json`
- `control/inventory/play_01_result.json`
- `control/inventory/play_01_next_task_decision.json`
- `.aide/queue/PLAY-01/task.yaml`
- `.aide/queue/PLAY-02/task.yaml`
- `.aide/queue/PLAY-02/**`
- `.aide/queue/IA-00/task.yaml`
- `.aide/queue/SYN-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/play-01-operator-play-session-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `private local files`
- `committed operator tokens`
- `committed provider credentials`
- `raw prompts`
- `raw responses`
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

PLAY-01 hardened `scripts/eureka_play_session.py`, hardened
`scripts/eureka_play_smoke.py`, added `scripts/validate_play_session.py`, and
recorded policy, command matrix, schema, smoke matrix, docs, tests, and audit
evidence.

## VALIDATION

Focused PLAY validators and tests passed. Architecture boundary checks passed.
Generated artifact cleanliness is expected to pass after the PLAY-01 commit
because the new audit pack is committed.

## EVIDENCE

- `control/inventory/play_01_result.json`
- `control/audits/play-01-operator-play-session-v0/`
- `.aide/queue/PLAY-01/task.yaml`
- `.aide/queue/PLAY-02/task.yaml`

## NON_GOALS

No live source calls, source probes, extraction, model/provider calls,
downloads, install/execute behavior, deployment, production readiness claim,
public launch readiness claim, or committed local instance state.

## ACCEPTANCE

PLAY-01 acceptance is recorded as pass in `control/inventory/play_01_result.json`.
PLAY-02 should preserve all PLAY boundaries.

## OUTPUT_SCHEMA

Use compact structured final reports with status, summary, validation, boundary
flags, commits, and next task.

## TOKEN_ESTIMATE

Compact packet under the normal AIDE token budget.

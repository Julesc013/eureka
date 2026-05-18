# Latest Task Packet

## PHASE

PLAY-02 — Demo Query / Absence / Hunt Smoke Pack completed as PASS.

## GOAL

Provide a compact repeatable smoke lane over the PLAY demo corpus and operator
session proof.

## WHY

PLAY-02 makes the PLAY demo loop cheap to rerun before SYN, IA, F0, workbench,
and source-pilot changes while preserving the no-live-source, no-extraction,
no-model-provider boundary.

## RESULT

PLAY-02 added:

- `control/policies/play_smoke_policy.json`
- query, route, and report-schema inventories
- hardened `scripts/eureka_play_smoke.py`
- `scripts/validate_play_smoke_pack.py`
- focused smoke-pack tests
- `docs/operations/PLAY_SMOKE_RUNBOOK.md`
- PLAY-02 result, next-task decision, and audit evidence

## CONTEXT_REFS

- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/play_02_result.json`
- `control/inventory/play_smoke_pack_result.json`
- `control/audits/play-02-demo-query-absence-hunt-smoke-v0/`
- `docs/operations/PLAY_SMOKE_RUNBOOK.md`
- `.aide/queue/PLAY-02/task.yaml`
- `.aide/queue/IA-00/task.yaml`

## ALLOWED_PATHS

- `examples/play/**`
- `docs/operations/PLAY_MODE_RUNBOOK.md`
- `docs/operations/PLAY_SESSION_RUNBOOK.md`
- `docs/operations/PLAY_SMOKE_RUNBOOK.md`
- `docs/operations/LOCAL_WORKBENCH_DEMO_QUERIES.md`
- `docs/operations/PLAY_SEED_CORPUS_POLICY.md`
- `scripts/eureka_play_smoke.py`
- `scripts/eureka_play_session.py`
- `scripts/eureka_seed_play_demo.py`
- `scripts/validate_play_seed_pack.py`
- `scripts/validate_play_session.py`
- `scripts/validate_play_smoke_pack.py`
- `tests/runtime/test_play_seed_pack.py`
- `tests/operations/test_play_session.py`
- `tests/operations/test_play_session_report.py`
- `tests/operations/test_play_smoke.py`
- `tests/operations/test_play_smoke_pack.py`
- `control/policies/play_smoke_policy.json`
- `control/inventory/play_02_*.json`
- `control/inventory/play_smoke_*.json`
- `.aide/queue/PLAY-02/task.yaml`
- `.aide/queue/IA-00/task.yaml`
- `.aide/queue/SYN-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/play-02-demo-query-absence-hunt-smoke-v0/**`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files
- committed operator tokens
- committed provider credentials
- raw prompts
- raw responses
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

PLAY-02 hardened `scripts/eureka_play_smoke.py` around temp-instance apply,
read-only operator-instance dry-run, optional localhost route checks, JSON and
Markdown report output, and explicit boundary flags. It added
`scripts/validate_play_smoke_pack.py`, policy and matrix inventories, runbook
coverage, focused tests, and audit evidence.

## VALIDATION

Required PLAY-02 focused validation is recorded in
`control/inventory/play_02_result.json` and the audit pack. Full discovery
remains optional for this focused smoke-pack task.

## EVIDENCE

- `control/policies/play_smoke_policy.json`
- `control/inventory/play_smoke_query_matrix.json`
- `control/inventory/play_smoke_route_matrix.json`
- `control/inventory/play_smoke_result_schema.json`
- `control/inventory/play_smoke_pack_result.json`
- `control/inventory/play_02_result.json`
- `control/audits/play-02-demo-query-absence-hunt-smoke-v0/`

## NON_GOALS

No live source calls, source probes, extraction, model/provider calls,
downloads, install/execute behavior, deployment, production readiness claim,
public launch readiness claim, or committed local instance state.

## ACCEPTANCE

PLAY-02 acceptance is recorded as pass in `control/inventory/play_02_result.json`.
The smoke pack proves known hit, known absence, media SearchNeed,
source/extraction SearchNeed, hard source-routing SearchNeed, compatibility
SearchNeed, visible demo Hunts/SearchNeeds/WorkUnits, and blocked
source/extraction/AI paths.

## OUTPUT_SCHEMA

Use compact structured final reports with status, summary, validation, boundary
flags, commits, and next task.

## TOKEN_ESTIMATE

Compact packet under the normal AIDE token budget.

## NEXT

Recommended next task:

IA-00 — Internet Archive Metadata Connector Approval Closure

Alternative:

SYN-00 — Synthetic Query Foundry planning over Local/HUNT/PLAY/IA

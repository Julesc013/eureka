# AIDE Latest Task Packet

phase: PLAY-01

## PHASE

PLAY-01

## GOAL

Refine the operator play-session script and workbench handoff after PLAY-00
added deterministic local demo data.

## WHY

PLAY-00 made the Local Appliance demonstrable with committed fixture-backed
demo records, demo Hunts, SearchNeeds, WorkUnits, and blocked future-action
examples. PLAY-01 should improve the operator-facing session loop without
opening live source calls, extraction, model/provider calls, downloads,
deployment, or public/production claims.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/PLAY-01/task.yaml`
- `examples/play`
- `examples/play/`
- `examples/play/**`
- `docs/operations/PLAY_MODE_RUNBOOK.md`
- `docs/operations/LOCAL_WORKBENCH_DEMO_QUERIES.md`
- `docs/operations/PLAY_SEED_CORPUS_POLICY.md`
- `control/inventory/play_00_result.json`
- `control/audits/play-00-local-workbench-seed-corpus-v0/`

## ALLOWED_PATHS

- `examples/play/`
- `runtime/local_appliance/**`
- `runtime/local_workbench/**`
- `runtime/local_service/**`
- `runtime/public_index/**`
- `runtime/search_hunt/**`
- `runtime/search_need/**`
- `runtime/workunit_queue/**`
- `runtime/local_worker/**`
- `runtime/local_eval/**`
- `scripts/eureka_seed_play_demo.py`
- `scripts/eureka_play_session.py`
- `scripts/eureka_play_smoke.py`
- `scripts/validate_play_seed_pack.py`
- `tests/runtime/test_play_seed_pack.py`
- `tests/operations/test_play_session.py`
- `tests/operations/test_play_smoke.py`
- `docs/operations/PLAY_MODE_RUNBOOK.md`
- `docs/operations/LOCAL_WORKBENCH_DEMO_QUERIES.md`
- `docs/operations/PLAY_SEED_CORPUS_POLICY.md`
- `control/policies/play_seed_corpus_policy.json`
- `control/inventory/play_00_input_state.json`
- `control/inventory/play_seed_corpus_inventory.json`
- `control/inventory/play_demo_query_matrix.json`
- `control/inventory/play_demo_hunt_matrix.json`
- `control/inventory/play_demo_workunit_matrix.json`
- `control/inventory/play_00_result.json`
- `control/inventory/play_00_next_task_decision.json`
- `.aide/queue/PLAY-00/task.yaml`
- `.aide/queue/PLAY-01`
- `.aide/queue/PLAY-01/task.yaml`
- `.aide/queue/IA-00`
- `.aide/queue/IA-00/task.yaml`
- `.aide/queue/SYN-00/task.yaml`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/audits/play-00-local-workbench-seed-corpus-v0`
- `control/audits/play-00-local-workbench-seed-corpus-v0/`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- `instances/**`
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

- Build on PLAY-00 fixtures and scripts.
- Keep the documented sibling default instance as the preferred local path.
- Keep the legacy sibling instance explicit-only.
- Do not run source probes, extraction, model/provider calls, downloads,
  installs, execution, deployment, or source sync.

## VALIDATION

- Use the PLAY-00 smoke/validator as the baseline unless a future PLAY-01
  prompt narrows or expands validation.

## EVIDENCE

- `.aide/queue/PLAY-01/`

## NON_GOALS

No live source calls, Internet Archive calls, source probes, extraction,
AI/model/provider calls, downloads, install/execute behavior, deployment,
public launch claim, production readiness claim, master-index mutation,
reviewed-index semantic mutation, operator instance move/delete, or committed
runtime instance state.

## ACCEPTANCE

- To be defined by a future PLAY-01 prompt.

## OUTPUT_SCHEMA

- To be defined by a future PLAY-01 prompt.

## TOKEN_ESTIMATE

approx_tokens: 650

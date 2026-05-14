# AIDE Latest Task Packet

## PHASE

HUNT-03 - Pause, resume, cancel, and steer commands

## GOAL

Add explicit Search Hunt command/state controls after HUNT-02 made Search Hunt Sessions visible in the Local Workbench.

## WHY

Search Hunt Sessions are now durable and inspectable. The next step is controlled local state transition behavior without creating WorkUnits, running source probes, or treating hunt state as evidence.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/queue/index.yaml`
- `.aide/queue/HUNT-03/task.yaml`
- `runtime/search_hunt/`
- `runtime/local_workbench/`
- `runtime/local_service/`
- `scripts/eureka_search_hunt.py`
- `scripts/eureka_search_hunt_ui_smoke.py`
- `scripts/validate_search_hunt_ui.py`
- `control/inventory/search_hunt_ui_result.json`
- `control/inventory/hunt_02_next_task_decision.json`
- `control/audits/hunt-02-search-hunt-ui-state-v0/`

## ALLOWED_PATHS

- HUNT-03 paths must be taken from a reviewed HUNT-03 task prompt.
- Search Hunt command/state changes may use `runtime/search_hunt/` only within the reviewed task scope.
- Local Workbench/service controls may be edited only if the reviewed task explicitly authorizes them.
- Control, docs, scripts, tests, queue metadata, and audit evidence may be used only within the reviewed task scope.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- private local files
- `runtime/connectors/**`
- `runtime/local_foundry/**`
- `runtime/extraction/**`
- `site/dist/**`
- source probes, WorkUnit creation, extraction, model/provider calls, deployment, production readiness claims, or public launch readiness claims unless a future reviewed task explicitly enables them

## IMPLEMENTATION

- Read HUNT-02 evidence and the HUNT-03 task file first.
- Preserve the Local Appliance explicit instance and Search Hunt store boundaries.
- Implement only reviewed command/state transition behavior.
- Keep hunts non-truth and do not mutate review queues, public indexes, master indexes, or generated site outputs.

## VALIDATION

- `python scripts/validate_search_hunt_ui.py`
- HUNT-03 focused tests when implemented
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/check_architecture_boundaries.py`
- `python -m unittest discover -s tests -t .`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py review-pack`

## COMMITS

- Commit coherent task outputs with a structured Markdown commit body.
- Do not merge or promote branches unless a future task explicitly asks for that.

## EVIDENCE

- HUNT-02 audit pack: `control/audits/hunt-02-search-hunt-ui-state-v0/`
- HUNT-02 UI policies under `control/policies/search_hunt_*_policy.json`
- HUNT-02 UI inventories under `control/inventory/search_hunt_ui_*`
- Queue state in `.aide/queue/index.yaml`

## NON_GOALS

- No WorkUnit creation from hunts
- No source probes
- No extraction runtime
- No SYN generation
- No F0 implementation
- No AI/model/provider calls
- No crawling, scraping, downloads, install, or execution
- No deployment
- No production readiness claim
- No public launch readiness claim

## ACCEPTANCE

- HUNT-03 remains bounded to explicit command/state controls.
- Existing HUNT-02 read-only UI and APIs continue to pass.
- No WorkUnits, source probes, model/provider calls, review/index mutation, deployment, or production/public launch claims are introduced.
- Queue and evidence clearly identify the next task after HUNT-03.

## OUTPUT_SCHEMA

Return a compact final report with:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `SEARCH_HUNT_COMMANDS`
- `BOUNDARIES`
- `VALIDATION`
- `NEXT_TASK`

## TOKEN_ESTIMATE

- latest_task_packet_chars: approximately 4300
- latest_task_packet_tokens: approximately 1000
- budget_status: within compact task packet budget

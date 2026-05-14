# AIDE Latest Task Packet

## PHASE

HUNT-04 - Hunt exhaustion report

## GOAL

Add structured Search Hunt exhaustion reports after HUNT-03 made local command and steering controls available.

## WHY

Search Hunt Sessions can now persist state, show state in the workbench, and accept operator-gated pause/resume/cancel/steer commands. The next step is a durable report that explains what was checked, what remained unchecked, why the hunt is exhausted or blocked, and what future work is still deferred.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/queue/index.yaml`
- `.aide/queue/HUNT-04/task.yaml`
- `runtime/search_hunt/`
- `runtime/local_workbench/`
- `runtime/local_service/`
- `scripts/eureka_search_hunt.py`
- `scripts/eureka_search_hunt_command.py`
- `scripts/validate_search_hunt_commands.py`
- `control/inventory/search_hunt_command_result.json`
- `control/inventory/hunt_03_next_task_decision.json`
- `control/audits/hunt-03-search-hunt-commands-v0/`

## ALLOWED_PATHS

- HUNT-04 paths must be taken from a future reviewed HUNT-04 task prompt.
- Search Hunt exhaustion report changes may use `runtime/search_hunt/` only within the reviewed task scope.
- Local Workbench/service report visibility may be edited only if the reviewed task explicitly authorizes them.
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

- Read HUNT-03 evidence and the HUNT-04 task file first.
- Preserve the Local Appliance explicit instance and Search Hunt store boundaries.
- Implement only reviewed exhaustion-report behavior.
- Keep hunts non-truth and do not mutate review queues, public indexes, master indexes, or generated site outputs.

## VALIDATION

- `python scripts/validate_search_hunt_commands.py`
- HUNT-04 focused tests when implemented
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/check_architecture_boundaries.py`
- `python -m unittest discover -s tests -t .`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py review-pack`

## COMMITS

- Commit coherent task outputs with a structured Markdown commit body.
- Do not merge or promote branches unless a future task explicitly asks for that.

## EVIDENCE

- HUNT-03 audit pack: `control/audits/hunt-03-search-hunt-commands-v0/`
- HUNT-03 command policies under `control/policies/search_hunt_*command*_policy.json`
- HUNT-03 command inventories under `control/inventory/search_hunt_command_*`
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

- HUNT-04 remains bounded to explicit exhaustion-report behavior.
- Existing HUNT-03 command controls continue to pass.
- No WorkUnits, source probes, model/provider calls, review/index mutation, deployment, or production/public launch claims are introduced.
- Queue and evidence clearly identify the next task after HUNT-04.

## OUTPUT_SCHEMA

Return a compact final report with:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `SEARCH_HUNT_EXHAUSTION`
- `BOUNDARIES`
- `VALIDATION`
- `NEXT_TASK`

## TOKEN_ESTIMATE

- latest_task_packet_chars: approximately 4100
- latest_task_packet_tokens: approximately 1025

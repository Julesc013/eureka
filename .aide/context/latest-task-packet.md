# AIDE Latest Task Packet

## PHASE

HUNT-05 - Hunt-to-SearchNeed pipeline

## GOAL

Prepare the next Search Hunt step after HUNT-04 exhaustion reports: durable SearchNeed generation from local/current-index exhaustion evidence.

## WHY

Search Hunt Sessions can now persist state, show workbench state, accept operator-gated commands and steering, and generate local exhaustion reports. The next task should convert those reports into durable SearchNeed records without creating WorkUnits yet unless a future reviewed HUNT-05 prompt explicitly enables it.

## CONTEXT_REFS

- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/queue/index.yaml`
- `.aide/queue/HUNT-05/task.yaml`
- `runtime/search_hunt/`
- `scripts/eureka_search_hunt_exhaustion.py`
- `scripts/validate_search_hunt_exhaustion.py`
- `control/inventory/search_hunt_exhaustion_result.json`
- `control/inventory/hunt_04_next_task_decision.json`
- `control/audits/hunt-04-hunt-exhaustion-report-v0/`

## ALLOWED_PATHS

- HUNT-05 paths must be taken from a future reviewed HUNT-05 task prompt.
- SearchNeed generation changes must preserve Local Appliance and Search Hunt boundaries.
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
- source probes, WorkUnit creation, extraction, model/provider calls, deployment, production readiness claims, or public launch readiness claims unless a future reviewed task explicitly enables them

## IMPLEMENTATION

- Read HUNT-04 evidence and the future HUNT-05 task file first.
- Use exhaustion reports as local explanation input.
- Do not infer truth from a hunt or exhaustion report.
- Keep SearchNeed records separate from WorkUnits until a future task explicitly connects them.

## VALIDATION

- `python scripts/validate_search_hunt_exhaustion.py`
- future HUNT-05 focused tests when implemented
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/check_architecture_boundaries.py`
- `python -m unittest discover -s tests -t .`

## COMMITS

- Commit coherent task outputs with a structured Markdown commit body.
- Do not merge or promote branches unless a future task explicitly asks for that.

## NON_GOALS

- No WorkUnit creation unless HUNT-05 explicitly scopes it
- No source probes
- No extraction runtime
- No SYN generation
- No F0 implementation
- No AI/model/provider calls
- No deployment
- No production readiness claim
- No public launch readiness claim

## ACCEPTANCE

- HUNT-05 remains bounded to SearchNeed behavior from explicit local Search Hunt evidence.
- HUNT-04 exhaustion reports remain valid and non-truth.
- Queue and evidence clearly identify the next task after HUNT-05.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, task-specific fields, `BOUNDARIES`, `VALIDATION`, and `NEXT_TASK`.

# AIDE Latest Task Packet

## PHASE

HUNT-02 - Search Hunt UI state in Local Workbench

## GOAL

Expose persisted Search Hunt Session state in the Local Workbench after HUNT-01 added the durable local runtime.

## WHY

Search Hunt Sessions are now stored in the explicit Local Appliance instance. The next proof should make those sessions inspectable through the existing local workbench without adding background execution or source probes.

## CONTEXT_REFS

- `runtime/search_hunt/`
- `scripts/eureka_search_hunt.py`
- `scripts/demo_search_hunt_session.py`
- `scripts/validate_search_hunt_runtime.py`
- `control/inventory/search_hunt_runtime_result.json`
- `control/inventory/hunt_01_next_task_decision.json`
- `control/audits/hunt-01-search-hunt-session-runtime-v0/`
- `.aide/queue/HUNT-02/task.yaml`

## ALLOWED_PATHS

- HUNT-02 paths must be taken from the future reviewed HUNT-02 prompt.
- Local Workbench/service changes may be edited only when that future prompt explicitly authorizes them.
- Control, docs, scripts, tests, and audit evidence may be used only within the reviewed task scope.

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- private local files
- source probes, extraction, model/provider calls, deployment, production readiness claims, or public launch readiness claims unless a future reviewed task explicitly enables them

## IMPLEMENTATION

- Read HUNT-01 evidence and the HUNT-02 task file first.
- Use the Local Appliance runtime composition boundary.
- Keep Search Hunt Sessions non-truth and read-only through workbench views unless a future task explicitly enables mutation.
- Do not bypass the Local Appliance with ad hoc stores or direct index mutation.

## VALIDATION

- `python scripts/validate_search_hunt_runtime.py`
- HUNT-02 focused tests when implemented
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest discover -s tests -t .`

## COMMITS

- Commit coherent task outputs with a structured Markdown commit body.
- Do not merge or promote branches unless a future task explicitly asks for that.

## EVIDENCE

- HUNT-01 audit pack: `control/audits/hunt-01-search-hunt-session-runtime-v0/`
- HUNT runtime policies under `control/policies/search_hunt_*_policy.json`
- HUNT runtime inventories under `control/inventory/search_hunt_*`
- Queue state in `.aide/queue/index.yaml`

## NON_GOALS

- No source probes
- No WorkUnit creation from hunts
- No extraction runtime
- No SYN generation
- No AI/model/provider calls
- No crawling, scraping, downloads, install, or execution
- No deployment
- No production readiness claim
- No public launch readiness claim

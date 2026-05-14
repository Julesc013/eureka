# AIDE Latest Task Packet

## PHASE

HUNT-01 - Search Hunt Session runtime

## GOAL

Begin from the HUNT-00 planning/control evidence and implement the first Search Hunt Session runtime only when a future HUNT-01 task explicitly scopes it.

## WHY

Search should become a governed investigation path when the reviewed local index is weak, absent, ambiguous, stale, or policy-blocked. HUNT-00 inserted the planning spine; HUNT-01 is the next runtime task.

## CONTEXT_REFS

- `control/inventory/search_hunt_track_plan.json`
- `control/inventory/search_hunt_readiness_matrix.json`
- `control/inventory/search_hunt_dependency_matrix.json`
- `control/inventory/search_hunt_local_appliance_dependency.json`
- `control/inventory/search_hunt_future_track_gate.json`
- `control/inventory/search_hunt_next_task_decision.json`
- `control/inventory/final_chat_alignment_packet.json`
- `.aide/queue/HUNT-01/task.yaml`

## ALLOWED_PATHS

- HUNT-01 paths must be taken from the future reviewed HUNT-01 prompt.
- Local Appliance runtime paths may be edited only when that future prompt explicitly authorizes them.
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

- Read HUNT-00 evidence and the HUNT-01 task file first.
- Use explicit local instance, runtime composition, WorkUnit queue, deterministic worker, review/evidence/index, workbench, and auto-test/search boundaries.
- Keep Search Hunt Session records non-truth until future review/evidence/index promotion paths accept them.
- Do not bypass the Local Appliance with ad hoc stores or direct index mutation.

## VALIDATION

- `python scripts/validate_search_hunt_track.py`
- HUNT-01 focused tests when implemented
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest discover -s tests -t .`

## COMMITS

- Commit coherent task outputs with a structured Markdown commit body.
- Do not merge or promote branches unless a future task explicitly asks for that.

## EVIDENCE

- HUNT-00 audit pack: `control/audits/hunt-00-search-hunt-track-v0/`
- HUNT policies under `control/policies/search_hunt_*.json`
- HUNT inventories under `control/inventory/search_hunt_*.json`
- Queue state in `.aide/queue/index.yaml`

## NON_GOALS

- No source probes
- No extraction runtime
- No SYN generation
- No AI/model/provider calls
- No crawling, scraping, downloads, install, or execution
- No deployment
- No production readiness claim
- No public launch readiness claim

## ACCEPTANCE

- HUNT-01 starts only after HUNT-00 passes.
- F0 remains resumable but not current unless explicitly chosen.
- SYN remains available as an alternative/follow-up.
- The Local Appliance remains the mandatory proof surface.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 650
- budget_status: PASS
- warnings:
  - none

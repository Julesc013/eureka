# AIDE Latest Task Packet

## PHASE

LOCAL-04 - Read-only localhost HTTP service over reviewed index

## GOAL

Add a read-only localhost HTTP service over the reviewed public index through the LOCAL-03 runtime composition boundary.

## WHY

LOCAL-03 completed the local appliance runtime composition boundary. The next local appliance step is a localhost-only read surface that uses `runtime/local_appliance` instead of opening store paths directly.

## CONTEXT_REFS

- `.aide/queue/index.yaml`
- `LOCAL-02 completed with instance configuration, schema, and migration guard`
- `.aide/queue/LOCAL-03/task.yaml`
- `.aide/queue/LOCAL-04/task.yaml`
- `runtime/local_appliance/`
- `docs/architecture/LOCAL_RUNTIME_COMPOSITION_BOUNDARY.md`
- `docs/reference/LOCAL_APPLIANCE_RUNTIME_API.md`
- `docs/operations/LOCAL_RUNTIME_COMPOSITION.md`
- `control/inventory/local_03_next_task_decision.json`
- `AGENTS.md`

## IMPLEMENTATION

- Start from `dev` or an explicit LOCAL-04 task branch from `dev`.
- Use `open_local_appliance(instance_path, read_only=True)` for local store access.
- Keep HTTP localhost-only and read-only.
- Do not implement the HTML workbench.
- Do not expose LAN.
- Do not deploy.
- Do not add write routes, source probes, index rebuilds, production readiness claims, or public launch claims.

## VALIDATION

- `git status --short`
- `git diff --check`
- LOCAL-04 focused validator and tests when defined
- `python scripts/validate_local_runtime_composition.py`
- `python scripts/check_architecture_boundaries.py`

## EVIDENCE

- changed files
- validation commands and results
- unresolved risks and deferrals

## NON_GOALS

- No HTML workbench implementation.
- No WorkUnit runtime implementation.
- No LAN binding.
- No deployment.
- No source probe execution.
- No index rebuild behavior.
- No production readiness claim.
- No public launch readiness claim.

## ACCEPTANCE

- LOCAL-04 acceptance criteria are met.
- Service code uses the LOCAL-03 runtime composition boundary.
- F0 remains deferred until LOCAL-14.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

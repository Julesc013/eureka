# Next Task Handoff

## Recommended Task

Title: `LOCAL-04 - Read-only localhost HTTP service over reviewed index`

Packet path: `.aide/context/latest-task-packet.md`

## Objective

Add a read-only localhost HTTP service over the reviewed public index through
the LOCAL-03 `runtime/local/appliance` composition boundary.

## Why This Task

The Eureka queue currently recommends LOCAL-04 after LOCAL-03 completed the
runtime composition boundary. LOCAL-04 is the next small product-facing step in
the local appliance track and remains bounded by localhost-only, read-only, and
no-deployment gates.

## Current Preflight Blocker

`py -3 scripts/validate_local_runtime_composition.py` currently fails because
the fresh runtime leakage scan exceeds the older LOCAL-03 baseline. The LOCAL-04
packet records this directly. LOCAL-04 should not be accepted until the leakage
drift is reconciled or explicitly reviewed and accepted.

## Context Refs

- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- `.aide/queue/LOCAL-03/task.yaml`
- `.aide/queue/LOCAL-04/task.yaml`
- `.aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/validation.md`
- `.aide/queue/EUREKA-AIDE-HANDOVER-01/evidence/quality-readiness.md`
- `runtime/local/appliance/`
- `docs/architecture/LOCAL_RUNTIME_COMPOSITION_BOUNDARY.md`
- `docs/reference/LOCAL_APPLIANCE_RUNTIME_API.md`
- `docs/operations/LOCAL_RUNTIME_COMPOSITION.md`
- `control/inventory/local_03_next_task_decision.json`

## Allowed Paths

See `.aide/context/latest-task-packet.md`. The packet allows the LOCAL-04 queue
packet, generated AIDE context, `runtime/local/appliance/**`, explicitly scoped
localhost-only service module paths, focused validators/tests, LOCAL-04 docs,
and LOCAL-04 control/audit evidence.

## Forbidden Paths

See `.aide/context/latest-task-packet.md`. The packet forbids secrets,
`.aide.local/**`, broad product areas outside the LOCAL-04 boundary, write
routes, source probes, index rebuilds, WorkUnit runtime, HTML workbench, LAN
binding, deployment, provider/model calls, and production/public launch claims.

## Validation Commands

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py index`
- `py -3 .aide/scripts/aide_lite.py context`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py route explain`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 scripts/check_architecture_boundaries.py`
- `py -3 scripts/validate_local_runtime_composition.py`
- LOCAL-04 focused validator and tests when defined
- `git diff --check`

## Acceptance Criteria

- LOCAL-03 runtime composition validation is passing again, or remaining
  leakage drift is separately reviewed and explicitly accepted.
- LOCAL-04 acceptance criteria are met.
- Service code uses the LOCAL-03 runtime composition boundary.
- HTTP service is localhost-only and read-only.
- No write routes, source probes, index rebuilds, HTML workbench, LAN,
  deployment, production readiness claim, or public launch claim are added.
- Validation and evidence are recorded.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are
  committed.

## Review Packet Guidance

GPT-5.5 or Codex review should use `.aide/context/latest-review-packet.md` and
Q26 evidence only. Do not paste long repo history or the entire source tree.

## Token Estimate

- Latest task packet: 6157 chars / 1540 approximate tokens.
- Method: `chars / 4`.
- Budget status: within budget.

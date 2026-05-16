# AIDE Latest Task Packet

phase: HUNT-PERFECT-CLOSEOUT-01

## PHASE

HUNT-PERFECT-CLOSEOUT-01

## GOAL

Final zero-blocker Search Hunt closeout under the updated AIDE baseline.

## WHY

Search Hunt closeout needs a compact AIDE handoff packet that points to repo-local evidence without redefining Eureka product behavior.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/queue/index.yaml`
- `.aide/reports/eureka-repo-health.json`
- `control/inventory/hunt_perfect_closeout_result.json`
- `control/inventory/hunt_perfect_validation_matrix.json`
- `control/audits/hunt-perfect-closeout-01-v0/`

## ALLOWED_PATHS

- `.aide/**`
- `control/inventory/**`
- `control/audits/**`
- `docs/operations/**`

## FORBIDDEN_PATHS

- `runtime/**`
- `contracts/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `examples/**`
- `evals/**`
- `tests/**`
- `scripts/**`
- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `.local/**`
- `.cache/**`
- `eureka-instance/**`
- raw prompts/responses/provider credentials

## IMPLEMENTATION

- Read final HUNT/AIDE/LOCAL evidence from committed control-plane records.
- Write compact closeout, warning, blocker, handoff, and queue evidence under `.aide/queue/` and `control/`.
- Do not change Eureka product behavior.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`
- HUNT validators
- LOCAL validators
- integrated HUNT smoke
- full unittest discovery
- generated artifact cleanliness
- runtime leakage

## EVIDENCE

- `.aide/queue/HUNT-PERFECT-CLOSEOUT-01/evidence/`
- `control/inventory/hunt_perfect_closeout_result.json`
- `control/inventory/hunt_perfect_validation_matrix.json`
- `control/audits/hunt-perfect-closeout-01-v0/`

## NON_GOALS

No SYN/F0 implementation, source probes, extraction, model/provider calls, downloads/install/execution, deployment, main promotion, production readiness claim, public launch readiness claim, or Eureka product behavior change.

## ACCEPTANCE

- HUNT closeout status is pass with zero warnings and zero hard blockers.
- AIDE eval remains green.
- Full unittest discovery passes.
- No forbidden HUNT boundary is crossed.

## OUTPUT_SCHEMA

- `control/inventory/hunt_perfect_closeout_result.json` uses `hunt_perfect_closeout_result.v0`.
- `control/inventory/hunt_perfect_next_task_decision.json` uses `hunt_perfect_next_task_decision.v0`.

## TOKEN_ESTIMATE

approx_tokens: 900

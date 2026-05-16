# AIDE Latest Task Packet

phase: HUNT-TO-MAIN-PROMOTION-REVIEW

## PHASE

HUNT-TO-MAIN-PROMOTION-REVIEW

## GOAL

Fast-forward the perfected Search Hunt baseline from dev to main only after promotion gates pass.

## WHY

Search Hunt is ready to become canonical repo truth while preserving no-production, no-provider, and no-live-source boundaries.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `control/inventory/hunt_main_promotion_result.json`
- `control/audits/hunt-to-main-promotion-review-v0/`

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

- Record promotion gates and branch plan in control-plane evidence.
- Use fast-forward-only branch mutation after validation.
- Do not change Eureka product behavior.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`
- `python scripts/check_architecture_boundaries.py`
- HUNT validators, LOCAL validators, full unittest discovery, generated cleanliness, runtime leakage, and report-size validator.

## EVIDENCE

- `.aide/queue/HUNT-TO-MAIN-PROMOTION-REVIEW/`
- `control/inventory/hunt_main_promotion_result.json`
- `control/audits/hunt-to-main-promotion-review-v0/`

## NON_GOALS

No SYN/F0 implementation, source probes, extraction, model/provider calls, downloads/install/execution, deployment, force push, history rewrite, production readiness claim, public launch readiness claim, or Eureka product behavior change.

## ACCEPTANCE

- Promotion gates pass.
- dev and main are aligned by fast-forward only.
- No forbidden HUNT boundary is crossed.

## OUTPUT_SCHEMA

- `control/inventory/hunt_main_promotion_result.json` uses `hunt_main_promotion_result.v0`.
- `control/inventory/hunt_main_next_task_decision.json` uses `hunt_main_next_task_decision.v0`.

## TOKEN_ESTIMATE

approx_tokens: 900

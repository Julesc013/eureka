# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-HOSTING-READINESS-00

## GOAL

Define hosting, security, operations, privacy, abuse, takedown, rollback, and
launch-gate readiness for the read-only public alpha without deploying or
claiming launch readiness.

## WHY

Public alpha routes exist on `dev`, but a route foundation is not a launch
foundation. This task records the hosting, security, ops, and non-claim gates
needed before any future launch-candidate review.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/PUBLIC-ALPHA-HOSTING-READINESS-00/task.yaml`
- `.aide/queue/PUBLIC-ALPHA-READONLY-CLOSEOUT-01/task.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_readonly_00_result.json`
- `control/inventory/public_alpha_hosting_result.json`
- `control/inventory/snapshot_relay_result.json`
- `docs/architecture/PUBLIC_ALPHA_HOSTING.md`
- `docs/architecture/PUBLIC_ALPHA_SECURITY_MODEL.md`
- `docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md`

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-HOSTING-READINESS-00/**`
- `.aide/queue/PUBLIC-ALPHA-READONLY-CLOSEOUT-01/**`
- `.aide/queue/DEV-TO-MAIN-PROMOTION-REVIEW-04/**`
- `.aide/queue/PUBLIC-ALPHA-LAUNCH-CANDIDATE-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/publication/**`
- `control/policies/public_alpha_*.json`
- `control/inventory/public_alpha_hosting_*.json`
- `control/audits/public-alpha-hosting-readiness-00-v0/**`
- `docs/architecture/PUBLIC_ALPHA_HOSTING.md`
- `docs/architecture/PUBLIC_ALPHA_SECURITY_MODEL.md`
- `docs/operations/PUBLIC_ALPHA_HOSTING_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_ROLLBACK_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_ABUSE_AND_TAKEDOWN.md`
- `docs/operations/POST_PUBLIC_ALPHA_HOSTING_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_ENVIRONMENT.md`
- `docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md`
- `scripts/validate_public_alpha_hosting_readiness.py`
- `tests/operations/test_public_alpha_hosting_readiness.py`
- `tests/scripts/test_validate_public_alpha_hosting_readiness.py`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `eureka-instance/**`
- `instances/**`
- `../eureka-test-runs/**`
- `site/dist/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`
- raw provider credentials, API keys, local caches, raw prompt logs, raw
  responses, raw full-discovery logs, and operator instance state

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_hosting_readiness.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/validate_source_wave.py`
- `python scripts/validate_source_action_kernel.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest tests.operations.test_public_alpha_hosting_readiness`
- `python -m unittest tests.scripts.test_validate_public_alpha_hosting_readiness`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`

## IMPLEMENTATION

- Keep all changes inside the allowed readiness, policy, docs, inventory, audit,
  validator, test, and AIDE queue/context paths.
- Treat this as planning and validation evidence only.
- Preserve public alpha read-only behavior; do not add runtime mutation,
  deployment, live source fanout, downloads, extraction, or model/provider calls.
- Prefer compact structured evidence over raw logs.

## EVIDENCE

- Hosting contracts under `contracts/publication/`.
- Control policies under `control/policies/public_alpha_*`.
- Readiness matrices under `control/inventory/public_alpha_hosting_*`.
- Docs under `docs/architecture/`, `docs/operations/`, and `docs/reference/`.
- Audit pack under `control/audits/public-alpha-hosting-readiness-00-v0/`.
- Validator and focused tests under `scripts/` and `tests/`.

## NON_GOALS

- No deployment.
- No public launch claim.
- No production readiness claim.
- No live source fanout.
- No public mutation.
- No downloads, uploads, or extraction.
- No model/provider calls.
- No public/master index mutation.
- No committed instance state.
- No full unittest discovery inside the AI session.

## ACCEPTANCE

- Hosting contracts, policies, matrices, docs, audit pack, validator, and
  focused tests exist.
- Launch gates require future explicit approval and external full discovery.
- Boundaries remain false.
- Recommended next task is `PUBLIC-ALPHA-READONLY-CLOSEOUT-01`.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `PUBLIC_ALPHA_HOSTING`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 6200
- approx_tokens: 1550
- budget_status: PASS
- warnings:
  - none

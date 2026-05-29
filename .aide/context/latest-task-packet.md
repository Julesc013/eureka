# AIDE Latest Task Packet

## PHASE

DEV-TO-MAIN-PROMOTION-REVIEW-05

## GOAL

Promote the public alpha launch-candidate and deploy dry-run evidence from
`dev` to `main` only after a current external full-discovery run passes. The
current state is waiting for that external gate.

## WHY

`PUBLIC-ALPHA-DEPLOY-DRY-RUN-00` passed on `dev`, but promotion policy requires
external full discovery before fast-forwarding `main`. This task records the
handoff and blocks promotion until the compact external result is returned.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/DEV-TO-MAIN-PROMOTION-REVIEW-05/task.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_deploy_dry_run_result.json`
- `control/inventory/public_alpha_launch_candidate_result.json`
- `control/inventory/dev_to_main_promotion_05_result.json`
- `control/inventory/dev_to_main_promotion_05_full_discovery_handoff.json`
- `control/audits/dev-to-main-promotion-review-05-v0/`

## ALLOWED_PATHS

- `.aide/queue/DEV-TO-MAIN-PROMOTION-REVIEW-05/**`
- `.aide/queue/PUBLIC-ALPHA-LAUNCH-00/**`
- `.aide/queue/PUBLIC-DEMAND-SIGNAL-00/**`
- `.aide/queue/PUBLIC-SOURCE-REQUEST-QUEUE-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/inventory/dev_to_main_promotion_05_*.json`
- `control/audits/dev-to-main-promotion-review-05-v0/**`
- `docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_05.md`
- `docs/operations/POST_PUBLIC_ALPHA_DEPLOY_DRY_RUN_PROMOTION_PLAN.md`
- `scripts/validate_dev_to_main_promotion_05.py`
- `tools/validators/validate_dev_to_main_promotion_05.py`
- `tests/operations/test_dev_to_main_promotion_05.py`
- `tests/scripts/test_validate_dev_to_main_promotion_05.py`
- `control/policies/generated_artifact_policy.json`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `eureka-instance/**`
- `instances/**`
- `../eureka-test-runs/**`
- static distribution output roots
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`
- raw live source responses, raw full-discovery logs, operator tokens, provider
  credentials, and committed local instance state

## VALIDATION

- `git diff --check`
- `python scripts/validate_dev_to_main_promotion_05.py`
- `python scripts/validate_public_alpha_deploy_dry_run.py`
- `python scripts/validate_public_alpha_launch_candidate.py`
- `python scripts/validate_public_alpha_readonly_closeout.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_public_alpha_hosting_readiness.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/validate_source_wave.py`
- `python scripts/validate_source_action_kernel.py`
- `python scripts/validate_test_run_summary.py --help`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest tests.operations.test_dev_to_main_promotion_05`
- `python -m unittest tests.scripts.test_validate_dev_to_main_promotion_05`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`

## IMPLEMENTATION

- Record promotion-05 branch, scope, validation, boundary, and waiting
  full-discovery handoff evidence.
- Verify deploy dry-run and launch-candidate evidence remains safe.
- Do not fast-forward `main` until a current external full-discovery pass is
  returned.

## EVIDENCE

- `control/inventory/dev_to_main_promotion_05_*.json`
- `control/audits/dev-to-main-promotion-review-05-v0/`
- `docs/operations/DEV_TO_MAIN_PROMOTION_REVIEW_05.md`
- focused promotion validator and tests

## NON_GOALS

No deployment, publication, DNS change, production readiness claim, public
launch readiness claim, live source fanout, public mutation, accounts,
downloads, uploads, extraction, model/provider calls, native work, marketplace
work, or full discovery inside the AI session.

## ACCEPTANCE

- Promotion-05 validator and tests pass in waiting state.
- External full-discovery handoff exists.
- `main` is not promoted while waiting.
- Next action is external full discovery.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `VALIDATION`, `BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 6500
- approx_tokens: 1625
- budget_status: PASS

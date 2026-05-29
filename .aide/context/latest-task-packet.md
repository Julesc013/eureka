# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-DEPLOY-DRY-RUN-00

## GOAL

Rehearse deployment mechanics for the read-only public alpha without deploying,
publishing, writing the static distribution output root, changing DNS, mutating indexes, calling live
sources/providers, or claiming production/public launch readiness.

## WHY

`PUBLIC-ALPHA-LAUNCH-CANDIDATE-00` passed and produced a go-to-dry-run
decision. The dry-run gate verifies the deploy manifest, environment checklist,
smoke checklist, rollback rehearsal, and no-deploy boundaries before promotion
and any future explicit launch task.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/PUBLIC-ALPHA-DEPLOY-DRY-RUN-00/task.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_launch_candidate_result.json`
- `control/inventory/public_alpha_deploy_dry_run_result.json`
- `control/audits/public-alpha-deploy-dry-run-00-v0/`

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-DEPLOY-DRY-RUN-00/**`
- `.aide/queue/DEV-TO-MAIN-PROMOTION-REVIEW-05/**`
- `.aide/queue/PUBLIC-ALPHA-LAUNCH-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `contracts/publication/public_alpha_deploy_dry_run.v0.json`
- `contracts/publication/public_alpha_deploy_manifest.v0.json`
- `contracts/publication/public_alpha_environment_checklist.v0.json`
- `contracts/publication/public_alpha_smoke_check.v0.json`
- `contracts/publication/public_alpha_rollback_rehearsal.v0.json`
- `contracts/publication/public_alpha_deploy_dry_run_gate.v0.json`
- `control/policies/public_alpha_deploy_dry_run_policy.json`
- `control/policies/public_alpha_dry_run_no_deploy_policy.json`
- `control/policies/public_alpha_deploy_smoke_policy.json`
- `control/policies/public_alpha_rollback_rehearsal_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_deploy_dry_run_*.json`
- `control/audits/public-alpha-deploy-dry-run-00-v0/**`
- `docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_DEPLOY_MANIFEST.md`
- `docs/operations/PUBLIC_ALPHA_DEPLOY_SMOKE_CHECKS.md`
- `docs/operations/PUBLIC_ALPHA_DEPLOY_ROLLBACK_REHEARSAL.md`
- `docs/operations/POST_PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_DEPLOY_DRY_RUN_GATES.md`
- `release/hosting/public_alpha_deploy_dry_run_report.md`
- `release/hosting/public_alpha_dry_run_smoke_checklist.md`
- `release/hosting/public_alpha_dry_run_rollback_rehearsal.md`
- `release/hosting/public_alpha_dry_run_environment.md`
- `scripts/validate_public_alpha_deploy_dry_run.py`
- `tools/validators/validate_public_alpha_deploy_dry_run.py`
- `tests/operations/test_public_alpha_deploy_dry_run.py`
- `tests/scripts/test_validate_public_alpha_deploy_dry_run.py`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `eureka-instance/**`
- `instances/**`
- `../eureka-test-runs/**`
- `static distribution output root`
- `static public-index output root`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`
- raw live source responses, raw full-discovery logs, operator tokens, provider
  credentials, and committed local instance state

## VALIDATION

- `git diff --check`
- `python scripts/validate_public_alpha_deploy_dry_run.py`
- `python scripts/validate_public_alpha_launch_candidate.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_public_alpha_hosting_readiness.py`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest tests.operations.test_public_alpha_deploy_dry_run`
- `python -m unittest tests.scripts.test_validate_public_alpha_deploy_dry_run`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`

## IMPLEMENTATION

- Record dry-run contracts, policies, manifest, environment checklist, smoke
  checklist, rollback rehearsal, boundary report, validator, and tests.
- Keep deployment, launch, DNS changes, the static distribution output root writes, index mutation, live
  source fanout, public mutation, downloads, extraction, and model calls
  disabled.
- Recommend `DEV-TO-MAIN-PROMOTION-REVIEW-05` before any explicit launch task.

## EVIDENCE

- `control/inventory/public_alpha_deploy_dry_run_*.json`
- `control/audits/public-alpha-deploy-dry-run-00-v0/`
- `docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_RUNBOOK.md`
- focused dry-run validator and tests

## NON_GOALS

No deployment, publication, DNS change, production readiness claim, public
launch readiness claim, live source fanout, public mutation, accounts,
downloads, uploads, extraction, model/provider calls, native work, marketplace
work, or full discovery inside the AI session.

## ACCEPTANCE

- Dry-run validator and tests pass.
- Deploy manifest, environment checklist, smoke checklist, and rollback
  rehearsal are present and pass.
- Deployment and public launch remain false.
- Next recommended task is `DEV-TO-MAIN-PROMOTION-REVIEW-05`.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `PUBLIC_ALPHA_DEPLOY_DRY_RUN`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 7200
- approx_tokens: 1800
- budget_status: PASS

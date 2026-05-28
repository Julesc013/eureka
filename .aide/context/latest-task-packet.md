# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-LAUNCH-CANDIDATE-00

## GOAL

Package the promoted read-only public alpha baseline as a launch candidate for a
future deploy dry run. This task is not a deployment, not a public launch, and
not a production or public launch readiness claim.

## WHY

`DEV-TO-MAIN-PROMOTION-REVIEW-04` promoted the public alpha read-only baseline
to `main`. The launch-candidate gate records the go/no-go decision, blocker
register, deploy dry-run plan, manual approval gate, and safety boundaries
before any deploy rehearsal can begin.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/PUBLIC-ALPHA-LAUNCH-CANDIDATE-00/task.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/dev_to_main_promotion_04_result.json`
- `control/inventory/public_alpha_readonly_closeout_result.json`
- `control/inventory/public_alpha_readonly_00_result.json`
- `control/inventory/public_alpha_hosting_result.json`
- `control/inventory/public_alpha_launch_candidate_result.json`
- `control/audits/public-alpha-launch-candidate-00-v0/`

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-LAUNCH-CANDIDATE-00/**`
- `.aide/queue/PUBLIC-ALPHA-DEPLOY-DRY-RUN-00/**`
- `.aide/queue/PUBLIC-ALPHA-LAUNCH-00/**`
- `.aide/queue/PUBLIC-DEMAND-SIGNAL-00/**`
- `.aide/queue/PUBLIC-SOURCE-REQUEST-QUEUE-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `contracts/publication/public_alpha_launch_candidate.v0.json`
- `contracts/publication/public_alpha_launch_gate.v0.json`
- `contracts/publication/public_alpha_launch_decision.v0.json`
- `contracts/publication/public_alpha_deploy_dry_run_plan.v0.json`
- `contracts/publication/public_alpha_blocker_register.v0.json`
- `contracts/publication/public_alpha_go_no_go.v0.json`
- `control/policies/public_alpha_launch_candidate_policy.json`
- `control/policies/public_alpha_no_deploy_policy.json`
- `control/policies/public_alpha_manual_approval_policy.json`
- `control/policies/public_alpha_launch_non_claim_policy.json`
- `control/policies/public_alpha_public_safety_policy.json`
- `control/policies/generated_artifact_policy.json`
- `control/inventory/public_alpha_launch_candidate_*.json`
- `control/audits/public-alpha-launch-candidate-00-v0/**`
- `docs/architecture/PUBLIC_ALPHA_LAUNCH_CANDIDATE.md`
- `docs/operations/PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_GO_NO_GO_CHECKLIST.md`
- `docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md`
- `docs/operations/PUBLIC_ALPHA_MANUAL_APPROVAL_GATE.md`
- `docs/operations/POST_PUBLIC_ALPHA_LAUNCH_CANDIDATE_PLAN.md`
- `docs/reference/PUBLIC_ALPHA_LAUNCH_GATES.md`
- `docs/reference/PUBLIC_ALPHA_BLOCKER_REGISTER.md`
- `release/hosting/public_alpha_launch_candidate.md`
- `release/hosting/public_alpha_deploy_dry_run_plan.md`
- `release/hosting/public_alpha_rollback_checklist.md`
- `release/hosting/public_alpha_environment_checklist.md`
- `scripts/validate_public_alpha_launch_candidate.py`
- `tools/validators/validate_public_alpha_launch_candidate.py`
- `tests/operations/test_public_alpha_launch_candidate.py`
- `tests/scripts/test_validate_public_alpha_launch_candidate.py`

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- `eureka-instance/**`
- `instances/**`
- `../eureka-test-runs/**`
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`
- raw live source responses, raw full-discovery logs, operator tokens, provider
  credentials, and committed local instance state

## VALIDATION

- `git diff --check`
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
- `python -m unittest tests.operations.test_public_alpha_launch_candidate`
- `python -m unittest tests.scripts.test_validate_public_alpha_launch_candidate`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`

## IMPLEMENTATION

- Record launch-candidate contracts, policies, matrices, and audit evidence.
- Validate prior promotion, public alpha read-only, hosting readiness, closeout,
  snapshot relay, source wave, source action, and CI harness evidence.
- Keep deployment, production readiness, public launch readiness, live source
  fanout, mutation, downloads, extraction, and model/provider calls disabled.
- Recommend only `PUBLIC-ALPHA-DEPLOY-DRY-RUN-00` as the next task.

## EVIDENCE

- `control/inventory/public_alpha_launch_candidate_*.json`
- `control/audits/public-alpha-launch-candidate-00-v0/`
- `docs/operations/PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md`
- `docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md`
- focused launch-candidate validator and tests

## NON_GOALS

No deployment, publication, production readiness claim, public launch readiness
claim, live source fanout, public mutation, accounts, downloads, uploads,
extraction, model/provider calls, native work, marketplace work, or full
discovery inside the AI session.

## ACCEPTANCE

- Launch-candidate validator and tests pass.
- Hard blockers and launch warnings are zero.
- Manual approval remains required before any deployment or launch.
- Next recommended task is `PUBLIC-ALPHA-DEPLOY-DRY-RUN-00`.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `PUBLIC_ALPHA_LAUNCH_CANDIDATE`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 7200
- approx_tokens: 1800
- budget_status: PASS

# AIDE Latest Task Packet

## PHASE

PUBLIC-ALPHA-READONLY-CLOSEOUT-01

## GOAL

Close the public read-only alpha route foundation and hosting-readiness baseline
before promotion. This task is a validation closeout and external full-discovery
handoff, not a launch or deployment task.

## WHY

Public alpha routes and hosting readiness are implemented on `dev`. Promotion to
main requires a compact closeout record and a full-discovery run outside the AI
session before `DEV-TO-MAIN-PROMOTION-REVIEW-04`.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/index.yaml`
- `.aide/queue/PUBLIC-ALPHA-READONLY-CLOSEOUT-01/task.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/public_alpha_readonly_00_result.json`
- `control/inventory/public_alpha_hosting_result.json`
- `control/inventory/public_alpha_readonly_closeout_result.json`
- `control/inventory/public_alpha_readonly_closeout_full_discovery_handoff.json`
- `control/audits/public-alpha-readonly-closeout-01-v0/`

## ALLOWED_PATHS

- `.aide/queue/PUBLIC-ALPHA-READONLY-CLOSEOUT-01/**`
- `.aide/queue/DEV-TO-MAIN-PROMOTION-REVIEW-04/**`
- `.aide/queue/PUBLIC-ALPHA-LAUNCH-CANDIDATE-00/**`
- `.aide/queue/PUBLIC-DEMAND-SIGNAL-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/inventory/public_alpha_readonly_closeout_*.json`
- `control/audits/public-alpha-readonly-closeout-01-v0/**`
- `docs/operations/PUBLIC_ALPHA_READONLY_CLOSEOUT.md`
- `docs/operations/POST_PUBLIC_ALPHA_READONLY_CLOSEOUT_PLAN.md`
- `scripts/validate_public_alpha_readonly_closeout.py`
- `tests/operations/test_public_alpha_readonly_closeout.py`
- `tests/scripts/test_validate_public_alpha_readonly_closeout.py`

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
- `python scripts/validate_public_alpha_readonly_closeout.py`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_public_alpha_hosting_readiness.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/validate_source_wave.py`
- `python scripts/validate_source_action_kernel.py`
- `python scripts/validate_test_run_summary.py --help`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python -m unittest tests.operations.test_public_alpha_readonly_closeout`
- `python -m unittest tests.scripts.test_validate_public_alpha_readonly_closeout`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`

## IMPLEMENTATION

- Record closeout matrices for route/API/hosting/security/boundaries.
- Verify prior public alpha read-only, hosting, snapshot relay, source wave,
  source action, source snapshot closeout, and CI full-discovery harness results.
- Create an external full-discovery handoff for the current dev head.
- Keep promotion readiness false until a compact external full-discovery summary
  is returned and validated.

## EVIDENCE

- `control/inventory/public_alpha_readonly_closeout_*.json`
- `control/audits/public-alpha-readonly-closeout-01-v0/`
- `docs/operations/PUBLIC_ALPHA_READONLY_CLOSEOUT.md`
- `docs/operations/POST_PUBLIC_ALPHA_READONLY_CLOSEOUT_PLAN.md`
- focused validator and tests

## NON_GOALS

- No deployment, publication, production readiness claim, public launch readiness
  claim, live source fanout, public mutation, accounts, downloads, uploads,
  extraction, model/provider calls, native work, marketplace work, or full
  discovery inside the AI session.

## ACCEPTANCE

- Focused closeout validator and tests pass.
- External full-discovery handoff exists.
- Status is `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`.
- `DEV-TO-MAIN-PROMOTION-REVIEW-04` remains blocked until full discovery passes.

## OUTPUT_SCHEMA

Return `STATUS`, `SUMMARY`, `PUBLIC_ALPHA_CLOSEOUT`, `VALIDATION`,
`BOUNDARIES`, and `NEXT_TASK`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 5800
- approx_tokens: 1450
- budget_status: PASS

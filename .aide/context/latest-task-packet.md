# AIDE Latest Task Packet

## PHASE

SYNC-BASELINE-01 - Canonical branch baseline

## GOAL

Create a canonical local/remote `main` baseline after OBS, Track B, repo sync
recovery, and SYNC-GUARD-01.

## WHY

The repo now has the guard rails needed for multi-machine work. This baseline
records that the current branches have been merged or classified, full tests
pass on `main`, and every other checkout has a simple resync path.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `control/audits/sync-baseline-01-canonical-main-v0/`
- `control/audits/sync-guard-01-multi-machine-git-guard-v0/`
- `docs/operations/MULTI_MACHINE_GIT_WORKFLOW.md`
- `scripts/check_git_task_state.py`

## IMPLEMENTATION

- Merge `origin/task/sync-guard-01` into `main`.
- Inventory local and remote branches.
- Run generated artifact drift checks, architecture checks, guard tests, full
  unittest discovery, and AIDE Lite checks.
- Add canonical baseline audit evidence.
- Push `main` normally.
- Provide resync instructions for all other machines and checkouts.

## VALIDATION

- `git status --short`
- `git diff --check`
- conflict marker scan
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_drift.py --json`
- `python scripts/validate_sync_guard_policy.py`
- `python -m unittest tests.operations.test_git_task_state_guard tests.operations.test_sync_guard_policy`
- `python -m unittest discover -s tests -t .`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- `control/audits/sync-baseline-01-canonical-main-v0/README.md`
- `control/audits/sync-baseline-01-canonical-main-v0/baseline_report.json`
- `control/audits/sync-baseline-01-canonical-main-v0/branch_inventory.md`
- `control/audits/sync-baseline-01-canonical-main-v0/merged_branch_report.md`
- `control/audits/sync-baseline-01-canonical-main-v0/validation_matrix.md`
- `control/audits/sync-baseline-01-canonical-main-v0/test_report.md`
- `control/audits/sync-baseline-01-canonical-main-v0/aide_state_report.md`
- `control/audits/sync-baseline-01-canonical-main-v0/resync_instructions.md`
- `control/audits/sync-baseline-01-canonical-main-v0/next_steps.md`
- `.aide/queue/` is not used for task evidence; SYNC-BASELINE-01 evidence lives under `control/audits/`.

## ALLOWED_PATHS

- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `control/audits/sync-baseline-01-canonical-main-v0/**`

## FORBIDDEN_PATHS

- runtime/**
- contracts/**
- surfaces/**
- site/**
- native/**
- crates/**
- connectors/**
- packaging/**
- third_party/**
- source/evidence/master-index records
- generated static artifacts
- ignored private local roots
- secrets or credential paths

## NON_GOALS

- Do not force push.
- Do not delete branches.
- Do not rewrite history.
- Complete this baseline without changing Eureka product behavior.
- Do not approve source access, execute WorkUnits, create public truth, enable
  connectors, or mutate the master index.

## ACCEPTANCE

- `main` contains OBS, Track B, repo sync evidence, and SYNC-GUARD-01.
- Full tests pass on `main`.
- AIDE Lite checks pass or warn with zero errors.
- Baseline audit pack exists.
- `origin/main` receives the final baseline commit by normal push.
- Resync instructions exist for all machines.

## OUTPUT_SCHEMA

Return the final response with:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `BRANCHES`
- `VALIDATION`
- `PUSH`
- `RESYNC`
- `RISKS`
- `NEXT`

## TOKEN_ESTIMATE

approx_tokens: 1200

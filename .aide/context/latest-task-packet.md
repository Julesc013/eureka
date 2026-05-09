# AIDE Latest Task Packet

## PHASE

SYNC-GUARD-01 - Multi-machine Git discipline and AIDE sync guard

## GOAL

Add a compact Git/AIDE sync guard that prevents future Codex/AIDE work from
starting in dirty, stale, interrupted, or direct-main task states.

## WHY

The OBS and Track B merge recovery succeeded, but it exposed a workflow hazard:
parallel machine work, stale local `main`, active merge metadata, and unpushed
local-only task work can make normal convergence far too difficult. The remedy
is a small guard and three simple workflow prompts, not more nested sync audits.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/memory/project-state.md`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-context-packet.md`
- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/reports/eureka-aide-lite-operating-handoff.md`
- `docs/operations/MULTI_MACHINE_GIT_WORKFLOW.md`
- `docs/operations/AIDE_SYNC_GUARD.md`
- `docs/operations/AIDE_SYNC_RECOVERY_COMMANDS.md`
- `control/inventory/git/sync_guard_policy.json`
- `control/inventory/git/task_branch_policy.json`
- `control/inventory/git/sync_workflow_commands.json`
- `scripts/check_git_task_state.py`
- `scripts/validate_sync_guard_policy.py`
- `tests/operations/test_git_task_state_guard.py`
- `tests/operations/test_sync_guard_policy.py`

## IMPLEMENTATION

- Add Git sync guard policies under `control/inventory/git/`.
- Add non-mutating guard and validator scripts under `scripts/`.
- Add AIDE prompt templates for sync, merge, and rescue workflows.
- Add multi-machine workflow and recovery docs.
- Add temp-repo tests for guard behavior.
- Add a SYNC-GUARD-01 audit pack.
- Add a compact AGENTS.md rule requiring the guard before normal task work.

## VALIDATION

- `git status --short`
- `git diff --check`
- `python -m json.tool control/inventory/git/sync_guard_policy.json`
- `python -m json.tool control/inventory/git/task_branch_policy.json`
- `python -m json.tool control/inventory/git/sync_workflow_commands.json`
- `python -m json.tool control/audits/sync-guard-01-multi-machine-git-guard-v0/sync_guard_01_report.json`
- `python scripts/check_git_task_state.py --mode start-task --task-id SYNC-GUARD-01 --allow-main`
- `python scripts/check_git_task_state.py --mode start-task --task-id SYNC-GUARD-01 --allow-main --json`
- `python scripts/validate_sync_guard_policy.py`
- `python -m unittest tests.operations.test_git_task_state_guard tests.operations.test_sync_guard_policy`
- `python scripts/check_architecture_boundaries.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py verify`

## EVIDENCE

- `control/audits/sync-guard-01-multi-machine-git-guard-v0/README.md`
- `control/audits/sync-guard-01-multi-machine-git-guard-v0/sync_guard_01_report.json`
- `control/audits/sync-guard-01-multi-machine-git-guard-v0/validation.md`
- `control/audits/sync-guard-01-multi-machine-git-guard-v0/workflow_summary.md`
- `.aide/queue/` is not used for task evidence; SYNC-GUARD-01 evidence lives under `control/audits/`.

## ALLOWED_PATHS

- `AGENTS.md`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/prompts/AIDE-SYNC-01.md`
- `.aide/prompts/AIDE-MERGE-01.md`
- `.aide/prompts/AIDE-RESCUE-01.md`
- `docs/operations/MULTI_MACHINE_GIT_WORKFLOW.md`
- `docs/operations/AIDE_SYNC_GUARD.md`
- `docs/operations/AIDE_SYNC_RECOVERY_COMMANDS.md`
- `control/inventory/git/sync_guard_policy.json`
- `control/inventory/git/task_branch_policy.json`
- `control/inventory/git/sync_workflow_commands.json`
- `scripts/check_git_task_state.py`
- `scripts/validate_sync_guard_policy.py`
- `tests/operations/test_git_task_state_guard.py`
- `tests/operations/test_sync_guard_policy.py`
- `control/audits/sync-guard-01-multi-machine-git-guard-v0/**`

## FORBIDDEN_PATHS

- product runtime behavior paths unless required for tests
- runtime/**
- contracts/**
- surfaces/**
- site/**
- native/**
- crates/**
- connectors/**
- packaging/**
- third_party/**
- public route behavior
- source/evidence/master-index records
- generated static artifacts
- ignored private local roots
- secrets or credential paths

## NON_GOALS

- Do not change Eureka product behavior.
- Do not enable hosting, live probes, source connectors, downloads, uploads,
  accounts, telemetry, WorkUnit execution, source approval, evidence truth, or
  master-index mutation.
- Do not create/delete Git branches from the guard script.
- Do not fetch, merge, push, reset, clean, stash, or rebase from the guard.

## NEXT

HUMAN-OBS-REVIEW-01 - Review OBS candidate packet

## ACCEPTANCE

- Sync guard policy, branch policy, and workflow command inventory exist.
- Guard and policy validator scripts exist and run.
- AIDE-SYNC-01, AIDE-MERGE-01, and AIDE-RESCUE-01 prompts exist.
- Multi-machine workflow docs exist.
- Guard tests and policy tests pass.
- No Eureka product behavior changes.
- Working tree is clean after commit.

## OUTPUT_SCHEMA

Return the final response with:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `CHANGED`
- `VALIDATION`
- `GUARD`
- `RISKS`
- `NEXT`

## TOKEN_ESTIMATE

approx_tokens: 1400

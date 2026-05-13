# Q32 Changed Files

## Queue And Evidence

- `.aide/queue/EUREKA-AIDE-SYNC-01/**`
- `.aide/queue/index.yaml`

## Canonical Governance Sync

- `.aide/scripts/aide_lite.py`
- `.aide/scripts/tests/test_export_import.py`
- `.aide/scripts/tests/test_q27_commit_recovery.py`
- `.aide/scripts/tests/test_q28_git_workflow.py`
- `.aide/scripts/tests/test_q29_git_helper.py`
- `.aide/scripts/tests/test_q31_export_pack_governance.py`
- `.aide/policies/commit-messages.yaml`
- `.aide/policies/task-resumption.yaml`
- `.aide/policies/work-units.yaml`
- `.aide/policies/recovery.yaml`
- `.aide/policies/git-workflow.yaml`
- `.aide/policies/branch-roles.yaml`
- `.aide/policies/promotion-rules.yaml`
- `.aide/policies/sync-policy.yaml`
- `.aide/policies/prune-policy.yaml`
- `.aide/policies/export-import.yaml`
- `.aide/hooks/commit-msg`
- `.aide/git/commit-template.md`
- `.aide/git/helper-policy.yaml`
- `.aide/git/helper-commands.md`
- `.aide/git/project-profiles.yaml`
- `.aide/git/README.md`

## Golden Tasks And Reports

- `.aide/evals/golden-tasks/**`
- `.aide/evals/runs/latest-golden-tasks.json`
- `.aide/evals/runs/latest-golden-tasks.md`
- `.aide/reports/aide-commit-message-standard.md`
- `.aide/reports/aide-task-resumption-standard.md`
- `.aide/reports/aide-workunit-recovery-standard.md`
- `.aide/reports/token-ledger.jsonl`
- `.aide/reports/token-savings-summary.md`

## Target-Local Generated State

- `.aide/context/repo-snapshot.json`
- `.aide/context/repo-map.json`
- `.aide/context/repo-map.md`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/verification/latest-verification-report.md`
- `.aide/git/workflow-detection.json`
- `.aide/git/workflow-detection.md`
- `.aide/git/latest-helper-plan.json`
- `.aide/git/latest-helper-plan.md`
- `.aide/changelog/**`

## Documentation And Guidance

- `AGENTS.md`
- `README.md`
- `docs/reference/aide-handover.md`
- `docs/reference/aide-governance-sync.md`
- portable AIDE reference docs under `docs/reference/**`

## Safety Boundary

No Eureka product source paths were changed. `.aide/memory/**`, existing
Eureka queue history, target evidence, and target-specific golden tasks were
preserved.

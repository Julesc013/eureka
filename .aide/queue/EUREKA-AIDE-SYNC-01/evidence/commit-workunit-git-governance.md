# Q32 Commit, WorkUnit, And Git Governance

## Commit Discipline

- Policy: `.aide/policies/commit-messages.yaml`
- Standard report: `.aide/reports/aide-commit-message-standard.md`
- Commit template: `.aide/git/commit-template.md`
- Hook template: `.aide/hooks/commit-msg`
- Checker: `py -3 .aide/scripts/aide_lite.py commit check`
- Latest structured commit check: PASS.
- Hook status: template imported only; not installed into `.git/hooks`.
- Changelog preview: available; WARN only because older commits in the preview
  range predate Q27/Q32 structured bodies.

## Task And WorkUnit Recovery

- Task resumption policy: `.aide/policies/task-resumption.yaml`
- WorkUnit policy: `.aide/policies/work-units.yaml`
- Recovery policy: `.aide/policies/recovery.yaml`
- Commands available: `task inspect`, `task status`, `task noop-check`,
  `task dependencies`, `task recover`, `task evidence`, `task current`.
- `task inspect --task-id EUREKA-AIDE-SYNC-01`: PASS after final status
  update; reports complete with `noop_already_complete`.
- `task noop-check --task-id EUREKA-AIDE-SYNC-01`: PASS; reports
  `noop_already_complete`.

## Git Workflow Governance

- Workflow policy: `.aide/policies/git-workflow.yaml`
- Branch roles: `.aide/policies/branch-roles.yaml`
- Promotion rules: `.aide/policies/promotion-rules.yaml`
- Sync policy: `.aide/policies/sync-policy.yaml`
- Prune policy: `.aide/policies/prune-policy.yaml`
- Helper policy/docs: `.aide/git/helper-policy.yaml`,
  `.aide/git/helper-commands.md`
- Project profiles: `.aide/git/project-profiles.yaml`
- Detection report: `.aide/git/workflow-detection.json`
- Latest helper plan: `.aide/git/latest-helper-plan.json`

## Git Command Result

- `git detect`: PASS; detected `trunk_with_dev_integration`, current branch
  `dev`, role `integration`, canonical `main`.
- `git policy`: PASS.
- `git plan`: blocked by dirty-tree safety gate while final Q32 evidence is
  present; non-mutating.
- `git sync --dry-run`: blocked by dirty tree; no sync applied.
- `git land --dry-run --target dev`: blocked because current branch is
  integration `dev`, not a task branch.
- `git promote --dry-run --from dev --to main`: blocked by dirty tree.
- `git prune --dry-run`: ready dry-run; `main` protected and current `dev`
  not eligible.

## Manual Content Preservation

`AGENTS.md` kept Eureka manual doctrine and product-boundary law. Only managed
AIDE guidance was refreshed. No hook was auto-installed and no branch was
created, merged, promoted, pushed, or pruned.

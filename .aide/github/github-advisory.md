# AIDE GitHub Protection And CI Advisory

- schema_version: aide.github-advisory.v0
- generated_by: aide-lite
- repo_id: Julesc013/eureka
- current_branch: dev
- current_commit: 6f2698c6e109a3b35d20402bb9871c1e4a674688
- current_branch_role: integration
- advisory_mode: report_only
- github_api_mutation: false
- branch_protection_applied: false
- workflow_file_written: false
- workflow_installation: false
- release_publishing: false
- tag_creation: false
- branch_mutation: false
- network_calls: false
- provider_or_model_calls: false

## Policies

- `.aide/policies/github-protection.yaml`
- `.aide/policies/ci-gates.yaml`
- `.aide/policies/branch-protection.yaml`

## Reports

- `.aide/github/github-advisory.json`
- `.aide/github/github-advisory.md`
- `.aide/github/branch-protection-plan.json`
- `.aide/github/branch-protection-plan.md`
- `.aide/github/ci-advisory.json`
- `.aide/github/ci-advisory.md`
- `.aide/github/latest-github-status.md`

## Findings

- none

## Recommended Next Action

- review Q35 advisory before any future Q36+ intent work; do not apply GitHub settings until a later reviewed phase

## Boundary

This report is advisory only. It compiles repo-local branch, commit, changelog,
pack, and validation gates into a future GitHub/CI plan without applying any
GitHub settings or workflow files.

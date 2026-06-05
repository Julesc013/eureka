# Full Discovery Summary Intake Protocol

When an operator returns `full_unittest_summary.json`, inspect only compact
summary artifacts unless targeted traceback excerpts are needed.

## Accept

Accept the summary only if:

- `schema_version` is `full_unittest_summary.v0`.
- `git.branch` is `dev`.
- `git.head` equals the operator checkout `HEAD` used for
  `EXTERNAL-FULL-DISCOVERY-RUN-01`.
- `git.working_tree_clean` is `true`.
- `generated_by` is the repo harness or approved CI workflow.

## Green Path

If `status` is `pass`, `exit_code` is `0`, and failures/errors are zero:

- mark full discovery current;
- keep corpus gate separately blocked until reviewed corpus thresholds pass;
- do not launch without manual approval;
- reassess the next release gate.

## Red Path

If the summary is red, classify current failure families from the returned
`failure_families.json` and choose one targeted repair task. Do not repair
historical families based only on stale reports.

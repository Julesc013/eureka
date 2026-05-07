# History Compliance

The user correctly identified that recent commits after the first governance
commit did not comply with the structured Markdown commit-message standard.

## Published History Status

`main` was aligned with `origin/main` when this audit ran, so the noncompliant
commits were treated as published history. AIDE does not silently rewrite
published history.

## Detected Noncompliant Commits

Command:

```text
py -3 .aide/scripts/aide_lite.py commit check --range 88d437f..HEAD
```

Result before this remediation commit: FAIL.

- `78efd5c` `contracts(representation): add host and representation profiles`
  - Subject failed the strict `type(scope): summary` parser because
    `contracts` is not an allowed commit type.
  - Body did not use the required Markdown headings.
- `b3d25ec` `contracts(representation): add semantic renderer parity policy`
  - Subject failed the strict `type(scope): summary` parser because
    `contracts` is not an allowed commit type.
  - Body was missing.

## Remediation

- Added `commit check --range` so AIDE can audit commit history ranges.
- Added `commit install-hook` and installed it locally with
  `core.hooksPath=.aide/hooks`.
- Updated `.aide/hooks/commit-msg` so future local commits run the checker
  before Git accepts the commit message.

## Rewrite Decision

The existing noncompliant published commits were not rewritten. Rewriting them
would require an explicit operator decision and a force-push workflow.

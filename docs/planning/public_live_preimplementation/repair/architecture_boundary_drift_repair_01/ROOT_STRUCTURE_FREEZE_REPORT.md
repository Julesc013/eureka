# Root Structure Freeze Report

## Status

`PRESERVED`

## Root Model

No new top-level roots were added. The frozen root model remains:

```text
.aide/
.github/
archive/
contracts/
control/
crates/
docs/
evals/
examples/
external/
native/
release/
runtime/
scripts/
site/
snapshots/
surfaces/
tests/
tools/
```

## `scripts/` Decision

`scripts/` remains an allowed top-level root for thin wrappers. The repo still
has 59 substantive script files, so the validator continues to report:

```text
scripts_large_tool_tree
```

as known debt.

This task did not move those files because that would be broad directory work
and outside the current repair scope.


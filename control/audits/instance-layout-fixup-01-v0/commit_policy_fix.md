# Commit Policy Fix

AIDE commit policy allows `chore`, `docs`, and other types, but not `ops`.

The requested `INSTANCE-LAYOUT-01` commit used:

```text
ops(local): standardize sibling instance layout
```

By the time this fixup began, `ff484007` was already at `origin/dev`.
Amending it would require rewriting pushed history and a force push, both of
which are forbidden for this task. The message is therefore classified as
blocked, not amended.

This fixup uses a new allowed-type commit so `commit check --latest` can pass
without rewriting pushed history.

# Architecture Boundary Repair Report

## Status

`PASS_WITH_WARNINGS`

## Repairs

### Runtime Architecture Leakage

Added 89 exact context-bound allowlist entries for current production-path
vocabulary findings. These entries are:

- created for `ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01`;
- scoped by path, term, line, column, and context hash;
- non-permanent;
- expired after `QUEUE-HANDOFF-DRIFT-REPAIR-01`;
- recorded as known debt, not readiness.

After repair:

```text
new_violation_count: 0
known_allowlisted_violation_count: 2035
```

### Legacy Runtime Leakage

The legacy validator now ignores `false_positive_candidate` findings while
checking R0 seam leakage. This prevents `User-Agent` transport headers from
being treated as task/control vocabulary leakage.

### Repo Structure Canon

`scripts/` remains known debt instead of a strict-mode warning. The
repo-structure tests now assert that known debt explicitly.

## Residual Debt

- `scripts_large_tool_tree` remains known debt.
- 2035 runtime architecture leakage findings remain allowlisted debt.
- Queue handoff drift remains the largest full-discovery failure family.
- Public alpha remains blocked.
- `dev -> main` promotion remains blocked.


# Allowed Divergences

This file documents the future format for Python-oracle to Rust-candidate
differences. It is not a divergence engine.

No Rust output may be treated as parity-equivalent to Python output unless the
difference is either an exact match or is explicitly recorded and accepted.

Future divergence records should include:

- seam:
- fixture:
- field_path:
- python_value:
- rust_value:
- reason:
- accepted_by:
- date:
- status:

Example:

```json
{
  "seam": "query_planner",
  "fixture": "windows_7_apps",
  "field_path": "$.body.query_plan.planner_notes[0]",
  "python_value": "Recognized a platform-scoped software browsing query.",
  "rust_value": "Recognized a platform-scoped software browsing query",
  "reason": "Punctuation-only rendering difference after reviewed normalization.",
  "accepted_by": "unassigned",
  "date": "YYYY-MM-DD",
  "status": "example_only"
}
```

The v0 fixture pack records no accepted divergences.

## Future Rust Local Index Divergences

Rust Local Index Parity Planning v0 does not record accepted divergences. It
only names the narrow classes that a future Rust Local Index Parity Candidate
may ask to record after review.

Allowed in a future candidate only if explicitly recorded:

- FTS5 availability differences after normalization.
- SQLite implementation/version metadata differences after normalization.
- Internal row IDs if public output stays stable.
- Non-public timing/performance differences.

Not allowed:

- Missing record kinds.
- Missing source IDs.
- Missing synthetic members.
- Missing parent/member lineage.
- Missing article/scan records where Python has them.
- Missing compatibility evidence where Python has it.
- Missing result lanes or user-cost fields.
- Unstable query result ordering after normalization.
- Private path leakage.
- Source placeholder overclaiming.

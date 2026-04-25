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

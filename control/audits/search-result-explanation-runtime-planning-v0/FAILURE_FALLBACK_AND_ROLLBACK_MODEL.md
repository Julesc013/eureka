# Failure, Fallback, And Rollback Model

Future behavior:

- If explanation runtime fails, public search still returns the result.
- If privacy policy fails, omit or redact explanation.
- If ranking explanation is missing, do not expose a ranking score.
- If source/evidence refs are missing, say not available or not checked.
- If explanation generation exceeds timeout, return the result without
  explanation or with a static fallback.
- Operator kill switch disables explanation completely.
- No mutation rollback is required because mutation is forbidden.

Errors must be bounded and must not include private payloads, paths, queries, or
secret-like values.


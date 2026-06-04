# Manual Observation Batch 00

Task ID: `MANUAL-OBSERVATION-BATCH-00`

This batch creates manual, source-backed observation material for the six
hard-query seed corpus queries.

JSON is used instead of YAML so the eval lane stays stdlib-only and consistent
with the existing hard-query and seed-corpus fixtures.

## Files

- `observations.json`: six manual observation attempts.
- `source_references.json`: bounded page-level source references.
- `query_mapping.json`: hard-query to observation/status map.
- `reviewable_items.json`: review queue handoff items.
- `non_reviewable_items.json`: manual follow-up items.
- `corpus_gate_status.json`: updated corpus gate counts.
- `validation_summary.json`: deterministic task validation summary.
- `loader.py`: parser, validator, and SurfaceKernel projection helper.

No reviewed records, review events, source-provider calls, downloads, file
fetches, Wayback replay, or index mutations are created by this batch.

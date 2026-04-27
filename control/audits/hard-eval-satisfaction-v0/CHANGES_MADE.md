# Changes Made

## Eval Runner

`runtime/engine/evals/archive_resolution_runner.py` now evaluates structured
search evidence when checking `search.expected_result_hints`.

The runner can recognize bounded evidence from:

- member paths
- representation IDs
- source IDs and source families
- compatibility evidence records
- artifact-like file locators
- result lanes
- top-result evidence snippets
- task platform, hardware, product, and function constraints

The mapping remains deterministic. It does not infer semantic relevance and
does not use planner fields alone to satisfy search-result checks.

## Fixtures

No fixture files were changed. Existing committed fixture evidence was enough
to move five tasks from `not_satisfied` to `partial`.

## Tests

Validation now checks that:

- the hard eval satisfaction report exists and parses
- task count remains six
- five source-backed tasks are partial
- article-inside-scan remains a capability gap
- partial tasks cite source-backed structured evidence
- no hard task is marked satisfied overall
- external baselines remain unrelated and pending/manual

## Docs And Metadata

The roadmap, backlog, AIDE metadata, test registry, and eval docs now identify
Hard Eval Satisfaction Pack v0 as implemented and select the next milestone.

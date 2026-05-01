# Result Summary Model

`result_summary` is summary-only and is not a result cache.

Fields include:

- `result_count`
- `returned_count`
- optional `top_score`
- confidence
- hit state
- near-miss count
- gap types
- warnings
- limitations

The example records a bounded summary for `windows 7 apps` against the
controlled public index. It does not store result cards or user history.

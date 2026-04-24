# Search Benchmark Design

Eureka's current benchmark posture starts from the archive-resolution task
corpus under `evals/archive_resolution/`.

## Why This Exists

The benchmark exists to prevent future resolver work from outrunning measurable
product behavior.

Future work on:

- source registry
- resolution runs
- query planner
- ranking
- decomposition
- compatibility
- absence reasoning
- optional AI helpers

should improve or at least preserve benchmark behavior rather than rely on
vague architectural enthusiasm alone.

## Current Corpus

The current task set already covers hard-query families such as:

- platform software search
- vague software identity
- latest-compatible release search
- driver inside bundle
- article inside scan

## Future Metrics

The benchmark should eventually report metrics such as:

- exact-object accuracy
- exact-version accuracy
- false-positive rate
- false-safe rate
- user-cost reduction
- time-to-first-useful-result
- time-to-confidence
- extraction success
- absence-report quality
- lane coverage
- actionability

## Current Status

The corpus now has its first executable guardrail:

- Archive Resolution Eval Runner v0 loads the packet
- it runs Query Planner v0
- it builds or uses Local Index v0 when available
- it falls back to deterministic search when needed
- it records bounded absence reasoning for no-result cases
- it emits stable JSON per-task and suite reports

This is not a full relevance benchmark. It does not score ranking, fuzzy
retrieval, vector or semantic search, LLM planning, crawling, live source sync,
or production search quality. Many hard tasks should currently report
`capability_gap`; that is the honest result until the corpus and bounded
resolver capabilities can satisfy their direct-artifact, member-level, article,
or evidence expectations.

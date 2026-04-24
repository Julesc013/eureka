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

The corpus exists today. A full benchmark runner does not yet exist. That is
acceptable for the current stage because the repo needed the governed task set
before it needed a broader scoring harness.

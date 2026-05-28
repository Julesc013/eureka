# Root Evals

`evals/` is reserved for repo-level evaluations that measure system behavior
over time rather than component-local correctness.

Current families:

- `archive_resolution/`: hard software-resolution benchmark tasks.
- `search_usefulness/`: broad query pack and manual external-baseline status.
- `system/`: system-level evaluation sets.
- `replay/`: replayable scenarios and regression-oriented runs.

Evals are evidence tools. They are not production relevance claims, broad corpus
coverage claims, Google/Internet Archive comparison claims, or proof of public
launch readiness.

Related docs:

- [Search Benchmark Design](../docs/evals/SEARCH_BENCHMARK_DESIGN.md)
- [Test and Eval Lanes](../docs/operations/TEST_AND_EVAL_LANES.md)

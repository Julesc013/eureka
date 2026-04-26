# Root Evals

`evals/` is reserved for repo-level evaluations that measure system behavior over time rather than component-local correctness.

- `archive_resolution/`: hard software-resolution benchmark tasks that guard future investigation, ranking, decomposition, source-expansion, and optional AI work
- `search_usefulness/`: broad Search Usefulness Audit v0 query pack,
  observation schemas, and report guidance for classifying current Eureka
  usefulness, source gaps, capability gaps, and pending manual external
  baselines
- `system/`: system-level evaluation sets
- `replay/`: replayable captured scenarios and regression-oriented runs

Benchmark-design guidance now lives in:

- [docs/evals/SEARCH_BENCHMARK_DESIGN.md](../docs/evals/SEARCH_BENCHMARK_DESIGN.md)

Repo-level audit findings and hard-test proposals now live under:

- [control/audits/](../control/audits/README.md)

Search usefulness backlog triage now lives under:

- [control/backlog/search_usefulness_triage/](../control/backlog/search_usefulness_triage/README.md)

Source Coverage and Capability Model v0 adds source capability and
coverage-depth metadata that later eval deltas can use when Real Source
Coverage Pack v0 adds recorded fixtures. It does not add live source access or
external baseline observations.

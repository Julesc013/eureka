# Engine Evals

`runtime/engine/evals/` contains bounded executable eval harnesses for the
Python reference lane.

Current scope:

- `archive_resolution_runner.py` implements Archive Resolution Eval Runner v0
  over the governed packet in `evals/archive_resolution/`
- `search_usefulness_runner.py` implements Search Usefulness Audit v0 over
  `evals/search_usefulness/`
- `eval_result.py` defines compact JSON-serializable task, check, task-result,
  and suite-result models
- the runner loads the current JSON-subset-of-YAML task fixtures, runs Query
  Planner v0, builds or uses Local Index v0 once per suite when available,
  falls back to deterministic search when needed, calls bounded absence
  reasoning for no-result cases, and reports structured checks

Archive Resolution Eval Runner v0 is a regression harness, not a ranking or
semantic relevance benchmark. It reports `satisfied`, `partial`,
`not_satisfied`, `not_evaluable`, and `capability_gap` states honestly. The
current hard fixtures are expected to remain mostly capability gaps until the
corpus and bounded resolver capabilities grow.

Search Usefulness Audit v0 is broader and more diagnostic: it runs a large
archive-resolution-style query pack through the current bounded Eureka path,
marks external baselines as `pending_manual_observation`, and aggregates
failure modes plus future-work labels. It does not call Google, Internet
Archive, or other external systems.

Out of scope:

- ranking metrics
- fuzzy retrieval
- vector or semantic search
- LLM planning
- live source sync or crawling
- production benchmark dashboards
- background or distributed eval workers

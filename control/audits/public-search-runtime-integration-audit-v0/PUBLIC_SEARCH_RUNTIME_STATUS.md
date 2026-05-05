# Public Search Runtime Status

Current mode: `local_index_only`.

Status:

- Local public search runtime: `implemented_local_runtime`.
- Hosted public search runtime: `operator_gated`.
- Public API status: local/prototype only.
- Static status: static handoff and generated public data exist.
- Current integrations: public search reads the controlled local/public index,
  source registry summaries, deterministic query planner output, and local
  public-safe result-card projection.
- Missing integrations: source cache dry-run, evidence ledger dry-run, query
  observation, page runtime, connector runtimes, pack import, deep extraction,
  search-result explanation runtime, and ranking runtime.
- Unexpected integrations: none found.

Limitations:

- No hosted deployment is verified.
- Public search remains local/prototype and not production-ready.
- Public search must not mutate source cache, evidence ledger, candidate index,
  public index, local index, runtime index, or master index.


# INDEXLESS-LIVE-SEARCH-FALLBACK-00-PREFLIGHT

This preflight decides where `INDEXLESS-LIVE-SEARCH-FALLBACK-00` should attach
inside the current Eureka repo.

It is docs-only. It does not implement fallback behavior, modify runtime code,
change contracts, mutate queue state, add source adapter behavior, or change
public surfaces.

## Decision

Read `RESOLVER_PATH_DECISION.md` first.

The selected path is:

```text
DECISION: USE_EXISTING_ENGINE_RESOLUTION_RUNS_PATH
```

## Next Task

Run `INDEXLESS-LIVE-SEARCH-FALLBACK-00` against the selected engine
resolution-runs seam. The implementation must preserve the path:

```text
query
-> runtime/engine/resolution_runs service
-> local lookup unavailable or insufficient
-> fallback eligibility and policy gate
-> bounded source work unit or equivalent
-> source action / metadata lookup seam
-> source observation or equivalent
-> candidate or search need
-> public-safe view model / result state
```

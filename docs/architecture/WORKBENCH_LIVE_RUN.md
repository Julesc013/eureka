# Workbench Live Run

Workbench live runs project headless `ResolutionRunKernel` packets into the local Workbench and local JSON API. The Workbench does not own search semantics, query compilation, WorkUnit planning, lane assembly, or policy gates.

The foundation path is:

```text
runtime/resolution_run
-> runtime/local_service/workbench_live_run
-> runtime/local_workbench rendering
-> local HTML/API routes
```

This task enables local dry-run creation and inspection only. It shows `run_id`, state, event log summaries, lane snapshots, planned IA-HUNT dry-run WorkUnits, and blocked/deferred actions.

Boundaries:

- no live IA calls by default
- no source probes by default
- no operator instance mutation by default
- no source-cache, evidence, candidate, reviewed-index, public-index, or master-index mutation
- no review/promote flow yet
- no Local Apply Gate yet
- no deployment, production readiness, or public launch claim

The presentation currently uses the existing transitional `runtime/local_workbench` renderer because that is the local service convention. Runtime behavior remains in `runtime/resolution_run` and `runtime/local_service`.

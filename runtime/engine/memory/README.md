# Resolution Memory v0

`runtime/engine/memory/` holds Eureka's first explicit local memory seam for
reusable investigation outcomes.

This slice is intentionally narrow:

- local only
- caller-provided memory-store root
- explicit/manual creation from one existing persisted resolution run
- JSON persistence only
- stdlib-only
- no shared or cloud memory
- no private user-history capture
- no personalization, ranking, or LLM memory semantics
- invalidation fields only, not an invalidation engine

Supported memory kinds created in v0:

- `successful_resolution`
- `successful_search`
- `absence_finding`

`source_usefulness` remains a governed memory kind in the contracts, but this
first runtime slice does not automatically create standalone source-usefulness
records yet.

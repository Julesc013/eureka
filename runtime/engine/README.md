# Engine

`runtime/engine/` is the home for engine behavior and its declared dependency boundaries.

Boundary notes:

- engine must not depend on `surfaces/*`
- engine owns runtime behavior, not surface presentation
- `interfaces/public/` and `interfaces/service/` are the only engine-facing paths that gateway may consume
- `interfaces/ingest/`, `interfaces/extract/`, and `interfaces/normalize/` are the only engine-facing paths that connectors may consume
- `sdk/` is reserved for a future narrow offline boundary and is intentionally empty
- these interface paths are concrete and advisory today; enforcement tooling is still deferred

Current thin-slice behavior:

- Python 3 standard library only
- engine consumes normalized records only
- governed local synthetic fixture access is kept behind `runtime/connectors/synthetic_software/`
- bootstrap normalization currently flows through `interfaces/ingest/`, `interfaces/extract/`, and `interfaces/normalize/`
- exact-match resolution for bounded `target_ref` values only
- bounded object-summary mapping aligned to the gateway public API draft

This slice does not settle connector strategy, ranking, fuzzy resolution, or broader archive semantics.

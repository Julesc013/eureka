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
- deterministic search over a tiny bounded set of normalized fields using stable catalog order
- bounded object-summary mapping aligned to the gateway public API draft
- bootstrap deterministic `resolved_resource_id` derivation for already-normalized or already-resolved records
- bounded resolution-manifest export from already-normalized records under `actions/`
- bounded portable resolution-bundle export from already-normalized records under `snapshots/`
- bounded portable bundle inspection from local bytes or a local file path under `snapshots/`, without live fixture dependence
- bounded deterministic local artifact storage and retrieval under `store/`, with stable `sha256:<hex>` artifact identity
- propagation of bootstrap `resolved_resource_id` through resolution, search, export, inspection, and local stored-artifact metadata

The current `resolved_resource_id` is a bootstrap deterministic seam only. It hardens propagation beyond raw `target_ref`, but it does not yet define Eureka's final global identity or cross-source merge model.

This slice does not settle connector strategy, ranking, fuzzy resolution, installer behavior, restore behavior, durable cache semantics, or broader archive semantics.

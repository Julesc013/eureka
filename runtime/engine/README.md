# Engine

`runtime/engine/` is the home for engine behavior and its declared dependency boundaries.

Boundary notes:

- engine must not depend on `surfaces/*`
- engine owns runtime behavior, not surface presentation
- `interfaces/public/` and `interfaces/service/` are the only engine-facing paths that gateway may consume
- `interfaces/ingest/`, `interfaces/extract/`, and `interfaces/normalize/` are the only engine-facing paths that connectors may consume
- `sdk/` is reserved for a future narrow offline boundary and is intentionally empty
- these interface paths are concrete today; wider enforcement remains intentionally deferred beyond the current narrow repo-local Python import checker

Current thin-slice behavior:

- Python 3 standard library only
- engine consumes normalized records only
- governed local synthetic fixture access is kept behind `runtime/connectors/synthetic_software/`
- recorded GitHub Releases source loading is kept behind `runtime/connectors/github_releases/`
- bootstrap normalization currently flows through `interfaces/ingest/`, `interfaces/extract/`, and `interfaces/normalize/`
- exact-match resolution for bounded `target_ref` values only
- deterministic search over a tiny bounded set of normalized fields using stable catalog order across synthetic fixtures and recorded GitHub Releases records
- bounded object-summary mapping aligned to the gateway public API draft
- bootstrap deterministic `resolved_resource_id` derivation for already-normalized or already-resolved records
- bounded source-family and source-origin summaries propagated from normalized records into resolution, search, export, and local store metadata
- bounded evidence summaries propagated from normalized records into exact resolution, deterministic search, export, local storage, and bundle inspection without implying a final provenance graph, trust model, or merge contract
- bounded side-by-side comparison of exactly two resolved targets with explicit agreements and disagreements, preserving evidence per side without implying a merge or truth-selection engine
- bounded subject/state grouping for one bootstrap `subject_key`, with deterministic state ordering and compact per-state source and evidence summaries without implying a final object identity model or timeline graph
- bounded resolution-manifest export from already-normalized records under `actions/`
- bounded portable resolution-bundle export from already-normalized records under `snapshots/`
- bounded portable bundle inspection from local bytes or a local file path under `snapshots/`, without live fixture dependence
- bounded deterministic local artifact storage and retrieval under `store/`, with stable `sha256:<hex>` artifact identity
- propagation of bootstrap `resolved_resource_id` through resolution, search, export, inspection, and local stored-artifact metadata

The current `resolved_resource_id` is a bootstrap deterministic seam only. It hardens propagation beyond raw `target_ref`, but it does not yet define Eureka's final global identity or cross-source merge model.

This slice does not settle broader live-source federation, provenance graphs, trust semantics, comparison or merge semantics beyond the current bounded disagreement seam, final object or state identity semantics beyond the current bounded timeline seam, ranking, fuzzy resolution, installer behavior, restore behavior, durable cache semantics, or broader archive semantics.

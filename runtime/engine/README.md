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
- recorded Internet Archive-like metadata and item-file fixtures are kept behind `runtime/connectors/internet_archive_recorded/`
- committed local bundle ZIP fixtures are kept behind `runtime/connectors/local_bundle_fixtures/`
- deterministic synthetic member records for selected fixture-backed bundle members are kept behind `runtime/engine/synthetic_records/`
- bounded result-lane and user-cost annotations for current result records are kept behind `runtime/engine/ranking/`
- bounded source-backed compatibility evidence extraction for committed
  fixture records is kept behind `runtime/engine/compatibility/`
- bootstrap normalization currently flows through `interfaces/ingest/`, `interfaces/extract/`, and `interfaces/normalize/`
- exact-match resolution for bounded `target_ref` values only
- deterministic search over a tiny bounded set of normalized fields using stable user-cost and label ordering across synthetic fixtures, recorded GitHub Releases records, recorded Internet Archive-like fixtures, local bundle fixtures, and derived synthetic member records
- bounded object-summary mapping aligned to the gateway public API draft
- bootstrap deterministic `resolved_resource_id` derivation for already-normalized or already-resolved records
- bounded source-family and source-origin summaries propagated from normalized records into resolution, search, export, and local store metadata
- bounded evidence summaries propagated from normalized records into exact resolution, deterministic search, export, local storage, and bundle inspection without implying a final provenance graph, trust model, or merge contract
- bounded side-by-side comparison of exactly two resolved targets with explicit agreements and disagreements, preserving evidence per side without implying a merge or truth-selection engine
- bounded subject/state grouping for one bootstrap `subject_key`, with deterministic state ordering and compact per-state source and evidence summaries without implying a final object identity model or timeline graph
- bounded absence reasoning for exact-resolution misses and deterministic search no-result cases, surfacing checked source families plus compact near matches without implying ranking, fuzzy retrieval, or a final diagnostic engine
- bounded representation and access-path summaries for one resolved target, preserving multiple known source-backed paths without implying final download, install, import, restore, or representation-selection semantics
- bounded compatibility evaluation for one resolved target against one bootstrap host profile preset, returning compact reasons plus honest `unknown` outcomes without implying a final compatibility oracle or installer model
- bounded source-backed compatibility evidence records for current fixture data,
  carrying platform, architecture, claim type, evidence kind, confidence,
  locator, and source identity without implying runtime execution or a final
  compatibility oracle
- bounded action routing for one resolved target, combining known representations, optional host-profile compatibility, and bounded local export/store context into explicit recommended, available, and unavailable next steps without implying execution, installer, or runtime-routing behavior
- bounded strategy profiles for one resolved target, varying recommendation emphasis across a fixed explicit set of user goals without mutating resolved identity, evidence, or representation truth and without implying personalization, ranking, or a final user-model framework
- bounded representation-selection and handoff recommendations for one resolved target, combining known representations plus optional host-profile compatibility and strategy emphasis into explicit preferred, available, unsuitable, and unknown choices without implying downloads, installers, launches, or final routing semantics
- bounded acquisition and fetch for one explicitly chosen representation, retrieving tiny deterministic fixture-backed payload bytes or returning structured unavailable and blocked results without implying live downloads, installers, restore flows, or execution behavior
- bounded decomposition and package-member inspection for one explicitly chosen fetched representation, returning compact ZIP member listings or structured unsupported, unavailable, and blocked results without implying extraction-to-disk, installers, import, or restore behavior
- bounded member-readback and preview for one explicitly chosen member inside one explicitly chosen fetched representation, returning compact text previews or structured unsupported, unavailable, and blocked results without implying extraction-to-disk, installers, import, restore, or broad file-format support
- bounded deterministic query planning for a small eval-backed set of raw-query families, compiling raw user text into a structured `ResolutionTask` with compact platform, product, hardware, topic, and date hints without implying LLM planning, vector search, fuzzy retrieval, ranking, or full investigation planning
- bounded result-lane and user-cost annotation under `ranking/`, assigning deterministic usefulness hints and reasons to current result records without implying production ranking, fuzzy retrieval, vector search, LLM scoring, live source behavior, or source-trust scoring
- bounded local indexing for the current mixed catalog under `index/`, building a local SQLite search substrate with FTS5 preferred and deterministic fallback query behavior, preserving compact source ids, source families, resolved-resource identity, representation summaries, synthetic member records, parent lineage, member paths, evidence summaries, source-registry records, bounded lane/user-cost annotations, and bounded compatibility evidence summaries without implying production ranking, fuzzy retrieval, vector search, live sync, or incremental indexing
- bounded archive-resolution eval execution under `evals/`, loading the governed hard-query packet, running Query Planner v0, building or using Local Index v0 once per suite, falling back to deterministic search when needed, recording absence reasoning, and reporting stable JSON check states without implying ranking, fuzzy retrieval, vector search, LLM planning, crawling, live source sync, or production relevance evaluation
- bounded synchronous local task execution under `workers/`, wrapping source-registry validation, local-index build and query, and archive-resolution eval validation as persisted JSON task records without implying background scheduling, retries, priorities, or distributed queue behavior
- bounded synchronous resolution runs for exact resolution, deterministic search, and planner-backed planned-search starts, persisted as local bootstrap JSON investigation records that capture checked source ids/families plus current result or absence summaries and optional `resolution_task` summaries without implying streaming phases, workers, or async orchestration
- bounded explicit local resolution memory under `memory/`, deriving compact reusable successful-resolution, successful-search, and absence-finding records from persisted completed resolution runs without implying shared/cloud memory, private user-history tracking, personalization, ranking, or an invalidation engine
- bounded resolution-manifest export from already-normalized records under `actions/`
- bounded portable resolution-bundle export from already-normalized records under `snapshots/`
- bounded portable bundle inspection from local bytes or a local file path under `snapshots/`, without live fixture dependence
- bounded deterministic local artifact storage and retrieval under `store/`, with stable `sha256:<hex>` artifact identity
- propagation of bootstrap `resolved_resource_id` through resolution, search, export, inspection, and local stored-artifact metadata

The current `resolved_resource_id` is a bootstrap deterministic seam only. It hardens propagation beyond raw `target_ref`, but it does not yet define Eureka's final global identity or cross-source merge model.

This slice does not settle broader live-source federation, provenance graphs, trust semantics, comparison or merge semantics beyond the current bounded disagreement seam, final object or state identity semantics beyond the current bounded timeline seam, final diagnostic or absence-reasoning semantics beyond the current bounded miss-explanation seam, final representation, access-path, acquisition, fetch, decomposition, member-record, member-readback, or result-lane semantics beyond the current bounded summary seams, final compatibility or host-profile semantics beyond the current bounded verdict and evidence seams, final action-routing, representation-selection, strategy, or execution-policy semantics beyond the current bounded recommendation seams, full investigation-planning semantics, planner-driven retrieval routing, incremental indexing, production ranking, fuzzy resolution, vector or semantic search, shared/cloud resolution memory, automatic invalidation, production worker queues, streaming transports, personalization, installer behavior, restore behavior, durable multi-user cache semantics, production relevance benchmarking, or broader archive and extraction semantics.

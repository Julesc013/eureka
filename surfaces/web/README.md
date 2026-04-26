# Web Surface

`surfaces/web/` is the home for the Eureka web workbench.

The normal web path goes through `contracts/gateway/public_api` and governed surface contracts. It must not bind directly to engine internals.

Current bootstrap slice:

- stdlib-only, local-only, server-rendered compatibility-first workbench page
- explicit `local_dev` and `public_alpha` server modes for the stdlib web/API surface
- public-alpha route posture is inventoried in `control/inventory/public_alpha_routes.json`
- public-alpha readiness smoke checks live in `scripts/public_alpha_smoke.py`
- consumes the transport-neutral gateway public submit/read and search boundaries
- renders exact resolution from the shared `WorkbenchSession` view model rather than engine-owned state
- renders side-by-side comparison at `/compare?left=...&right=...` from a shared comparison view model rather than engine-owned compare state
- renders bounded subject-state listing at `/subject?key=...` from a shared subject-state view model rather than engine-owned grouping state
- renders bounded miss explanations at `/absence/resolve?target_ref=...` and `/absence/search?q=...` from a shared absence-report view model rather than engine-owned diagnostic state
- renders bounded known representations and access paths in the exact-resolution page and at `/representations?target_ref=...` from shared public-boundary data rather than engine-owned artifact logic
- renders compatibility-first source-registry listing at `/sources` and bounded source detail at `/source?id=...` from a shared source-registry view model rather than reading control inventory directly, including capability summaries, coverage depth, connector mode, current limitations, next coverage steps, and placeholder warnings
- renders compatibility-first deterministic query planning at `/query-plan?q=...` from a shared query-plan view model rather than engine-owned planner state, including old-platform platform constraints, latest-compatible intent, driver/hardware hints, vague identity uncertainty, documentation intent, member-discovery hints, and suppression hints when present
- renders compatibility-first local-index build, status, and search pages at `/index/build?index_path=...`, `/index/status?index_path=...`, and `/index/search?q=...&index_path=...` from a shared local-index view model rather than engine-owned SQLite state
- renders compatibility-first archive-resolution eval reports at `/evals/archive-resolution?task_id=...&index_path=...` from a shared eval-report view model rather than engine-owned runner state, keeping capability gaps visible for hard fixtures
- renders mode/capability status at `/status` without disclosing private configured local paths
- renders compatibility-first synchronous local-task listing at `/tasks?task_store_root=...`, bounded task detail at `/task?id=...&task_store_root=...`, and bounded task-run pages at `/task/run/validate-source-registry?...`, `/task/run/build-local-index?...`, `/task/run/query-local-index?...`, plus `/task/run/validate-archive-resolution-evals?...` without implying background scheduling, retries, or distributed queue behavior
- renders compatibility-first synchronous resolution-run listing at `/runs?run_store_root=...`, bounded run detail at `/run?id=...&run_store_root=...`, and bounded run-start pages at `/run/resolve?...&run_store_root=...`, `/run/search?...&run_store_root=...`, plus `/run/planned-search?...&run_store_root=...` without implying worker queues, streaming updates, or full investigation planning
- renders compatibility-first explicit local resolution-memory listing at `/memories?memory_store_root=...`, bounded memory detail at `/memory?id=...&memory_store_root=...`, and bounded create-from-run pages at `/memory/create?...` without implying cloud memory, private user-history tracking, personalization, ranking, or automatic invalidation
- renders bounded compatibility evaluation at `/compatibility?target_ref=...&host=...` from a shared compatibility view model rather than engine-owned requirement logic
- renders bounded representation-selection and handoff guidance in the exact-resolution page and at `/handoff?target_ref=...&host=...&strategy=...` from a shared handoff view model rather than engine-owned routing logic
- distinguishes fetchable and non-fetchable known representations in the exact-resolution page and handoff guidance, and exposes `/fetch?target_ref=...&representation_id=...` as a bounded local payload-retrieval route over the public acquisition boundary
- exposes `/decompose?target_ref=...&representation_id=...` as a bounded package-member inspection route over the public decomposition boundary, returning compact member listings for supported fetched formats and explicit unsupported or unavailable explanations otherwise
- exposes `/member?target_ref=...&representation_id=...&member_path=...` as a bounded inside-the-package member preview route over the public member-access boundary, rendering compact text previews when available and explicit unsupported, unavailable, or blocked explanations otherwise
- renders bounded recommended, available, and unavailable next-step actions in the exact-resolution page and at `/action-plan?target_ref=...&host=...&strategy=...` from a shared action-plan view model rather than engine-owned policy logic
- renders the bootstrap `resolved_resource_id` for known resolved targets without importing engine internals
- renders bounded source-family and source-origin summaries for resolved and searched records from synthetic fixtures and recorded GitHub Releases fixtures
- renders bounded source-family and source-origin summaries for recorded Internet Archive-like fixtures and committed local bundle fixtures without implying live Internet Archive access or arbitrary local filesystem ingestion
- renders bounded evidence summaries for resolved, searched, and inspected records without implying a final provenance or trust model
- renders a bounded action panel from the shared `ResolutionActions` view model and exposes JSON manifest export plus ZIP bundle export routes
- renders local stored-export actions plus a stored-exports section from a shared `StoredExports` model and exposes stored-artifact retrieval routes
- renders a compatibility-first bundle inspection page from a shared bundle-inspection model through a local-path bootstrap route
- renders deterministic search results and structured absence reports from a shared search-results view model
- renders deterministic `synthetic_member` search, local-index, and exact-resolution fields when the public boundary provides bounded member target refs, member paths, parent target refs, member kind, and action hints
- renders bounded result-lane and user-cost hints for search, local-index, and
  exact-resolution records when the public boundary provides them, including
  compact explanations for member-vs-parent usefulness
- links blocked exact-resolution pages and search no-result pages into the dedicated bounded absence-report routes
- renders `resolved_resource_id` in search results, stored-export summaries, and bundle inspection when the public boundary provides it
- links search results back into the exact-resolution workbench flow through target references
- exposes the first local stdlib machine-readable HTTP API slice under `/api/...` for exact resolution, deterministic search, manifest export, bundle export, bundle inspection, and local stored-export actions by reusing the same transport-neutral gateway public boundary already consumed by the HTML workbench and CLI
- exposes `/api/compare?left=...&right=...` for machine-readable comparison over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/states?subject=...` for machine-readable bounded subject-state listing over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/absence/resolve?target_ref=...` and `/api/absence/search?q=...` for machine-readable bounded miss explanations over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/representations?target_ref=...` for machine-readable bounded representation and access-path listing over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/sources?...` and `/api/source?id=...` for machine-readable bounded source-registry listing and source detail over the same transport-neutral public boundary already reused by the HTML workbench and CLI, including safe capability and coverage metadata
- exposes `/api/query-plan?q=...` for machine-readable deterministic query planning over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/index/build?index_path=...`, `/api/index/status?index_path=...`, and `/api/index/query?index_path=...&q=...` for machine-readable bootstrap local indexing over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/evals/archive-resolution?task_id=...&index_path=...` for machine-readable Archive Resolution Eval Runner v0 reports over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/status` for machine-readable mode, safe-mode, enabled-capability, disabled-capability, and configured-root-kind reporting without returning private local path values
- exposes `/api/tasks?task_store_root=...`, `/api/task?id=...&task_store_root=...`, `/api/task/run/validate-source-registry?task_store_root=...`, `/api/task/run/build-local-index?task_store_root=...&index_path=...`, `/api/task/run/query-local-index?task_store_root=...&index_path=...&q=...`, and `/api/task/run/validate-archive-resolution-evals?task_store_root=...` for machine-readable synchronous bootstrap local tasks over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/runs?run_store_root=...`, `/api/run?id=...&run_store_root=...`, `/api/run/resolve?target_ref=...&run_store_root=...`, `/api/run/search?q=...&run_store_root=...`, and `/api/run/planned-search?q=...&run_store_root=...` for machine-readable bounded synchronous resolution runs over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/memories?memory_store_root=...`, `/api/memory?id=...&memory_store_root=...`, and `/api/memory/create?run_store_root=...&memory_store_root=...&run_id=...` for machine-readable explicit local resolution memory over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/compatibility?target_ref=...&host=...` for machine-readable bounded compatibility evaluation over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/handoff?target_ref=...&host=...&strategy=...` for machine-readable bounded representation-selection and handoff evaluation over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/fetch?target_ref=...&representation_id=...` for bounded payload bytes or structured unavailable and blocked results over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/decompose?target_ref=...&representation_id=...` for machine-readable bounded decomposition results over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/member?target_ref=...&representation_id=...&member_path=...` for machine-readable bounded member preview results, plus explicit raw-byte readback only when the local bootstrap route is asked for it, over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/action-plan?target_ref=...&host=...&strategy=...` for machine-readable bounded action-plan evaluation over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- does not imply a real framework choice, browser-side JavaScript dependency, routing tree, authentication layer, or deployment model
- does not settle final HTTP API route naming, auth, HTTPS/TLS, deployment, or multi-user semantics
- public-alpha mode blocks caller-provided local path parameters and local write/readback route groups, but remains a constrained demo posture rather than production deployment
- Public Alpha Deployment Readiness Review documents the current verdict and operator checklist under `docs/operations/`; it is not a final security review or public hosting approval
- local store root configuration is a bootstrap-only demo choice, not a final deployment or multi-user storage contract
- run_store_root configuration is a bootstrap-only demo choice for synchronous persisted resolution runs, not a final deployment, worker, or multi-user storage contract
- task_store_root configuration is a bootstrap-only demo choice for synchronous persisted local tasks, not a final deployment, worker, scheduler, or multi-user storage contract
- memory_store_root configuration is a bootstrap-only demo choice for explicit persisted local resolution memory, not a final deployment, shared-memory, or multi-user storage contract
- index_path configuration is a bootstrap-only demo choice for local SQLite indexing, not a final hosted search, multi-user storage, or deployment contract
- local path-based bundle inspection is a bootstrap-only demo choice, not a production upload or import contract
- source-registry pages are inventory, capability, and coverage-depth metadata only; placeholder and future sources must remain visibly unimplemented and local private paths must not be exposed
- Real Source Coverage Pack v0 source pages expose two new active fixture-backed records, `internet-archive-recorded-fixtures` and `local-bundle-fixtures`; the Internet Archive and local-files placeholders remain unimplemented planning anchors
- Member-Level Synthetic Records v0 projects member-level target refs derived from committed local bundle fixtures; this is not broad archive extraction, arbitrary local filesystem ingestion, ranking, live source behavior, or a new connector
- Result Lanes + User-Cost Ranking v0 projects deterministic usefulness hints
  for existing result records; this is not final production ranking,
  fuzzy/vector retrieval, LLM scoring, semantic search, live source behavior, or
  a source-trust model
- query-plan pages are deterministic interpretation aids only; they must not imply LLM reasoning, fuzzy/vector retrieval, ranking, live source behavior, full investigation planning, or planner-owned retrieval routing yet
- local-index pages are deterministic local retrieval aids only; they must not imply ranking, fuzzy retrieval, vector search, live source sync, incremental indexing, or final hosted search semantics
- archive-resolution eval pages are regression reports only; they must not imply ranking, fuzzy retrieval, vector search, LLM planning, crawling, live source sync, or production relevance benchmarking, and current hard-task capability gaps must remain visible
- local-task pages are synchronous local execution aids only; they must not imply async orchestration, background scheduling, retries, priorities, or distributed queue semantics
- resolution-run pages are investigation records only; they must not imply async progression, streaming partial results, worker orchestration, or full planner-owned reasoning yet
- resolution-memory pages are explicit local reuse aids only; they must not imply shared/cloud memory, private user-history tracking, personalization, ranking, or automatic invalidation
- does not settle final download, acquisition, installer, restore, durable cache, persistence, representation-selection, handoff, decomposition, member-readback, or extraction behavior
- does not settle final compatibility, host-profile, installer, or runtime-routing behavior
- does not settle final action-routing, strategy, execution, installer, or runtime-routing behavior
- does not settle final object/state identity presentation, state ordering semantics, or global merge behavior
- does not settle final diagnostic, ranking, trust, or absence-reasoning semantics beyond the current bounded miss-explanation seam

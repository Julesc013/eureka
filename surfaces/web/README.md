# Web Surface

`surfaces/web/` is the home for the Eureka web workbench.

The normal web path goes through `contracts/gateway/public_api` and governed surface contracts. It must not bind directly to engine internals.

Current bootstrap slice:

- stdlib-only, local-only, server-rendered compatibility-first workbench page
- consumes the transport-neutral gateway public submit/read and search boundaries
- renders exact resolution from the shared `WorkbenchSession` view model rather than engine-owned state
- renders side-by-side comparison at `/compare?left=...&right=...` from a shared comparison view model rather than engine-owned compare state
- renders bounded subject-state listing at `/subject?key=...` from a shared subject-state view model rather than engine-owned grouping state
- renders bounded miss explanations at `/absence/resolve?target_ref=...` and `/absence/search?q=...` from a shared absence-report view model rather than engine-owned diagnostic state
- renders bounded known representations and access paths in the exact-resolution page and at `/representations?target_ref=...` from shared public-boundary data rather than engine-owned artifact logic
- renders bounded compatibility evaluation at `/compatibility?target_ref=...&host=...` from a shared compatibility view model rather than engine-owned requirement logic
- renders bounded representation-selection and handoff guidance in the exact-resolution page and at `/handoff?target_ref=...&host=...&strategy=...` from a shared handoff view model rather than engine-owned routing logic
- distinguishes fetchable and non-fetchable known representations in the exact-resolution page and handoff guidance, and exposes `/fetch?target_ref=...&representation_id=...` as a bounded local payload-retrieval route over the public acquisition boundary
- exposes `/decompose?target_ref=...&representation_id=...` as a bounded package-member inspection route over the public decomposition boundary, returning compact member listings for supported fetched formats and explicit unsupported or unavailable explanations otherwise
- exposes `/member?target_ref=...&representation_id=...&member_path=...` as a bounded inside-the-package member preview route over the public member-access boundary, rendering compact text previews when available and explicit unsupported, unavailable, or blocked explanations otherwise
- renders bounded recommended, available, and unavailable next-step actions in the exact-resolution page and at `/action-plan?target_ref=...&host=...&strategy=...` from a shared action-plan view model rather than engine-owned policy logic
- renders the bootstrap `resolved_resource_id` for known resolved targets without importing engine internals
- renders bounded source-family and source-origin summaries for resolved and searched records from synthetic fixtures and recorded GitHub Releases fixtures
- renders bounded evidence summaries for resolved, searched, and inspected records without implying a final provenance or trust model
- renders a bounded action panel from the shared `ResolutionActions` view model and exposes JSON manifest export plus ZIP bundle export routes
- renders local stored-export actions plus a stored-exports section from a shared `StoredExports` model and exposes stored-artifact retrieval routes
- renders a compatibility-first bundle inspection page from a shared bundle-inspection model through a local-path bootstrap route
- renders deterministic search results and structured absence reports from a shared search-results view model
- links blocked exact-resolution pages and search no-result pages into the dedicated bounded absence-report routes
- renders `resolved_resource_id` in search results, stored-export summaries, and bundle inspection when the public boundary provides it
- links search results back into the exact-resolution workbench flow through target references
- exposes the first local stdlib machine-readable HTTP API slice under `/api/...` for exact resolution, deterministic search, manifest export, bundle export, bundle inspection, and local stored-export actions by reusing the same transport-neutral gateway public boundary already consumed by the HTML workbench and CLI
- exposes `/api/compare?left=...&right=...` for machine-readable comparison over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/states?subject=...` for machine-readable bounded subject-state listing over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/absence/resolve?target_ref=...` and `/api/absence/search?q=...` for machine-readable bounded miss explanations over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/representations?target_ref=...` for machine-readable bounded representation and access-path listing over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/compatibility?target_ref=...&host=...` for machine-readable bounded compatibility evaluation over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/handoff?target_ref=...&host=...&strategy=...` for machine-readable bounded representation-selection and handoff evaluation over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/fetch?target_ref=...&representation_id=...` for bounded payload bytes or structured unavailable and blocked results over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/decompose?target_ref=...&representation_id=...` for machine-readable bounded decomposition results over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/member?target_ref=...&representation_id=...&member_path=...` for machine-readable bounded member preview results, plus explicit raw-byte readback only when the local bootstrap route is asked for it, over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- exposes `/api/action-plan?target_ref=...&host=...&strategy=...` for machine-readable bounded action-plan evaluation over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- does not imply a real framework choice, browser-side JavaScript dependency, routing tree, authentication layer, or deployment model
- does not settle final HTTP API route naming, auth, HTTPS/TLS, deployment, or multi-user semantics
- local store root configuration is a bootstrap-only demo choice, not a final deployment or multi-user storage contract
- local path-based bundle inspection is a bootstrap-only demo choice, not a production upload or import contract
- does not settle final download, acquisition, installer, restore, durable cache, persistence, representation-selection, handoff, decomposition, member-readback, or extraction behavior
- does not settle final compatibility, host-profile, installer, or runtime-routing behavior
- does not settle final action-routing, strategy, execution, installer, or runtime-routing behavior
- does not settle final object/state identity presentation, state ordering semantics, or global merge behavior
- does not settle final diagnostic, ranking, trust, or absence-reasoning semantics beyond the current bounded miss-explanation seam

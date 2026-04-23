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
- renders bounded recommended, available, and unavailable next-step actions in the exact-resolution page and at `/action-plan?target_ref=...&host=...` from a shared action-plan view model rather than engine-owned policy logic
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
- exposes `/api/action-plan?target_ref=...&host=...` for machine-readable bounded action-plan evaluation over the same transport-neutral public boundary already reused by the HTML workbench and CLI
- does not imply a real framework choice, browser-side JavaScript dependency, routing tree, authentication layer, or deployment model
- does not settle final HTTP API route naming, auth, HTTPS/TLS, deployment, or multi-user semantics
- local store root configuration is a bootstrap-only demo choice, not a final deployment or multi-user storage contract
- local path-based bundle inspection is a bootstrap-only demo choice, not a production upload or import contract
- does not settle final download, installer, restore, durable cache, persistence, or representation-selection behavior
- does not settle final compatibility, host-profile, installer, or runtime-routing behavior
- does not settle final action-routing, execution, installer, or runtime-routing behavior
- does not settle final object/state identity presentation, state ordering semantics, or global merge behavior
- does not settle final diagnostic, ranking, trust, or absence-reasoning semantics beyond the current bounded miss-explanation seam

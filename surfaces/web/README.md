# Web Surface

`surfaces/web/` is the home for the Eureka web workbench.

The normal web path goes through `contracts/gateway/public_api` and governed surface contracts. It must not bind directly to engine internals.

Current bootstrap slice:

- stdlib-only, local-only, server-rendered compatibility-first workbench page
- consumes the transport-neutral gateway public submit/read and search boundaries
- renders exact resolution from the shared `WorkbenchSession` view model rather than engine-owned state
- renders the bootstrap `resolved_resource_id` for known resolved targets without importing engine internals
- renders a bounded action panel from the shared `ResolutionActions` view model and exposes JSON manifest export plus ZIP bundle export routes
- renders local stored-export actions plus a stored-exports section from a shared `StoredExports` model and exposes stored-artifact retrieval routes
- renders a compatibility-first bundle inspection page from a shared bundle-inspection model through a local-path bootstrap route
- renders deterministic search results and structured absence reports from a shared search-results view model
- renders `resolved_resource_id` in search results, stored-export summaries, and bundle inspection when the public boundary provides it
- links search results back into the exact-resolution workbench flow through target references
- does not imply a real framework choice, browser-side JavaScript dependency, routing tree, authentication layer, or deployment model
- local store root configuration is a bootstrap-only demo choice, not a final deployment or multi-user storage contract
- local path-based bundle inspection is a bootstrap-only demo choice, not a production upload or import contract
- does not settle final download, installer, restore, durable cache, or persistence behavior
- does not settle final identity presentation or global merge semantics

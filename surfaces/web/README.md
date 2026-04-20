# Web Surface

`surfaces/web/` is the home for the Eureka web workbench.

The normal web path goes through `contracts/gateway/public_api` and governed surface contracts. It must not bind directly to engine internals.

Current bootstrap slice:

- stdlib-only, local-only, server-rendered compatibility-first workbench page
- consumes the transport-neutral gateway public submit/read and search boundaries
- renders exact resolution from the shared `WorkbenchSession` view model rather than engine-owned state
- renders a bounded action panel from the shared `ResolutionActions` view model and exposes JSON manifest export plus ZIP bundle export routes
- renders a compatibility-first bundle inspection page from a shared bundle-inspection model through a local-path bootstrap route
- renders deterministic search results and structured absence reports from a shared search-results view model
- links search results back into the exact-resolution workbench flow through target references
- does not imply a real framework choice, browser-side JavaScript dependency, routing tree, authentication layer, or deployment model
- local path-based bundle inspection is a bootstrap-only demo choice, not a production upload or import contract
- does not settle final download, installer, restore, or persistence behavior

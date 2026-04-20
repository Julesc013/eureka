# Web Surface

`surfaces/web/` is the home for the Eureka web workbench.

The normal web path goes through `contracts/gateway/public_api` and governed surface contracts. It must not bind directly to engine internals.

Current bootstrap slice:

- stdlib-only, local-only, server-rendered compatibility-first workbench page
- consumes the transport-neutral gateway public submit and read boundary
- renders from the shared `WorkbenchSession` view model rather than engine-owned state
- does not imply a real framework choice, browser-side JavaScript dependency, routing tree, authentication layer, or deployment model

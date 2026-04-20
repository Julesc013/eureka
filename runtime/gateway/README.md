# Gateway

`runtime/gateway/` is the runtime implementation area for gateway behavior.

Boundary notes:

- gateway depends on governed contracts plus `runtime/engine/interfaces/public/**` and `runtime/engine/interfaces/service/**`
- gateway public product contracts live under `contracts/gateway/public_api`
- the `public_api/` directory here is for runtime implementation support, not for canonical contract definition

Current thin-slice behavior:

- transport-neutral public submit and read boundary over an in-memory job service
- transport-neutral public search boundary over normalized synthetic records
- transport-neutral public action boundary for bounded manifest and bundle discovery and export
- transport-neutral public stored-exports boundary for local deterministic artifact storage, listing, and retrieval
- transport-neutral public bundle inspection boundary for local bootstrap readback of exported bundles
- submit returns an accepted public envelope while read returns the current bounded job envelope
- deterministic job envelopes for known and unknown local synthetic targets
- deterministic search results or a structured absence report for bounded queries
- deterministic manifest and bundle export for known synthetic targets plus blocked export responses for misses
- deterministic local stored-export identity, listing, and readback through a caller-provided store root
- deterministic local bundle inspection without live fixture dependence
- gateway composes with engine service interfaces over normalized records and does not read governed fixtures directly
- shared workbench-session, search-results, resolution-actions, stored-exports, and bundle-inspection mappings are exercised without implementing web or native shells
- no broker, relay, worker, scheduler, auth, or persistence implementation

This slice proves the public boundary shape without implying that async gateway infrastructure already exists.

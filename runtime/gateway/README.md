# Gateway

`runtime/gateway/` is the runtime implementation area for gateway behavior.

Boundary notes:

- gateway depends on governed contracts plus `runtime/engine/interfaces/public/**` and `runtime/engine/interfaces/service/**`
- gateway public product contracts live under `contracts/gateway/public_api`
- the `public_api/` directory here is for runtime implementation support, not for canonical contract definition

Current thin-slice behavior:

- transport-neutral public submit and read boundary over an in-memory job service
- submit returns an accepted public envelope while read returns the current bounded job envelope
- deterministic job envelopes for known and unknown local synthetic targets
- gateway composes with engine service interfaces over normalized records and does not read governed fixtures directly
- shared workbench-session mapping is exercised without implementing web or native shells
- no broker, relay, worker, scheduler, auth, or persistence implementation

This slice proves the public boundary shape without implying that async gateway infrastructure already exists.

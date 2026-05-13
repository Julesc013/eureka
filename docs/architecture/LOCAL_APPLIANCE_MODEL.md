# Local Appliance Model

The Local Appliance is the product kernel for Eureka before F0 continues. R0 recovered durable seams for source observations, source cache, evidence ledger, review queue, and reviewed public index. LOCAL adds the missing local machine-hosted loop that proves those seams as a usable product surface.

The model has five layers:

- Instance: an explicit local instance root, config, schema, migration guard, and no hidden state roots.
- Store: durable local stores for reviewed index, source cache, evidence ledger, review queue, WorkUnits, sessions, and eval records.
- Service: localhost-first HTTP access, read-only by default, with LAN disabled unless a future explicit gate enables it.
- Worker: deterministic WorkUnit execution only, with typed outputs routed through stores and review.
- Workbench: an HTML operator surface for search, sessions, WorkUnits, evidence review, index rebuilds, smoke tests, and evals.

LOCAL-00 does not implement any of those runtime layers. It makes them mandatory before F0 and later tracks claim completion.

## LOCAL-03 Runtime Kernel

LOCAL-03 adds the local runtime composition boundary in `runtime/local_appliance`. This is the first runtime kernel for the appliance route. It opens an explicit initialized instance, validates config/schema/migration state, opens the four existing R0 stores from the store manifest, exposes one `LocalApplianceRuntime`, and reports unified status.

Future service, worker, workbench, and tests must use this boundary instead of opening SQLite paths ad hoc.

LOCAL-03 still does not implement an HTTP server, HTML workbench, WorkUnit runtime, LAN mode, deployment, production readiness, or public launch readiness.

## LOCAL-04 Read-Only Service

LOCAL-04 adds the first service layer in `runtime/local_service`. It is a localhost-only, read-only HTTP adapter over `LocalApplianceRuntime`.

The service exposes status, health, reviewed-index search, object, source, and absence routes. It does not create product truth and does not bypass the instance manifest. The full HTML workbench remains LOCAL-05, and LAN mode remains disabled until a later explicit gate.

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

## LOCAL-05 HTML Workbench

LOCAL-05 adds the first browser workbench in `runtime/local_workbench`. It is server-rendered through the LOCAL-04 service, requires no frontend build and no JavaScript, and stays read-only over the reviewed public index.

The workbench renders home, search, object, source, absence, and status pages. It does not add review decision controls, WorkUnits, source probes, index rebuild behavior, LAN mode, deployment, production readiness, or public launch readiness.

## LOCAL-06 Page Hardening

LOCAL-06 keeps the same localhost-only, read-only workbench and makes it operationally useful. Pages now show store health, reviewed-index status, provenance references, local-only source scope, current-index absence semantics, warnings, limitations, and unavailable capabilities.

This is still not a WorkUnit runtime, review/rebuild UI, source probe runner, LAN mode, deployment, production readiness claim, or public launch claim.

## LOCAL-07 WorkUnit Queue

LOCAL-07 adds the durable local WorkUnit queue as a fifth manifest-defined store: `workunit_queue` at `db/workunit_queue.sqlite`.

The queue records operator-gated work proposals and state transitions. It supports search needs, source probe proposals, evidence review follow-up, index rebuild proposals, regression checks, extraction tasks, and agent-task records as queue entries only.

LOCAL-07 still does not execute workers, run source probes, create review decisions, rebuild indexes, expose LAN, deploy, or claim production/public launch readiness.

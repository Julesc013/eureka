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

## LOCAL-08 Review And Rebuild Loop

LOCAL-08 adds localhost-only operator-gated review decisions and reviewed-index
rebuild. Review decisions are stored in the local `review_queue`; rebuild reads
`source_cache`, `evidence_ledger`, and `review_queue`, then writes accepted
review projections to the local `public_index`.

Raw operator tokens are not persisted. The loop does not execute queued work,
run source probes, mutate a master index, write `site/dist`, expose LAN, deploy,
or claim production/public launch readiness.

## LOCAL-09 Deterministic Worker Runner

LOCAL-09 adds `runtime/local_worker`, a deterministic runner over queued WorkUnits. Enabled workers are local and bounded: noop, review queue summary, token-gated reviewed-index rebuild, absence report, and local status snapshot.

Risky workers remain blocked, including source probes, extraction, research delegation, model calls, downloads, installs, source sync, LAN operations, and deployment. Worker runs record transition history and audit references; they do not accept truth, mutate a master index, expose LAN, deploy, or claim production/public launch readiness.

## LOCAL-10 Auto-Test Harness

LOCAL-10 adds `runtime/local_eval`, a deterministic auto-test and auto-search
harness over the localhost service and workbench. It records service health,
fixed local search results, absence semantics, read-only safety, worker-kind
safety, and latency smoke evidence.

The harness remains local reviewed-index only. It does not add synthetic query
generation, source probes, extraction, model/provider calls, downloads, LAN,
deployment, `site/dist` writes, or master-index mutation.

## LOCAL-11 LAN Binding Safety Gate

LOCAL-11 defines explicit read-only LAN mode for the Local Appliance.

The default service bind remains `127.0.0.1`. LAN-facing bind hosts are accepted
only with `--bind-lan`, and LAN clients can inspect only read-only local status,
health, search, object, source, and absence routes. Operator mutation routes
remain localhost-only. Actual cross-device LAN smoke remains deferred to
LOCAL-12.

## LOCAL-12 LAN Read-Only Smoke

LOCAL-12 proves explicit LAN-bind startup and read-only route availability
through a same-machine smoke script. Mutation route classes remain blocked for
LAN scope, operator mutation remains localhost-only, and shutdown cleanup is
validated.

External second-client smoke was not performed in the automated run, so LOCAL-12
does not claim cross-device LAN proof, deployment, public hosting, production
readiness, or public launch readiness.

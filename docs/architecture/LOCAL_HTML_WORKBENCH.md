# Local HTML Workbench

LOCAL-05 adds the first browser surface for the Local Appliance. It is server-rendered by `surfaces/web/workbench/local_html` and served through `runtime/local_service`; it does not add a frontend build stack, JavaScript requirement, external assets, or write routes.

## Boundary

The workbench is a presentation layer over the LOCAL-04 read-only service and the LOCAL-03 runtime composition boundary. It uses service routes and presentation-safe view models instead of opening store paths or SQLite files directly.

The workbench is allowed to render:

- local appliance status
- reviewed public index search results
- reviewed object details
- records for a local source id
- local current-index absence reports

The workbench is not allowed to render controls that mutate review decisions, create WorkUnits, run source probes, rebuild indexes, enable LAN, upload files, download/install/execute software, write `site/dist`, deploy, or claim production/public launch readiness.

## Pages

- `GET /`
- `GET /search?q=<query>`
- `GET /object/<record_id>`
- `GET /source/<source_id>`
- `GET /absence?q=<query>`
- `GET /status`

All pages include a non-claim banner: local appliance prototype, localhost only, not production, not public launch, and read-only.

## Handoff

LOCAL-06 hardens status, object, source, and absence page behavior. Review decisions remain deferred until LOCAL-08, WorkUnits until LOCAL-07, and LAN until later LOCAL gates.

## LOCAL-06 Page Hardening

LOCAL-06 makes the pages diagnostic rather than merely navigational. The status page shows instance, store, index, migration, server, LAN, deployment, and non-claim flags. Search and object pages show provenance references when the reviewed public index record has source cache, evidence, review item, or review decision IDs. Source pages state local source scope only. Absence pages show checked and unchecked layers and say that absence is not proof that an artifact does not exist.

The hardening keeps the LOCAL-05 posture: server-rendered HTML, no frontend build, no JavaScript requirement, no external assets, no mutation controls, no source probes, no WorkUnits, no review mutation, no index rebuild, no LAN, and no deployment.

## LOCAL-08 Review Pages

LOCAL-08 adds review queue, review item, and reviewed-index rebuild pages. These
pages remain server-rendered and localhost-only. They include POST forms only
for operator-token-gated local review and rebuild actions. The forms do not
start source probes, execute queued work, expose LAN, deploy, or claim public
readiness.

## LOCAL-10 Eval Harness

LOCAL-10 checks the workbench pages as server-rendered HTML. The harness
verifies page availability and safety markers without adding a frontend build,
JavaScript requirement, external assets, or new workbench controls.

## LOCAL-13 Clean-Machine Role

LOCAL-13 uses the HTML workbench smoke as a reproducibility gate. A clean temp
checkout must serve the home, status, search, absence, object-not-found, and
source routes over localhost without external assets, mutation controls, or
readiness claims.

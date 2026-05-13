# Local HTML Workbench

LOCAL-05 adds the first browser surface for the Local Appliance. It is server-rendered by `runtime/local_workbench` and served through `runtime/local_service`; it does not add a frontend build stack, JavaScript requirement, external assets, or write routes.

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

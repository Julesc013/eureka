# Local HTTP Service

LOCAL-04 adds the first HTTP adapter for the Local Appliance. It is a read-only localhost service over `runtime/local_appliance`.

## Boundary

The service uses `open_local_appliance(instance_path, read_only=True)` and reads the reviewed public index through the runtime composition object. It does not open SQLite paths directly.

The service is allowed to:

- bind to `127.0.0.1` or `localhost`
- return local appliance status
- return health status
- search the reviewed public index
- return one reviewed record by record id
- list reviewed records for one source id
- return a known-absence style report over the checked local index state

The service is not allowed to:

- bind to `0.0.0.0`, `::`, or LAN hosts
- expose write routes
- run source probes
- create WorkUnits
- mutate review decisions
- rebuild indexes
- write `site/dist`
- call model/provider APIs
- claim production or public launch readiness

## Routes

The service route set now includes the LOCAL-04 JSON API and the LOCAL-05 HTML workbench:

- `GET /`
- `GET /status`
- `GET /health`
- `GET /api/v1/status`
- `GET /api/v1/health`
- `GET /api/v1/search?q=<query>`
- `GET /api/v1/object/<record_id>`
- `GET /api/v1/source/<source_id>`
- `GET /api/v1/absence?q=<query>`
- `GET /search?q=<query>`
- `GET /object/<record_id>`
- `GET /source/<source_id>`
- `GET /absence?q=<query>`

All routes are read-only. `/api/v1/*` routes return JSON. Non-API workbench routes return server-rendered HTML by default, with `?format=json` available where a JSON equivalent already exists.

## Handoff

LOCAL-06 hardens the status, object, source, and absence pages. LAN mode remains deferred until later LOCAL tasks.

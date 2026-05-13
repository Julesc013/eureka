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

The LOCAL-04 route set is:

- `GET /`
- `GET /status`
- `GET /health`
- `GET /api/v1/status`
- `GET /api/v1/health`
- `GET /api/v1/search?q=<query>`
- `GET /api/v1/object/<record_id>`
- `GET /api/v1/source/<source_id>`
- `GET /api/v1/absence?q=<query>`

All routes are read-only and return JSON except `/`, which returns minimal plain text. The full HTML workbench starts in LOCAL-05.

## Handoff

LOCAL-05 can build the HTML workbench on top of this service boundary. LAN mode remains deferred until later LOCAL tasks.

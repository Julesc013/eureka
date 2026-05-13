# Local HTTP API

The LOCAL-04 API is available only from a loopback bind.

Start the service:

```bash
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765
```

Smoke test it:

```bash
python scripts/eureka_local_service_smoke.py --base-url http://127.0.0.1:8765 --json
```

## Status

`GET /api/v1/status` returns `local_http_status_response.v0`. `GET /status?format=json` returns the same JSON shape; `GET /status` returns the LOCAL-05 HTML status page by default.

The response includes:

- service read-only and localhost flags
- runtime status from `LocalApplianceRuntime.status()`
- reviewed public index summary
- warnings and limitations

## Health

`GET /health` and `GET /api/v1/health` return `local_http_health_response.v0`.

Health reflects local runtime status only. It is not a deployment readiness check.

## Search

`GET /api/v1/search?q=<query>&limit=<limit>` returns `local_http_search_response.v0`.

- `q` is limited to 256 characters.
- `limit` is capped at 50.
- results come from the reviewed public index only.

## Object

`GET /api/v1/object/<record_id>` returns `local_http_object_response.v0` when the record exists.

If the record is missing, the service returns a 404 JSON error. Missing means the record was not found in the checked local index, not that the object does not exist anywhere.

## Source

`GET /api/v1/source/<source_id>` returns `local_http_source_response.v0`.

An empty result is a bounded local-index result. It is not a source-truth claim.

## Absence

`GET /api/v1/absence?q=<query>` returns `local_http_absence_response.v0`.

Absence reports check the local reviewed index only and do not inspect live sources.

## HTML Workbench Routes

LOCAL-05 adds read-only HTML routes for browser use:

- `GET /`
- `GET /search?q=<query>`
- `GET /object/<record_id>`
- `GET /source/<source_id>`
- `GET /absence?q=<query>`
- `GET /status`

The JSON API remains under `/api/v1/*`.

LOCAL-06 hardens the HTML pages without changing these JSON response shapes. Search JSON may carry full public-index record fields for result cards, while preserving the existing result fields.

## Disabled Methods

`POST`, `PUT`, `PATCH`, and `DELETE` are rejected. LOCAL-04 has no write routes.

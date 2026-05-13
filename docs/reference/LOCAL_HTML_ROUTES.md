# Local HTML Routes

The LOCAL-05 workbench routes are read-only HTML routes served by the localhost service.

Start the local service:

```bash
python scripts/eureka_local_server.py --instance ./eureka-instance --host 127.0.0.1 --port 8765
```

Smoke the workbench:

```bash
python scripts/eureka_local_workbench_smoke.py --base-url http://127.0.0.1:8765 --json
```

## Routes

| Route | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Home, status summary, search form, status/API links |
| `/search?q=<query>` | GET | Reviewed public index result cards |
| `/object/<record_id>` | GET | Reviewed record details or not-found state |
| `/source/<source_id>` | GET | Local reviewed records for one source id |
| `/absence?q=<query>` | GET | Local current-index absence report |
| `/status` | GET | Instance, store, migration, and disabled flag status |

## JSON Compatibility

The LOCAL-04 JSON API remains available under `/api/v1/*`. HTML routes that already have JSON equivalents support `?format=json`.

## Accessibility

Pages use semantic HTML, document titles, `lang="en"`, labels for search forms, ordinary links, and no JavaScript dependency. They are readable without CSS.

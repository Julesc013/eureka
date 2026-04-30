# Public Search Impact

Public search remains local/prototype and `local_index_only`.

Current smoke command:

```text
python scripts/public_search_smoke.py --json
```

Smoke status:

- status: passed
- total checks: 30
- failed checks: 0
- mode: local_index_only
- hosted public deployment: false
- live probes enabled: false
- downloads enabled: false
- installs enabled: false
- uploads enabled: false
- local paths enabled: false
- telemetry enabled: false

Representative safe routes remain available in the local/prototype harness:

- `/api/v1/status`
- `/api/v1/search?q=windows+7+apps`
- `/api/v1/search?q=driver.inf`
- `/api/v1/query-plan?q=windows+7+apps`
- `/api/v1/sources`
- `/api/v1/source/synthetic-fixtures`
- `/search?q=windows+7+apps`

Blocked request checks still reject missing queries, too-long queries, too-large limits, live probe mode, local path/store parameters, URL/fetch URL parameters, download/install/upload flags, source credentials, API keys, and live source parameters.


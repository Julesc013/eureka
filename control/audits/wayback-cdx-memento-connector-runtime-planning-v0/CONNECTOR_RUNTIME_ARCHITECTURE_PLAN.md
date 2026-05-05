# Connector Runtime Architecture Plan

Future modules only:

```text
runtime/connectors/wayback_cdx_memento/
  client.py       future bounded metadata-only HTTP client
  uri_policy.py   URI-R privacy and allowlist guard
  policy.py       source policy, approval, rate-limit, timeout, and circuit-breaker guard
  normalize.py    response-to-source-cache summary normalizer
  evidence.py     cache-to-evidence observation candidate builder
  errors.py       bounded error model
  README.md       runtime operating notes
```

These files are not created by P88.

Future dependencies:

- Source sync worker.
- URI privacy guard.
- Source policy guard.
- Source cache writer.
- Evidence ledger writer.
- Connector health reporter.
- Operator kill switch.

Required future env flags:

- `EUREKA_WAYBACK_CDX_MEMENTO_CONNECTOR_ENABLED=0`.
- `EUREKA_WAYBACK_CDX_MEMENTO_LIVE_CALLS_ENABLED=0`.
- `EUREKA_WAYBACK_CDX_MEMENTO_MAX_RESULTS=10`.
- `EUREKA_WAYBACK_CDX_MEMENTO_TIMEOUT_MS=5000`.
- `EUREKA_WAYBACK_CDX_MEMENTO_RATE_LIMIT_QPS=<operator-defined>`.
- `EUREKA_WAYBACK_CDX_MEMENTO_USER_AGENT=<operator-defined>`.
- `EUREKA_WAYBACK_CDX_MEMENTO_CONTACT=<operator-defined>`.
- `EUREKA_WAYBACK_CDX_MEMENTO_URI_PRIVACY_REQUIRED=1`.
- `EUREKA_WAYBACK_CDX_MEMENTO_CACHE_REQUIRED=1`.
- `EUREKA_WAYBACK_CDX_MEMENTO_PUBLIC_SEARCH_FANOUT=0`.
- `EUREKA_WAYBACK_CDX_MEMENTO_ARCHIVED_CONTENT_FETCH=0`.
- `EUREKA_WAYBACK_CDX_MEMENTO_CAPTURE_REPLAY=0`.
- `EUREKA_WAYBACK_CDX_MEMENTO_WARC_DOWNLOAD=0`.

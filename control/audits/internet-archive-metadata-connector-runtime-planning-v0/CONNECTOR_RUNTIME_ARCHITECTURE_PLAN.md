# Connector Runtime Architecture Plan

Future modules only:

```text
runtime/connectors/internet_archive_metadata/
  client.py       future bounded metadata-only HTTP client
  policy.py       source policy, approval, rate-limit, timeout, and circuit-breaker guard
  normalize.py    response-to-source-cache summary normalizer
  evidence.py     cache-to-evidence observation candidate builder
  errors.py       bounded error model
  README.md       runtime operating notes
```

These files are not created by P87.

Future dependencies:

- Source sync worker.
- Source policy guard.
- Source cache writer.
- Evidence ledger writer.
- Connector health reporter.
- Operator kill switch.

Required future env flags:

- `EUREKA_IA_METADATA_CONNECTOR_ENABLED=0`.
- `EUREKA_IA_METADATA_LIVE_CALLS_ENABLED=0`.
- `EUREKA_IA_METADATA_MAX_ROWS=10`.
- `EUREKA_IA_METADATA_TIMEOUT_MS=5000`.
- `EUREKA_IA_METADATA_RATE_LIMIT_QPS=<operator-defined>`.
- `EUREKA_IA_METADATA_USER_AGENT=<operator-defined>`.
- `EUREKA_IA_METADATA_CONTACT=<operator-defined>`.
- `EUREKA_IA_METADATA_CACHE_REQUIRED=1`.
- `EUREKA_IA_METADATA_PUBLIC_SEARCH_FANOUT=0`.

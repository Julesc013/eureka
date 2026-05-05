# User-Agent, Contact, And Rate-Limit Review

Operator values are missing and must not be fabricated.

Required future values:

- `EUREKA_PYPI_METADATA_USER_AGENT=<operator-defined>`
- `EUREKA_PYPI_METADATA_CONTACT=<operator-defined>`
- `EUREKA_PYPI_METADATA_RATE_LIMIT_QPS=<operator-defined>`
- `EUREKA_PYPI_METADATA_TIMEOUT_MS=5000`
- retry/backoff policy
- per-source circuit breaker

Until those values are approved, live metadata probes remain blocked.

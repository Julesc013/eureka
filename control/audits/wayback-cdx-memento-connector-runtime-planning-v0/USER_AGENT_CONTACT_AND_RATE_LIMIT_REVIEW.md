# User-Agent Contact And Rate Limit Review

Current status: User-Agent/contact and rate-limit values are not configured.

Required future configuration:

- `EUREKA_WAYBACK_CDX_MEMENTO_USER_AGENT=<operator-defined>`.
- `EUREKA_WAYBACK_CDX_MEMENTO_CONTACT=<operator-defined>`.
- `EUREKA_WAYBACK_CDX_MEMENTO_RATE_LIMIT_QPS=<operator-defined>`.
- `EUREKA_WAYBACK_CDX_MEMENTO_TIMEOUT_MS=5000` or another approved bounded value.
- Approved retry/backoff policy.
- Approved per-source circuit breaker.

The plan forbids fake contact details. P88 records an operator action, not a configured value.

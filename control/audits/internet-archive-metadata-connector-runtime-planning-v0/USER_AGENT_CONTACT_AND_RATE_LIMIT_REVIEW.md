# User-Agent Contact And Rate Limit Review

Current status: User-Agent/contact and rate-limit values are not configured.

Required future configuration:

- `EUREKA_IA_METADATA_USER_AGENT=<operator-defined>`.
- `EUREKA_IA_METADATA_CONTACT=<operator-defined>`.
- `EUREKA_IA_METADATA_RATE_LIMIT_QPS=<operator-defined>`.
- `EUREKA_IA_METADATA_TIMEOUT_MS=5000` or another approved bounded value.
- Approved retry/backoff policy.
- Approved per-source circuit breaker.

The plan forbids fake contact details. P87 records an operator action, not a configured value.

# Failure Retry Timeout Circuit Breaker Plan

Future rules:

- Timeout required.
- Max retries bounded.
- Exponential backoff or retry-after respect required.
- Per-source circuit breaker required.
- Per-source rate limit required.
- No retry storms.
- No public-search blocking.
- No raw error payload leaks.
- Connector disabled on policy violation.
- Operator-visible failure summary required.

Public search must not wait on or trigger connector failures.

# Security And Abuse Review

Required future controls:

- Rate limits.
- Timeout.
- Circuit breaker.
- Descriptive User-Agent/contact.
- Cache required before public use.
- Kill switch.
- No public fanout.
- Source policy guard.
- Operator approval.
- Monitoring future only.

Abuse cases to block:

- Identifier spam.
- Large row requests.
- Retry storms.
- Source blocking.
- Public query escalation.
- Arbitrary URL/source fetch attempts.

# Security And Abuse Review

Required future controls:

- Rate limits.
- Timeout.
- Circuit breaker.
- Descriptive User-Agent/contact.
- Cache required before public use.
- Kill switch.
- No public fanout.
- URI privacy guard.
- Source policy guard.
- Operator approval.
- Monitoring future only.

Abuse cases to block:

- Arbitrary URL probing.
- Private URL leakage.
- Credentialed URL leakage.
- Localhost, file, data, or javascript URL abuse.
- Capture replay forcing.
- WARC download forcing.
- Large result requests.
- Retry storms.
- Source blocking.
- Public query escalation.

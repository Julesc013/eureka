# User-Agent, Contact, Rate Limit, Timeout, And Circuit Breaker Status

All first-wave runtime plans require operator decisions for User-Agent/contact,
rate limits, timeouts, retries/backoff, and circuit breakers.

Current status for every connector:

- User-Agent configured: no runtime value configured.
- Contact configured: no runtime value configured.
- Fake contact: forbidden.
- Rate-limit configured: not implemented.
- Timeout configured: required before runtime, not implemented here.
- Retry/backoff configured: required before runtime, not implemented here.
- Circuit breaker configured: required before runtime, not implemented here.
- Operator action required: yes.

This audit records the gate only. It does not choose a User-Agent, contact
address, timeout, rate limit, retry policy, or circuit-breaker threshold.

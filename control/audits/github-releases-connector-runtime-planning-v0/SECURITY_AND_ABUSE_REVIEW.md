# Security And Abuse Review

Required future controls:

- rate limits
- timeout
- circuit breaker
- User-Agent/contact
- token-free default
- cache required before public use
- kill switch
- no public fanout
- repository identity guard
- source policy guard
- operator approval
- monitoring future only

Abuse cases:

- arbitrary repository probing
- private repository leakage
- credentialed URL leakage
- token forcing
- asset download forcing
- source archive download forcing
- raw blob/file fetch forcing
- large release requests
- retry storms
- source blocking
- public query escalation

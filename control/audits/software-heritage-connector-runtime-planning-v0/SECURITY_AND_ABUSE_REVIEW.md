# Security And Abuse Review

Required controls:

- rate limits
- timeout
- circuit breaker
- User-Agent/contact
- token-free default
- cache required before public use
- kill switch
- no public fanout
- SWHID/origin/repository identity guard
- source-code-content guard
- source policy guard
- operator approval
- monitoring future only

Abuse cases:

- arbitrary SWHID probing
- arbitrary origin URL probing
- private repository leakage
- credentialed URL leakage
- token forcing
- content blob fetch forcing
- directory traversal forcing
- source archive download forcing
- repository clone forcing
- origin crawl forcing
- source code execution forcing
- large graph traversal requests
- retry storms
- source blocking
- public query escalation

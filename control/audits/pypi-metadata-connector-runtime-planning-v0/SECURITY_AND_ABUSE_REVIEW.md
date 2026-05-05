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
- package identity guard
- dependency metadata guard
- source policy guard
- token/auth guard
- operator approval
- monitoring future only

Abuse cases:

- arbitrary package probing
- private package leakage
- credentialed index leakage
- token forcing
- wheel/sdist/package file download forcing
- dependency resolution forcing
- package install forcing
- setup.py/build script execution forcing
- large release/file requests
- retry storms
- source blocking
- public query escalation

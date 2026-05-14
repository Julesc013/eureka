# Auth Boundary

Mutating HUNT-03 routes require an operator token and are localhost-only.

- missing token: rejected
- invalid token: rejected
- LAN mutation: rejected with 403
- raw token storage: forbidden
- token logging: forbidden

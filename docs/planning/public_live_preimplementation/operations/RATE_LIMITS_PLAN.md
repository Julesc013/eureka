# Rate Limits Plan

Public alpha should rate-limit:

- search requests
- API requests
- expensive representation generation
- report issue endpoint if first-party later
- any future metadata fallback endpoint

Public rate limits must fail to honest unavailable or policy-blocked states,
not trigger unbounded fanout.


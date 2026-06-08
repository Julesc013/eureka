# Next Task Recommendation

## Recommended Next Task

`EXTERNAL-FULL-DISCOVERY-RERUN-02`

## Why

The known focused repair families from the current external ingest have now been
repaired or reclassified in focused validation:

- architecture boundary drift
- queue handoff drift
- source/snapshot baseline drift
- generated artifact drift
- contract/schema drift

The next gate is an external full-discovery rerun. Do not run full discovery
inside the AI session.

## Still Blocked

- public alpha
- `dev -> main` promotion
- source/snapshot release readiness


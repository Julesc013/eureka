# Next Task Recommendation

## Recommended Next Task

`GENERATED-ARTIFACT-DRIFT-REPAIR-01`

## Why

The targeted source/snapshot baseline family is locally repaired and focused
validation passes. The current queue and external-discovery repair chain still
show generated-artifact drift and contract/schema drift as residual blockers.

Generated-artifact drift should run next because it can affect interpretation of
snapshot/public-site/checksum validation and should be repaired before rerunning
external full discovery.

## Gates Still Blocked

- public alpha
- `dev -> main` promotion
- source/snapshot release gate

## Later Tasks

After generated-artifact and contract/schema drift are repaired or explicitly
externalized, run:

`EXTERNAL-FULL-DISCOVERY-RERUN-02`


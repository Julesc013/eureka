# Identity Contracts

This directory holds governed identity-resolution contracts for Eureka.

Cross-Source Identity Resolution Contract v0 is contract-only. It defines identity relation assessments and provisional identity clusters without runtime identity resolution, destructive deduplication, record merge, candidate promotion, live source calls, telemetry, or index/cache/ledger mutation.

G0 adds fixture/local-eval identity cluster candidates, duplicate candidates,
near misses, and representation groups. They remain provisional and cannot
create accepted identity merges.

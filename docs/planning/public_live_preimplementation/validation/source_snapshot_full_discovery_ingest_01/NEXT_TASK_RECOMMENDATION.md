# Next Task Recommendation

## Recommended Next Task

```text
ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01
```

## Why

The external summary is current but red. Architecture/leakage failures are
explicitly present and rank above queue handoff drift in the ingest prompt
priority order.

## Follow-Up Repair Tasks

After architecture-boundary repair, continue with:

```text
QUEUE-HANDOFF-DRIFT-REPAIR-01
GENERATED-ARTIFACT-DRIFT-REPAIR-01
SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01
CONTRACT-SCHEMA-DRIFT-REPAIR-01
```

The order should be rechecked after each focused repair because one repair may
collapse multiple validator failures.

## Still Blocked

Do not run:

```text
PUBLIC-ALPHA-READINESS-00
PUBLIC-ALPHA-LAUNCH-00
DEV-TO-MAIN-PROMOTION-REVIEW-*
```

until the full-discovery gate, corpus gate, reviewed-artifact gate, readiness
gate, rehearsal gate, and manual approval gate are satisfied.

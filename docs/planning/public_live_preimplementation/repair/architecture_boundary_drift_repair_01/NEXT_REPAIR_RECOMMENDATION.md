# Next Repair Recommendation

## Recommended Next Task

```text
QUEUE-HANDOFF-DRIFT-REPAIR-01
```

## Why

`architecture_boundary_drift` is repaired for the focused labels identified by
the ingest package. The largest remaining full-discovery family is:

```text
queue_handoff_drift
```

The ingest package reported 39 failed-test labels in that family.

## Still Blocked

Do not run:

```text
PUBLIC-ALPHA-READINESS-00
PUBLIC-ALPHA-LAUNCH-00
DEV-TO-MAIN-PROMOTION-REVIEW-*
```

until full discovery is green or the remaining failure families are repaired and
rerun through the external harness.


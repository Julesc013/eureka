# WORKBENCH-RUN-REVIEW-PROJECTION-00

This package records the Workbench run/review projection implementation.

The implementation adds a private/operator projection over:

```text
ResolutionRunRecord
-> fallback_summary
-> sanitized review handoff
-> ReviewQueueStore / ReviewLedger decisions
-> audit events
```

It does not create reviewed records, mutate reviewed/public/master indexes, call source providers, or expose a public review route.

Read:

```text
IMPLEMENTATION_REPORT.md
WORKBENCH_PROJECTION_MAP.md
OPERATOR_ACTION_POLICY.md
PUBLIC_SURFACE_AUDIT.md
REVIEW_LEDGER_INTEGRATION.md
FALLBACK_SUMMARY_PROJECTION.md
TEST_REPORT.md
VALIDATION_REPORT.md
```

Next task: `SURFACE-KERNEL-00`.

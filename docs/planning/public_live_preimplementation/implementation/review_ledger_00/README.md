# REVIEW-LEDGER-00

This package records the focused review-ledger implementation.

The task adds a product-facing review ledger boundary over the existing durable review queue. It lets fallback candidates, fallback needs, source observations, evidence refs, and absence refs become review inputs, then records canonical review decisions through explicit review events.

It does not create reviewed records directly, rebuild indexes, mutate public surfaces, add public operator actions, or allow candidate/source/fallback output to self-promote.

Read:

- `IMPLEMENTATION_REPORT.md`
- `BEHAVIOR_SUMMARY.md`
- `POLICY_AND_SAFETY_REPORT.md`
- `TEST_REPORT.md`
- `VALIDATION_REPORT.md`
- `NEXT_TASK_HANDOFF.md`

Next recommended task: `WORKBENCH-RUN-REVIEW-PROJECTION-00`.

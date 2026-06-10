# Failure Family Inventory

The terminal summary reported `22` failing tests across historical operation-validator expectations.

## Classified Family

| Family | Failed tests | Status |
|---|---:|---|
| `historical_queue_validator_drift` | 22 | blocking |

## Evidence

Representative failures require old queue states such as:

```text
HUNT-01
HUNT-02
HUNT-03
HUNT-04
HUNT-05
HUNT-06
HUNT-07
HUNT-08
HUNT-09
HUNT-10
LOCAL-01
DEV-TO-MAIN-PROMOTION-REVIEW-03
DEV-TO-MAIN-PROMOTION-REVIEW-04
```

The live queue currently points at:

```text
EXTERNAL-FULL-DISCOVERY-RERUN-03
```

These are stale validator expectations, not evidence that the repo should rewind the queue to old tasks.

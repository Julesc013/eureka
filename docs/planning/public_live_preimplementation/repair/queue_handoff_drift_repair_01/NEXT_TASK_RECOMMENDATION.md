# Next Task Recommendation

## Recommended Next Task

```text
SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01
```

## Why

Queue-specific handoff drift is repaired in focused validation. The external
discovery run remains red, and the remaining source/snapshot family is now the
highest-priority product-adjacent validation blocker.

## Acceptable Alternate

If the next repair owner wants one coordinated pass over the smaller residual
families, use:

```text
SOURCE-SNAPSHOT-FAILURE-REPAIR-01
```

and explicitly include:

```text
source_snapshot_baseline_drift
generated_artifact_drift
contract_schema_drift
```

## Still Blocked

Do not run:

```text
PUBLIC-ALPHA-READINESS-00
PUBLIC-ALPHA-LAUNCH-00
DEV-TO-MAIN-PROMOTION-REVIEW-06
```

until full-discovery/source-snapshot gates and corpus/artifact gates are green
or formally waived.

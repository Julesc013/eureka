# Residual Failures

## Repaired

Queue-specific handoff drift is repaired in focused split lanes.

## Reclassified Residual

`ValidateTemporalSemanticInterfaceSystemTest.test_validator_passes` still fails
because `TSIS-00` validator forbids runtime/surface phase files that now exist:

```text
runtime/surface/cache_key.py
runtime/surface/fallback.py
runtime/surface/kernel.py
runtime/surface/output_policy.py
```

This should be handled by `CONTRACT-SCHEMA-DRIFT-REPAIR-01` or a grouped
`SOURCE-SNAPSHOT-FAILURE-REPAIR-01`, not by queue-handoff repair.

## Other External Families Still Expected

```text
source_snapshot_baseline_drift
generated_artifact_drift
contract_schema_drift
```

## Architecture Allowlist Expiry Note

`ARCHITECTURE-BOUNDARY-DRIFT-REPAIR-01` added exact context-bound allowlist
entries with:

```text
expires_after_task: QUEUE-HANDOFF-DRIFT-REPAIR-01
```

This task did not broaden or remove those entries. They remain needed until the
remaining source/snapshot/generated/contract drift repairs either remove the
underlying findings or replace the temporary expiry with a narrower validated
follow-up. This is intentionally documented as residual bounded debt.

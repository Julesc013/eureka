# Failure Family Repair Plan

## Repair Gate

Current repair selection is blocked pending current external full discovery.

## Conditional Repair Order

If current external full discovery fails, repair only the current failure
families returned by the run. Historical families suggest this order if they
recur:

1. `QUEUE-HANDOFF-DRIFT-REPAIR-01`
2. `PUBLIC-INDEX-GENERATED-DRIFT-REPAIR-01`
3. `CHECKSUM-MANIFEST-DRIFT-REPAIR-01`
4. `LEGACY-LEAKAGE-VALIDATOR-DRIFT-REPAIR-01`
5. `SOURCE-SNAPSHOT-FAILURE-REPAIR-01` for mixed or unclassified failures

## Unsafe Repair Approaches

- Do not hand-edit generated `site/dist/**` public-index artifacts.
- Do not hand-edit checksum manifests without running the owning generator or
  validator flow.
- Do not mutate `.aide/queue/current.toml`; it is absent in this checkout.
- Do not change runtime shim paths into new implementation roots.
- Do not treat old red reports as current failure proof.

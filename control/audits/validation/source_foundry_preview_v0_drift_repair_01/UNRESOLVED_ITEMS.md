# Unresolved Items

## Blockers

1. `runtime_leakage_safety_unknown`

   Reclassified as `genuine_product_regression`. The runtime leakage gate reports
   52 new unallowlisted production-path findings and the targeted test lane has
   two current-repo failures.

   Required next task:

   ```text
   SOURCE-FOUNDRY-RUNTIME-LEAKAGE-REPAIR-00
   ```

2. `local_worker_validator_unknown_or_slow`

   Reclassified as `historical_queue_expectation_drift`. Runtime behavior is
   intact, but the validator still expects the old `LOCAL-09` to `LOCAL-10`
   queue posture. The shared historical queue-progress helper is not authorized
   by the current committed repair packet.

## Historical Drift Still Unrepaired

- HUNT queue drift
- LOCAL queue drift
- dev-to-main promotion validator drift
- repo-layout/canon validator drift
- public-alpha defer drift
- IA readiness drift
- local quarantine staging obsolete assertion

## External Full Discovery

Do not run another full discovery yet.

Required before the next external rerun:

- runtime leakage gate repaired
- local-worker historical queue drift repaired
- all historical drift targeted lanes green
- architecture/generated/public-alpha/snapshot checks green
- tracked repairs committed and pushed


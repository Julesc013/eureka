# HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08

Task: `HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08`

This repair addresses the historical queue, promotion, and public-alpha validator
drift reported by external full-discovery rerun 08.

Input evidence:

```text
run_id: source_snapshot_full_discovery_rerun_08
tests_run: 5676
failures: 23
errors: 0
classified_families:
  - historical_queue_validator_drift
  - historical_dev_to_main_promotion_validator_drift
  - public_alpha_defer_queue_validator_drift
```

This is a validator repair only. It does not change runtime/product behavior.


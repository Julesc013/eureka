# CONTRACT-SCHEMA-DRIFT-REPAIR-01

This package records the focused repair of the residual
`contract_schema_drift` family from the external full-discovery ingest.

The targeted failure was the TSIS validator. Current repo evidence shows that
`SURFACE-KERNEL-00` and `BASELINE-RENDERERS-00` completed after `TSIS-00`, so
runtime surface files are now expected current-repo files. The repair makes the
validator phase-aware without changing runtime behavior or live contracts.

Read `REPAIR_REPORT.md` for the result and `NEXT_TASK_RECOMMENDATION.md` for
the next gate.


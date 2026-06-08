# Validator Expectation Audit

## Validator

`scripts/validate_temporal_semantic_interface_system.py`

## Stale Expectation

The validator originally treated current existence of selected
`runtime/surface/**` files as proof that `TSIS-00` violated its boundary.

That was accurate immediately after `TSIS-00`, but stale after the current repo
completed `SURFACE-KERNEL-00` and `BASELINE-RENDERERS-00`.

## Updated Expectation

The validator now separates:

- TSIS-00 result flags from `control/inventory/tsis_00_result.json`
- current repo phase state from `.aide/queue/index.yaml`

It still validates that TSIS-00 itself did not claim runtime behavior.

## Regression Coverage

`tests/scripts/test_validate_temporal_semantic_interface_system.py` now covers:

- current repo passes with completed surface runtime phases
- `runtime/surface/kernel.py` fails when no surface runtime phase is complete
- `runtime/surface/kernel.py` is allowed after `SURFACE-KERNEL-00` completion


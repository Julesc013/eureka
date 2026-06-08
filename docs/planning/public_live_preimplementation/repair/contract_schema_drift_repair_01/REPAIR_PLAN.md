# Repair Plan

## Decision

Repair the validator expectation, not live contracts, runtime behavior, or
surface code.

## Steps

1. Reproduce the focused TSIS validator failure.
2. Confirm the failing files are current later-phase `runtime/surface/**` files.
3. Teach the validator to read completed surface runtime phases from
   `.aide/queue/index.yaml`.
4. Permit the known runtime surface phase files only when a later phase is
   complete.
5. Add focused regression tests for both the denied and allowed paths.
6. Update the repair evidence package and queue recommendation.

## Files Not Repaired

No live contract schema file required changes.

No `runtime/surface/**` behavior changed.

No generated contract index was regenerated.


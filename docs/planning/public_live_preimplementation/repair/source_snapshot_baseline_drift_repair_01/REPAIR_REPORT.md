# Repair Report

## Task

`SOURCE-SNAPSHOT-BASELINE-DRIFT-REPAIR-01`

## Status

`PASS_WITH_WARNINGS`

## Summary

The external ingest reported one source/snapshot baseline family:
`unittest-e31dd26eed981165`.

Focused rerun showed the LOCAL-09 validator path is already green on the current
tree. The remaining failing label was the source-observation seam validator. It
failed because `runtime/source/observation/internet_archive_live_transport.py`
still contained a Windows shell fallback for TLS failures. That fallback imported
`subprocess` and carried reserved vocabulary in the source-observation seam.

The repair removes that alternate shell execution path. TLS failures now degrade
through the normal redacted transport-error response. The IA live metadata lane
still passes its own bounded urllib validation, and the R0 source-observation
seam returns to zero forbidden vocabulary and zero network dependencies.

## Gates

Public alpha remains blocked.

`dev -> main` promotion remains blocked.

The source/snapshot release gate remains blocked until remaining drift families
are repaired or externalized and external full discovery is rerun.

## No Broad Work

No directories were moved.

No new top-level roots were added.

No public source fanout, downloads, Wayback replay, public launch, or promotion
behavior was added.


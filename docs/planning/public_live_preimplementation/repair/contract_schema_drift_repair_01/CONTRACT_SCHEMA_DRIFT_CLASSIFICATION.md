# Contract Schema Drift Classification

| Label | Classification | Evidence | Minimal repair path | Risk |
|---|---|---|---|---|
| TSIS validator rejects current `runtime/surface/**` files | `tsis_phase_boundary_drift` and `runtime_surface_phase_drift` | Queue and implementation docs show `SURFACE-KERNEL-00` and `BASELINE-RENDERERS-00` completed after `TSIS-00`. | Make the TSIS validator read current phase state and allow `runtime/surface/**` files only after a completed surface runtime phase. | Low to medium; a blanket allowlist would hide real early-phase drift, so tests preserve the pre-phase failure. |

## Why This Is Not Broader Architecture Drift

Architecture-boundary validators are already green in focused validation. This
repair does not move roots or change dependency law.

## Why This Is Not Generated Artifact Drift

No generated artifacts are stale or regenerated. The drift is validator phase
interpretation.

## Why This Is Not Queue Handoff Drift

The queue already records completed `SURFACE-KERNEL-00` and
`BASELINE-RENDERERS-00`. This task uses that queue state instead of changing the
handoff claim itself.


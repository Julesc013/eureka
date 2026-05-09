# SYNC-GUARD-01 - Multi-Machine Git Guard

This audit records the control/tooling guard added after the OBS and Track B merge recovery.

## Added

- Git task-state guard script: `scripts/check_git_task_state.py`
- Sync guard policy inventories under `control/inventory/git/`
- AIDE sync prompt templates for finish, merge, and rescue workflows
- Multi-machine Git workflow docs under `docs/operations/`
- Temp-repo operation tests for guard behavior

## Why

The recent recovery proved that local-only work, stale local `main`, and active merge metadata can make a normal merge feel impossible. This task adds a small preflight and workflow vocabulary so future work stops early in unsafe states.

## Boundary

This is control/tooling/docs/test work only. It changes no Eureka product behavior, public routes, hosting, live probes, source connectors, downloads, accounts, telemetry, WorkUnit execution, evidence truth, or master-index state.

## Validation

See `validation.md`.

## Next

`HUMAN-OBS-REVIEW-01 - Review OBS candidate packet`

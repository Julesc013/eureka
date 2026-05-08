# TRACK-B-05 WorkUnit Result Contract

This audit pack adds the first Eureka WorkUnit result contract.

WorkUnit results follow WorkUnit contracts because bounded tasks need an
equally bounded, replay-safe output envelope before any dry-run runner or
runtime planning exists.

## Added

- `contracts/node/work_unit_result.v0.json`
- WorkUnit result policy, status, output, review, and recovery inventories
- six compact WorkUnit result examples
- WorkUnit result reference, architecture, and operations docs
- `scripts/validate_eureka_workunit_result.py`
- `tests/contracts/test_eureka_workunit_result.py`

## Boundary

No WorkUnit runner, WorkUnit execution, node runtime, source access, network
calls, model/provider calls, local state, pack import runtime, review runtime,
downloads, uploads, accounts, telemetry, accepted evidence, public truth, or
master-index mutation was added.

## Validation

```powershell
python scripts/validate_eureka_workunit_result.py
python -m unittest discover -s tests -t .
```

## Next Task

TRACK-B-06 - Local foundry state contract

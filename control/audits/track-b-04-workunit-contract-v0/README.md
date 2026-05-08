# TRACK-B-04 WorkUnit Contract

This audit pack adds the first Eureka WorkUnit contract.

WorkUnits follow node manifests, node policies, and node capabilities because
bounded work should reference an identified node shape, a policy envelope, and
a governed capability vocabulary before any runner exists.

## Added

- `contracts/node/work_unit.v0.json`
- WorkUnit type, policy, idempotency, action, input/output, and review-gate
  inventories under `control/inventory/nodes/`
- seven compact WorkUnit examples under `examples/work_units/`
- WorkUnit reference, architecture, and operations docs
- `scripts/validate_eureka_workunit.py`
- `tests/contracts/test_eureka_workunit.py`

## Boundary

No WorkUnit runner, node runtime, source access, network calls, model/provider
calls, local state, pack import runtime, review runtime, downloads, uploads,
accounts, telemetry, accepted evidence, public truth, or master-index mutation
was added.

## Validation

```powershell
python scripts/validate_eureka_workunit.py
python -m unittest discover -s tests -t .
```

## Next Task

TRACK-B-05 - WorkUnit result contract

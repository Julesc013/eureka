# TRACK-B-06 Local Foundry State Contract

This audit pack adds the first Eureka Local Foundry State contract.

Local foundry state follows WorkUnit result contracts because future nodes need
a bounded place to draft, dry-run, review, and package local/private outputs
without treating those outputs as truth.

## Added

- `contracts/node/local_foundry_state.v0.json`
- local foundry state policy, kind, path, privacy, export, and reset
  inventories
- five compact Local Foundry State examples
- Local Foundry State reference, architecture, and operations docs
- `scripts/validate_local_foundry_state.py`
- `tests/contracts/test_local_foundry_state.py`

## Relationship To Staging

The contract builds on the local quarantine and staging model by naming future
private roots as policy references only. It distinguishes committed audit
evidence from ignored private state and from reviewed future exports.

## Boundary

No local foundry runtime, local state directory, node runtime, WorkUnit runtime,
source access, network calls, model/provider calls, live probes, source sync,
downloads, uploads, accounts, telemetry, accepted evidence, public truth, or
master-index mutation was added.

## Deferred

Query observation runtime, candidate store, source cache, evidence ledger,
review queue, and pack builder runtime work remain future tasks.

## Validation

```powershell
python scripts/validate_local_foundry_state.py
python -m unittest discover -s tests -t .
```

## Next Task

TRACK-B-07 - Query observation runtime

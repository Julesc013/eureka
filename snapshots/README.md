# Snapshots

`snapshots/` contains snapshot schemas and deterministic reviewed-record
examples.

Snapshots are read-only data products. They may support public-alpha routes,
static projections, relay experiments, and future native clients, but they do
not perform live source actions, mutate stores, include private local state,
include raw live source responses, deploy a public service, or claim
production/public launch readiness.

Use:

```powershell
python scripts/validate_snapshot_relay.py
python scripts/validate_static_snapshot.py
```

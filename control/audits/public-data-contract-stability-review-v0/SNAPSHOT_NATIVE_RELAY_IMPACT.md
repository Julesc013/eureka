# Snapshot, Native, And Relay Impact

Signed snapshots, future native clients, and future relay prototypes may use the
same stable-draft field list as their first public-data baseline.

Impact on snapshots:

- Snapshot metadata may reference `source_summary.sources[].source_id`, source
  posture fields, route basics, checksum/snapshot contract posture, and no-live
  safety flags.
- Snapshots must not treat public JSON as production-authentic or fully stable.
- Snapshot consumers must still follow the Signed Snapshot Consumer Contract.

Impact on native clients:

- Native client planning may consume stable-draft public data for read-only
  display and demo skeleton planning.
- Native clients must version-check public data and treat experimental fields as
  display-only.
- Native clients must not add downloads, installs, private cache, telemetry,
  accounts, live probes, or production API assumptions from this review.

Impact on relay:

- Relay Prototype Planning may use stable-draft public data and seed snapshots
  as allowlisted read-only inputs after explicit approval.
- Relay work must not expose internal repo paths, private data, live backend
  proxying, write/admin routes, or live probes.
- Experimental nested policy objects are useful status displays, not relay API
  contracts.

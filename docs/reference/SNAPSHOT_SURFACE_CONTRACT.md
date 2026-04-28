# Snapshot Surface Contract

Snapshot surfaces are future/deferred. No `/snapshots/` artifact, signed
bundle, snapshot manifest, or offline snapshot contract is implemented yet.

Future snapshots must be static, deterministic, and safe to copy. A later
Signed Snapshot Format v0 should define:

- bundle layout
- manifest schema
- checksum list
- future signature policy
- data/source/eval/demo inputs
- base-path behavior
- no private local paths
- no executable download claim

Snapshots are the preferred future path for offline clients and clients that
cannot consume modern hosted TLS reliably. They must not imply live backend,
live probe, or production API availability.

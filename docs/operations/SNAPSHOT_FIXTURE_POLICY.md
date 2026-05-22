# Snapshot Fixture Policy

D-BUNDLE-01 snapshots are fixture-only and local.

Allowed inputs are explicit files under `examples/snapshots/`, selected example/audit paths, or temp test directories. Private user files, downloaded payloads, mirrored files, installer payloads, executable payloads, credentials, cookies, and tokens are not valid fixture inputs.

Allowed outputs are `examples/snapshots/`, `control/audits/**/generated/`, and temp test directories.

Forbidden outputs include `site/dist/`, `site/dist/data/public_index/`, `runtime/`, `contracts/`, publication inventories, master-index roots, relay roots, hosted roots, and local private-state roots.

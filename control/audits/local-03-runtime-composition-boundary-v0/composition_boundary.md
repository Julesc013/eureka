# Composition Boundary

LOCAL-03 introduces `runtime/local/appliance` as the stable runtime kernel for the Local Appliance track.

The boundary opens an explicit initialized instance root, loads versioned instance configuration, loads the store manifest, loads migration state, and opens the source cache, evidence ledger, review queue, and reviewed public index stores through manifest relative paths.

Future service, workbench, workers, and tests should use `open_local_appliance(instance_path)` instead of opening SQLite paths directly.

The boundary is not a server and not a worker. It does not run source probes, create review decisions, rebuild indexes, expose LAN, deploy, or claim production/public readiness.

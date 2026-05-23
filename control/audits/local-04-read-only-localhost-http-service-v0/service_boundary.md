# Service Boundary

LOCAL-04 adds a read-only HTTP adapter over `runtime/local/appliance`.

The service opens `LocalApplianceRuntime` with an explicit instance path. It reads status and reviewed public index records through that runtime object. It does not open ad hoc SQLite paths.

Allowed bind hosts are `127.0.0.1` and `localhost`. Wildcard and LAN hosts are rejected.

The service starts no source probes, workers, agents, model/provider calls, or deployment actions.

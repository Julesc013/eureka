# Read-Only Boundary

LOCAL-04 rejects mutating HTTP methods:

- POST
- PUT
- PATCH
- DELETE

The service has no route for source probes, WorkUnits, review decisions, index rebuilds, site generation, deployment, or provider calls.

The underlying runtime is opened in read-only mode through `open_local_appliance(instance_path, read_only=True)`.

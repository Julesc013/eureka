# Local Appliance Capability Map

LOCAL-14 records the capability map in
`control/inventory/local_appliance_capability_matrix.json`.

Required capabilities are:

- explicit instance root
- instance schema and migration guard
- runtime composition boundary
- read-only localhost service
- HTML workbench
- hardened status, object, source, and absence pages
- WorkUnit queue
- review decision loop
- reviewed-index rebuild
- deterministic worker runner
- auto-test and auto-search harness
- LAN binding safety gate
- LAN read-only smoke
- clean-machine bootstrap

Every future track must use these boundaries when applicable rather than
claiming scaffold-only completion.

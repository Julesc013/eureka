# Search Hunt Local Appliance Integration

HUNT uses the Local Appliance product kernel: explicit instance root, runtime composition, reviewed public index, WorkUnit queue, deterministic worker runner, review queue, evidence ledger, HTML workbench, and auto-test/search harness. It must not use ad hoc stores or direct master-index mutation.

HUNT-01 adds `search_hunt` as a manifest-backed store in the explicit instance. Runtime composition opens it as `runtime.search_hunt`, and status reports it with source probes, WorkUnit creation, and model providers disabled.

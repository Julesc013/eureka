# Search Hunt Local Appliance Integration

HUNT uses the Local Appliance product kernel: explicit instance root, runtime composition, reviewed public index, WorkUnit queue, deterministic worker runner, review queue, evidence ledger, HTML workbench, and auto-test/search harness. It must not use ad hoc stores or direct master-index mutation.

HUNT-01 adds `search_hunt` as a manifest-backed store in the explicit instance. Runtime composition opens it as `runtime.search_hunt`, and status reports it with source probes, WorkUnit creation, and model providers disabled.

HUNT-02 reads `runtime.search_hunt` from the local HTTP service and renders server-side workbench pages. The workbench stays inside the Local Appliance boundary and does not bypass the store manifest, review queue, evidence ledger, or reviewed index.
## SearchNeed Store

The Local Appliance manifest now includes the `search_need` store at `db/search_need.sqlite`. Runtime composition opens this store alongside `search_hunt`, `workunit_queue`, review, evidence, cache, and reviewed index stores.

SearchNeed writes remain local appliance mutations only and do not bypass the hunt/exhaustion path.

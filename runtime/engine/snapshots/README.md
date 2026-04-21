# Engine Snapshots

`runtime/engine/snapshots/` holds bounded engine-side export artifacts that are more portable than a single manifest while still remaining bootstrap-scale.

Current bootstrap scope:

- build a deterministic, self-contained resolution bundle ZIP for an already-normalized synthetic match
- carry the bootstrap `resolved_resource_id` through bundle metadata, manifest content, and normalized-record export
- inspect a previously exported deterministic resolution bundle from local bytes or a local file path
- keep bundle contents local, inspectable, and stdlib-only
- avoid restore, import, installer, or durable preservation semantics

This is the first portable offline export and readback seam only. The recovered `resolved_resource_id` remains bootstrap-scale and does not define a final snapshot, import, restore, reconstruction, or global identity contract.

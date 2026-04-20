# Engine Snapshots

`runtime/engine/snapshots/` holds bounded engine-side export artifacts that are more portable than a single manifest while still remaining bootstrap-scale.

Current bootstrap scope:

- build a deterministic, self-contained resolution bundle ZIP for an already-normalized synthetic match
- inspect a previously exported deterministic resolution bundle from local bytes or a local file path
- keep bundle contents local, inspectable, and stdlib-only
- avoid restore, import, installer, or durable preservation semantics

This is the first portable offline export and readback seam only. It does not define a final snapshot, import, restore, or reconstruction contract.

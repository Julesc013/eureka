# Engine Actions

`runtime/engine/actions/` holds bounded engine-side action behavior.

Current bootstrap scope:

- build a deterministic machine-readable resolution manifest from an already-normalized synthetic match
- keep export behavior local, auditable, and stdlib-only
- avoid installer, download, snapshot-restore, or workflow semantics

This is a bootstrap action seam only. It does not define final reconstruction or preservation behavior.

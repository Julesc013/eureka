# Engine Store

`runtime/engine/store/` holds the first deterministic local store seam for exported
bootstrap artifacts.

Current bootstrap scope:

- compute stable content-addressed artifact identities using `sha256:<hex>`
- store exported manifest JSON and bundle ZIP payloads in a small local filesystem layout
- keep metadata, object paths, and target indexes deterministic and easy to inspect
- support local list and readback by target ref or artifact identity
- avoid databases, eviction policy, multi-user locking, restore, import, or preservation claims

This is a bootstrap local store or cache seam only. It does not define a final
database, cache, preservation, or deployment architecture.

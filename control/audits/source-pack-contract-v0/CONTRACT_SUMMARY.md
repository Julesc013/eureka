# Contract Summary

Source packs are portable directories or archive-like bundles that carry
source metadata, public-safe evidence inputs, tiny deterministic fixtures,
rights/privacy notes, and checksums.

The governed manifest is `SOURCE_PACK.json`, described by
`contracts/packs/source_pack.v0.json`.

Source Pack Contract v0 answers how a pack declares:

- source identity and source families
- source records that align with Source Registry v0 vocabulary
- public-safe evidence and representation files
- fixture and payload policy
- rights/access and privacy posture
- prohibited behavior
- checksum coverage
- validation command and lifecycle status

The contract does not make pack contents canonical. A pack source record is not
automatically accepted into `control/inventory/sources/`, a local index, public
search, snapshots, relay clients, native clients, or a hosted/master index.

# Source Registry Contracts

`contracts/source_registry/` holds the draft governed schema set for Source
Registry v0.

Current scope:

- one draft `source_record` schema for individual source entries
- one draft aggregate `source_registry` schema for list-shaped documents
- one draft `source_capability` schema for bounded capability flags
- one draft `source_coverage` schema for the coverage-depth ladder

Source Coverage and Capability Model v0 adds explicit metadata for what a
registered source can currently do and how deeply it is indexed. The coverage
depth ladder is:

0. `source_known`
1. `catalog_indexed`
2. `metadata_indexed`
3. `representation_indexed`
4. `content_or_member_indexed`
5. `action_indexed`

Depth is descriptive, not aspirational. Placeholder sources remain
`source_known` until a later recorded-fixture or connector slice changes their
actual bounded coverage.

Source Registry v0 is intentionally bounded:

- inventory and validation only
- no live sync
- no crawling
- no source health scoring
- no trust scoring
- no auth
- no async scheduling
- no live probing
- no new source connectors

These schemas are draft and provisional. They help keep source records explicit
and inspectable without pretending the long-term source model is finished.

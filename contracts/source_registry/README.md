# Source Registry Contracts

`contracts/source_registry/` holds the draft governed schema set for Source
Registry v0.

Current scope:

- one draft `source_record` schema for individual source entries
- one draft aggregate `source_registry` schema for list-shaped documents

Source Registry v0 is intentionally bounded:

- inventory and validation only
- no live sync
- no crawling
- no source health scoring
- no trust scoring
- no auth
- no async scheduling

These schemas are draft and provisional. They help keep source records explicit
and inspectable without pretending the long-term source model is finished.

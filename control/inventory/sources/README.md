# Source Inventory

This directory holds the governed seed records for Source Registry v0.

Current scope:

- inventory and labeling only
- explicit source roles, surfaces, connector ownership, and posture metadata
- active fixture-backed seed sources plus honest placeholder or future entries

Source Registry v0 does **not** imply:

- live sync
- crawling
- source health scoring
- trust scoring
- authentication
- async workers
- production deployment semantics

Seed records currently cover:

- `synthetic-fixtures`
- `github-releases-recorded-fixtures`
- `internet-archive-placeholder`
- `wayback-memento-placeholder`
- `software-heritage-placeholder`
- `local-files-placeholder`

Placeholder and future records are planning anchors only. They must not be
described as implemented connectors until runtime code lands for them.

# Logical Graphs

Eureka's architecture should be reasoned about through six logical graphs.
These are conceptual graphs, not a requirement to deploy six graph databases.

## 1. Object Graph

This graph describes what the thing is.

Examples:

- software product
- software release
- driver
- package
- book
- article
- manual
- website
- dataset
- source repository
- public record

## 2. Representation Graph

This graph describes how the thing appears.

Examples:

- ZIP
- ISO
- PDF
- EPUB
- WARC or WACZ
- installer
- scan
- OCR text
- manifest
- extracted member
- source archive

## 3. Temporal Graph

This graph describes when and which state.

Examples:

- release date
- capture date
- edition
- build
- patch level
- service pack
- validity window
- latest compatible state
- historically authentic version

## 4. Claim and Provenance Graph

This graph describes who says what and on what evidence.

Examples:

- source A claims file X is version 2.1
- source B claims the same file is version 2.0
- a hash links two artifacts
- a manual claims Windows 98 compatibility
- release notes claim support ended after a given version

Disagreement belongs here. The resolver should preserve disagreement rather than
erase it too early.

## 5. Access and Action Graph

This graph describes what the user can do next.

Examples:

- inspect
- view or read
- fetch
- download
- mirror
- install later
- mount later
- emulate later
- cite
- export manifest
- save to local archive
- compare versions
- inspect provenance

## 6. User and Strategy Graph

This graph is private and local by default. It should influence strategy and
ranking without rewriting objective facts.

Examples:

- user OS and hardware constraints
- preferred formats
- trusted sources
- current task context
- strategy profiles
- explicit user goals

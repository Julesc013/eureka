# Local Bundle Fixtures Connector

This connector loads committed ZIP fixture payloads from this repository. It is
not arbitrary local-files ingestion.

The fixture corpus exists to exercise bounded bundle representation, member
listing, and member readback behavior for later member-level discovery work.
Old-Platform Source Coverage Expansion v0 adds three more tiny text-only ZIP
fixtures for Windows 98 registry repair, Windows XP browser/tools notes, and
legacy Creative CT1740 plus 3Com 3C905 driver support members. These fixtures
are committed repo data and do not enable arbitrary local filesystem ingestion.

It does not add:

- user filesystem crawling
- public-alpha local path access
- live source probing
- background import
- installer/download automation

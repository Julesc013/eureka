# Local Bundle Fixtures Connector

This connector loads committed ZIP fixture payloads from this repository. It is
not arbitrary local-files ingestion.

The fixture corpus exists to exercise bounded bundle representation, member
listing, and member readback behavior for later member-level discovery work.

It does not add:

- user filesystem crawling
- public-alpha local path access
- live source probing
- background import
- installer/download automation

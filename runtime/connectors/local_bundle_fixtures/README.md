# Local Bundle Fixtures Connector

This connector loads committed ZIP fixture payloads from this repository. It is
not arbitrary local-files ingestion.

The fixture corpus exists to exercise bounded bundle representation, member
listing, and member readback behavior for later member-level discovery work.
Old-Platform Source Coverage Expansion v0 adds three more tiny text-only ZIP
fixtures for Windows 98 registry repair, Windows XP browser/tools notes, and
legacy Creative CT1740 plus 3Com 3C905 driver support members. These fixtures
are committed repo data and do not enable arbitrary local filesystem ingestion.

More Source Coverage Expansion v1 extends those committed ZIP fixtures with
additional tiny text-safe members for Firefox XP candidate evidence, a blue
FTP-client XP installer stand-in, Windows 98 registry repair artifact evidence,
and extra Windows 7 utility members. The payloads are deterministic fixtures
only and include no real binaries.

It does not add:

- user filesystem crawling
- public-alpha local path access
- live source probing
- background import
- installer/download automation

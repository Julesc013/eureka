# Validation Rules

`scripts/validate_source_pack.py` validates the example pack by default and can
validate another pack with `--pack-root`.

The validator checks:

- `SOURCE_PACK.json` exists and parses.
- required manifest fields and lifecycle status are present.
- source records and evidence records parse as JSONL.
- source records declare source family, coverage depth, connector mode,
  capabilities, limitations, rights/access notes, and disabled live/network
  posture.
- public/shareable packs are `public_safe`.
- prohibited behavior lists include live fetch, arbitrary URL fetch, scraping,
  crawling, executables, installers, downloads, uploads, credentials, private
  path publication, raw private file export, malware-safety claims,
  rights-clearance claims, master-index auto-acceptance, and runtime plugin
  execution.
- `CHECKSUMS.SHA256` matches declared pack files.
- no executable/archive payload extensions appear in the example pack.
- no live URL text, private local path, credential key, import behavior, network
  behavior, or unsupported acceptance claim appears.

The validator does not import, index, upload, execute, or contact a network.

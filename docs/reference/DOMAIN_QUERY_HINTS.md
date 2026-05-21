# DOMAIN Query Hints

DOMAIN query hints are small interpretation packets embedded in DOMAIN packs.
They list:

- `promote_terms`
- `suppress_terms`
- `source_family_preferences`
- `query_classes`
- review requirements

Examples:

- `legacy_software` promotes portable apps, installers, versioned releases, and
  compatibility evidence while suppressing OS ISOs when the user wants apps and
  modern scam/updater tools.
- `driver_support_media` promotes model, chipset, OEM support disc, and member
  path signals while suppressing generic driver updater sites.
- `frontier_resolution_media` promotes format lineage, source provenance, best
  representation, and collection/uploader trails while suppressing generic
  low-quality reposts.
- `package_source_release` promotes release tags, source archives, package
  metadata, and checksums if available while suppressing install commands
  without source evidence.

Hints are not truth. They perform no live source behavior, no source probes, no
downloads, no extraction, no model calls, no deployment, and no index mutation.
Unsafe actions remain blocked.

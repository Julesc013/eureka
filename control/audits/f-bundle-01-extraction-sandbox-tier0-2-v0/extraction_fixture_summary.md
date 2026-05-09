# Extraction Fixture Summary

Fixtures are synthetic and committed under `examples/extraction/fixtures/`.

- `zip_basic`: safe ZIP for Tier 0 and Tier 1.
- `zip_manifest`: safe ZIP with `package.json` for Tier 2 manifest candidate extraction.
- `tar_basic`: safe TAR for Tier 1.
- `path_traversal_blocked`: ZIP with a blocked `../` member.
- `archive_bomb_blocked`: tiny ZIP that trips compression-ratio policy.

No fixture contains private files, credentials, installers, downloaded payloads, malware samples, or executable behavior.

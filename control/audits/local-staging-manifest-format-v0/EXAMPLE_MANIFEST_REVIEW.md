# Example Manifest Review

The synthetic example lives at:

`examples/local_staging_manifests/minimal_local_staging_manifest_v0/`

It contains:

- `LOCAL_STAGING_MANIFEST.json`
- `README.md`
- `CHECKSUMS.SHA256`

The example uses repo-relative synthetic references only. It records two
staged pack references, three staged entities, hard no-mutation guarantees, and
future reset/delete/export policy. It contains no real local paths, secrets,
executables, raw databases, user data, staged runtime state, or pack payload
copies.

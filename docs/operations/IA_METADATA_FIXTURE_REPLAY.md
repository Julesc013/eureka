# IA Metadata Fixture Replay

Fixture replay is the only execution mode in IA-BUNDLE-01.

## Inputs

Fixtures live under:

`examples/connectors/internet_archive/fixtures/`

They must be committed, synthetic or public-safe, stable for tests, and
normalizable without network access. They must not contain secrets,
credentials, cookies, private paths, live-call evidence, downloaded binaries,
or rights/malware/installability claims.

## Outputs

Expected normalized examples live under:

`examples/connectors/internet_archive/normalized/`

Audit previews live under:

`control/audits/ia-bundle-01-metadata-connector-foundation-v0/generated/`

## Commands

```text
python scripts/normalize_ia_metadata_fixture.py --input examples/connectors/internet_archive/fixtures/software_item_metadata.json --check
python scripts/validate_ia_metadata_connector_foundation.py
```

The CLI writes no files unless explicit output paths are provided.

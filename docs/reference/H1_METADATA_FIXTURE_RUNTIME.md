# H1 Metadata Fixture Runtime

H1-BUNDLE-02 adds fixture-only normalizers for the seven H1 metadata sources. The runtime reads committed public-safe fixtures and emits normalized metadata records, source-cache candidate previews, evidence candidate previews, output envelopes, and replay reports.

It is not live source access, source sync, scraping, downloading, evidence acceptance, or public truth creation.

Validation:

```bash
python scripts/validate_h1_metadata_fixture_runtime.py
python scripts/replay_h1_metadata_fixtures.py --check
```

# H1 Metadata Wave Source Packs

H1-BUNDLE-01 defines the first metadata-wave policy packs after the Internet Archive reference pattern and the H0 Source OS foundation.

The wave covers:

- Wayback / CDX / Memento
- GitHub Releases
- PyPI
- npm Registry
- Software Heritage
- Repology
- OSV

These records are policy-pack-only. They describe source posture, connector-family fit, fixture requirements, output boundaries, coverage previews, and scorecard expectations. They do not approve live source access.

## Current Boundary

- No network, API, browser, model, or provider call is allowed.
- No source sync or live connector runtime is enabled.
- No package, release asset, source archive, item file, or binary download is allowed.
- No scraping, crawling, unbounded search, or public-query fanout is allowed.
- No source observation, evidence, candidate, pack, public record, public index, or master index is accepted or mutated.

## Pack Artifacts

- `control/inventory/source_packs/h1_metadata_wave_source_pack_policy.json` records the wave-level policy.
- `control/inventory/source_packs/h1_metadata_wave_sources.json` lists the seven source records and their current no-access posture.
- `examples/packs/source/h1_metadata_wave_source_pack_manifest_v0.json` is the portable draft manifest.
- `examples/packs/source/h1_metadata_wave_policy_pack_v0.json` aggregates the per-source policy-pack refs.

## Validation

Run:

```bash
python scripts/validate_h1_metadata_wave_policy_packs.py
python scripts/summarize_h1_metadata_wave_sources.py --check
```

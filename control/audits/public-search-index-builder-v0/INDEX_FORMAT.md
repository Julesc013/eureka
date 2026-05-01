# Index Format

The committed artifact root is `data/public_index/`.

Required generated files:

- `build_manifest.json`
- `source_coverage.json`
- `index_stats.json`
- `search_documents.ndjson`
- `checksums.sha256`

`search_documents.ndjson` contains one public-safe JSON document per line.
Documents include identity, source, evidence, compatibility, action posture,
warnings, limitations, and deterministic `search_text`.

No SQLite binary is committed in P55.

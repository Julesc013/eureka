# Public Index Status

Classification: `implemented_static_artifact`.

Artifact paths:

- `data/public_index/search_documents.ndjson`
- `data/public_index/index_stats.json`
- `data/public_index/source_coverage.json`
- `data/public_index/build_manifest.json`
- `data/public_index/checksums.sha256`
- `site/dist/data/public_index_summary.json`

Observed document count: 584.

Current status:

- Index builder status: validator/check commands exist and pass in the current
  repo.
- Index validator status: governed public-search index validation exists.
- Static index summary status: generated and valid.
- Source cache integration: not integrated.
- Evidence ledger integration: not integrated.
- Mutation status: public search does not mutate public/local/runtime/master
  indexes.

Limitations:

- Public index is fixture/recorded metadata and local-index-only.
- Public index is not proof of global source coverage, rights clearance, malware
  safety, installability, or source truth.


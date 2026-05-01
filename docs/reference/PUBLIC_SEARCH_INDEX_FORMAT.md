# Public Search Index Format v0

Public Search Index v0 is a committed, deterministic, public-safe index bundle
for `local_index_only` public search.

## Artifact Root

`data/public_index/`

Required files:

- `build_manifest.json`
- `source_coverage.json`
- `index_stats.json`
- `search_documents.ndjson`
- `checksums.sha256`

The committed bundle is JSON/NDJSON text only. `eureka.sqlite` is not committed
in v0; SQLite and FTS5 availability are detected and recorded, but the runtime
uses deterministic lexical fallback over the generated documents.

## Document Model

Each line in `search_documents.ndjson` is a JSON object with stable public fields:

- `doc_id`, `record_id`, `record_kind`
- `title`, `subtitle`, `description`
- `source_id`, `source_family`, `source_status`, `source_coverage_depth`
- `object_family`, `representation_kind`, `member_path`, `parent_ref`
- `platform_terms`, `architecture_terms`, `version_terms`, `date_terms`, `keyword_terms`
- `compatibility_summary`, `evidence_summary`
- `result_lane`, `user_cost_summary`
- `allowed_actions`, `blocked_actions`
- `warnings`, `limitations`
- `public_target_ref`
- `search_text`

The index must not include absolute local paths, credentials, executable
payloads, private cache roots, raw user uploads, live API responses, or raw
copyrighted payload dumps.

P57 Public Search Safety Evidence v0 validates this bundle as a public-safe
artifact: document counts match the static summary, live/private/executable
flags are false, dangerous actions are not enabled, and no private path or
secret marker is recorded in the evidence output.

P56 exposes a static summary of this bundle at
`site/dist/data/public_index_summary.json`. That summary is publication data,
not dynamic search execution and not a hosted backend claim.

## Runtime Contract

Public search may load this bundle from the repository-owned
`data/public_index` path. Public requests must not choose an index path,
database path, source root, local path, store root, or filesystem root.

Result cards remain governed by `PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md`.
Actions stay safe: inspect, view source, view provenance, and read public-safe
summary text. Downloads, uploads, installs, execution, live probes, and arbitrary
URL fetching remain blocked.

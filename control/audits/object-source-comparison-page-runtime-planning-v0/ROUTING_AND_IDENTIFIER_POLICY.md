# Routing And Identifier Policy

Future safe routes:

- /object/{object_id}
- /source/{source_id}
- /comparison/{comparison_id}
- /api/v1/object/{object_id}
- /api/v1/source-page/{source_id}
- /api/v1/comparison/{comparison_id}

Allowed IDs:

- public-index object IDs
- public-index source IDs
- public-index comparison IDs
- reviewed page IDs
- generated stable slugs derived from reviewed records

Forbidden IDs:

- local paths
- absolute paths
- arbitrary URLs
- raw source URLs
- unreviewed package names
- unreviewed repository names
- unreviewed SWHIDs
- unreviewed URI-R values
- uploaded filenames
- private cache keys
- secrets/tokens
- database paths

Rules:

- IDs must be normalized, bounded, public-safe, and not interpreted as filesystem paths.
- Unknown IDs return a stable error envelope or absence/unknown page, not file access.
- Page route parameters must never trigger live source calls.
- Route parameters must never choose page_path, source_cache_path, evidence_ledger_path, candidate_path, promotion_path, index_path, store_root, local_path, database path, source root, URL, live source, emulator path, VM path, package manager path, or filesystem root.

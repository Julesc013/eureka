# Local Public Search Integration

`build_demo_public_search_public_api()` now loads
`data/public_index/search_documents.ndjson` when present. The local public API
reports `index_status: generated_public_search_index` and document count 584.

Public requests still cannot choose an index path or source root. The generated
index root is repository-owned and fixed.

The P54 hosted wrapper remains undeployed, but its config check now requires the
generated public index file to be present.

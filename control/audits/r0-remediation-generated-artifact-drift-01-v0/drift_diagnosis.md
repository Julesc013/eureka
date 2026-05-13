# Drift Diagnosis

Full unittest discovery previously failed and left generated outputs dirty.

The reproduced drift covered:

- `data/public_index/checksums.sha256`
- `data/public_index/search_documents.ndjson`
- demand dashboard example `CHECKSUMS.SHA256` files
- committed `site/dist` static-site outputs and data manifests

The test-order-sensitive source was `tests/scripts/test_static_site_generator.py`, where the JSON build test used the default static site output path. That test now writes to a temporary output path.

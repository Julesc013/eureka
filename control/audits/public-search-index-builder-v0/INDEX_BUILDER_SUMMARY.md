# Index Builder Summary

P55 adds `scripts/build_public_search_index.py` and committed text artifacts
under `data/public_index/`.

The builder converts the current controlled fixture/recorded catalog and source
registry into 584 public search documents. `--rebuild` updates artifacts;
`--check` regenerates in a temporary directory and compares against committed
files.

The public search runtime now loads `data/public_index/search_documents.ndjson`
first. If the committed index is absent in local development it can fall back to
the previous in-memory controlled catalog, but the hosted wrapper config check
requires the generated index file to be present.

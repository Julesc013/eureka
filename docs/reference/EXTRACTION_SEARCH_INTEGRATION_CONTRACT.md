# Extraction Search Integration Contract

`extraction_search_integration.v0` is an offline bundle of extraction-result refs, candidate-effect refs, search gaps, review seeds, WorkUnit seeds, source-cache/evidence previews, and a local search preview. It is not public search behavior and cannot mutate public search, public index, master index, candidate store, evidence ledger, or review queue.

Validate with `python scripts/validate_extraction_search_integration.py`.

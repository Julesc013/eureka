# Engine Provenance

`runtime/engine/provenance/` holds the first bounded provenance and evidence seam for Eureka.

Current bootstrap scope:

- explicit, compact evidence summaries carried alongside normalized records
- enough structure to preserve source-backed claims through resolution, export, storage, and inspection
- no provenance graph
- no trust scores
- no cross-source merge model
- no final claim ontology or compatibility promise

This slice is intentionally small and replaceable. It preserves source-backed evidence summaries without collapsing multiple inputs into one silent truth.

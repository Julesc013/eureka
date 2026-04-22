`runtime/engine/states/` holds the first bounded object/state timeline seam for Eureka.

This slice groups already-normalized records under a bootstrap `subject_key`, produces a compact subject summary, and returns an ordered list of bounded state summaries without claiming that Eureka has a final global object identity model or a full temporal graph.

Current bootstrap rules:

- `subject_key` is a local grouping device derived from bounded target-ref structure.
- state ordering is deterministic and replaceable:
  - normalized dotted versions sort descending when recognized
  - non-version states sort by normalized state text descending
  - ties fall back to lexical `target_ref` order
- per-state output preserves compact source and evidence summaries instead of silently merging states into one answer

This slice does not introduce merge logic, trust scoring, ranking, fuzzy retrieval, or durable timeline semantics.

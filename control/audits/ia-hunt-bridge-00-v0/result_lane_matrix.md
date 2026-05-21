# Result Lane Matrix

The bridge emits Workbench result lanes using the existing result-lane projection layer.

Covered lane kinds:

- `reviewed_local_results`
- `ia_metadata_candidates`
- `source_cache_hits`
- `review_queue_items`
- `known_absence`
- `blocked_actions`
- `running_workunits`
- `deferred_deepening`
- `future_extraction_work`

Projection expectations:

- `operator_workbench` can see operational details and blocked/deferred actions.
- `public_web` hides operator-only details and keeps IA metadata as candidate information, not truth.
- `native_desktop_read_only` remains read-only and cannot mutate stores.

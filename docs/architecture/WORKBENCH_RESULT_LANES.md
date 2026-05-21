# Workbench Result Lanes

WORKBENCH-RESULT-LANES-01 adds the first concrete result-lane projection over the Search Interaction contracts. A lane is a read-only view of already-local or committed fixture-shaped records. It does not create truth, run source work, mutate stores, or promote records.

Required lanes:

- reviewed_local_results: reviewed local records, still not master or public truth.
- local_candidate_results: provisional candidate records requiring review.
- source_cache_hits: source-cache-shaped hits that are not accepted evidence.
- ia_metadata_candidates: provisional IA metadata candidates from committed examples or local previews.
- review_queue_items: review queue projections only.
- known_absence: bounded absence, not global proof.
- near_misses: uncertain possible matches.
- blocked_actions: current policy blocks.
- running_workunits: read-only WorkUnit state when available.
- deferred_deepening: future SearchNeed/WorkUnit work.
- future_extraction_work: extraction-deferred work only; extraction remains disabled.

Workbench uses the operator projection and may show provenance and operator metadata. Public and native read-only projections hide operator fields and keep unsafe actions disabled. IA-HUNT-BRIDGE-00 remains the next task because this task does not connect IA source work to Hunt execution, WorkUnit execution, or live sources.

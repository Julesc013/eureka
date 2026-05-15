# Side Effect Boundary

Allowed effects:

- WorkUnit state mutation
- WorkUnit transition history
- worker result reference recording
- worker audit reference recording
- local public-index rebuild only through token-gated `reviewed_index_rebuild_worker`

Forbidden effects:

- source probes
- extraction
- external network
- model/provider calls
- downloads
- installs
- executable actions
- source sync
- LAN operations
- deployment
- site/dist writes
- master-index mutation
- source or connector registry mutation

# Local Search And Index Impact

Current local public search is unaffected.

Rules:

- staged packs do not appear in search by default
- staged records do not alter the runtime source registry
- local public search remains `local_index_only`
- hosted public search is unaffected
- `local_index_candidate_future` requires a separate future milestone
- any future index candidate must preserve staged provenance and remain
  local/private unless separately reviewed

This milestone adds no search or index behavior.

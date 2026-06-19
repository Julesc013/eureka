# E2E Reference Contract Map

Task: `E2E-REFERENCE-CONTRACT-00`

This map selects existing contract authority where possible and uses profiles
where a runner needs a shared interpretation before a formal schema exists.

| Concept | Semantic authority | Runtime/store support | Projection support | Gap decision |
| --- | --- | --- | --- | --- |
| QueryIntent | Profile in this map | `contracts/api/search_request.v0.json`, `contracts/search/interaction/search_request_packet.v0.json`, `contracts/search/interaction/compiled_query_packet.v0.json` | search request and query-plan projections | `no_gap_use_existing_plus_profile` |
| ResolutionRun | `contracts/resolution/run/resolution_run.v0.json` | `contracts/resolution/run/run_event.v0.json`, `contracts/resolution/run/run_command.v0.json` | UI/view models and `contracts/search/interaction/resolution_run_packet.v0.json` | `no_gap_use_existing` |
| WorkUnit | `docs/reference/WORKUNIT_CONTRACT.md` plus workunit seed/result contracts | query and extraction workunit seed contracts | Workbench/search flow docs | `no_gap_use_existing_plus_profile` |
| SourceObservation | `contracts/runtime/source/observation.v0.json` | normalized observation and source cache contracts | `docs/reference/SOURCE_OBSERVATION_RUNTIME.md` | `no_gap_use_existing` |
| EvidenceSummary | `contracts/evidence/ledger/evidence_ledger_record.v0.json` as internal support; public API summary remains a projection | `contracts/stores/evidence_candidate_record.v0.json`, `contracts/stores/evidence_event.v0.json` | `contracts/api/evidence_summary.v0.json` | `projection_only_gap` |
| Candidate | Common candidate envelope profile plus specialized candidate contracts | `contracts/runtime/evidence_candidate.v0.json`, `contracts/candidates/candidate_record.v0.json`, `contracts/candidates/candidate_index_record.v0.json` | candidate pages, near-miss, identity cluster, public candidate projections | `no_gap_use_existing_plus_profile` |
| PreviewRecord | Profile in this map | result lane and candidate index records | `contracts/api/search_result_card.v0.json`, `contracts/view/result_card/result_card.v0.json` | `projection_only_gap` |
| ReviewItem | `contracts/runtime/review_item.v0.json` as queue item only | `contracts/stores/review_item_record.v0.json`, review queue store contracts | review page/view projections | `no_gap_use_existing_plus_profile` |
| ReviewDecision | `contracts/stores/review_decision.v0.json` for ledger decision events | review event store contracts | `contracts/index/master/review_decision.v0.json` is master-index future projection | `no_gap_use_existing` |
| ReviewedRecord | reviewed metadata/limited record contracts, with non-claims | reviewed public proposal is a proposal, not authority | snapshot/public projections | `no_gap_use_existing_plus_profile` |
| IndexDelta | public-index rebuild and local apply/result contracts | `contracts/stores/public_index_rebuild.v0.json`, local apply result contracts | snapshot refresh results | `lifecycle_gap` |
| SnapshotManifest | `contracts/snapshots/snapshot_manifest.v0.json` for distribution manifest | snapshot envelope/record/fixity contracts | text/html/json snapshot projections | `no_gap_use_existing_plus_profile` |

## Operational Rule

The runner task should consume this map as authority. It may implement adapters
to existing schemas, but it must not promote a projection to core truth or
modify runtime behavior based on this document alone.

Additional boundary statements:

- The public result card is not core authority for `PreviewRecord`.
- ReviewItem cannot substitute for `ReviewDecision`.
- A `Candidate` cannot become a `ReviewedRecord` without explicit review and
  materialization.

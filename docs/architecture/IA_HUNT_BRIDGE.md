# IA Hunt Bridge

`IA-HUNT-BRIDGE-00` connects the existing local Internet Archive metadata pilot to Search Hunt, IA WorkUnit packets, and Workbench result lanes.

The bridge is an orchestrator. It does not create a new source connector framework and does not replace the IA fixture replay, source-cache, evidence, candidate, review, promotion dry-run, or reviewed-index helpers. The bridge composes those pieces into a local plan:

```text
query or SearchNeed
-> Search Hunt reference
-> IA metadata WorkUnits
-> fixture-backed IA metadata pipeline
-> optional temp-instance writes
-> Workbench result lane projection
```

## Boundaries

The default mode is dry-run. It creates a Search Hunt reference, bridge WorkUnit packets, result lane packets, and boundary reports without mutating a store.

Temp-instance mode may write source-cache, evidence, candidate, review queue, and reviewed local index records only under an explicit temporary instance path. Those writes prove the existing local IA pipeline can be orchestrated, but they do not mutate the operator instance, master index, committed `data/public_index`, or hosted/public search surfaces.

The bridge keeps these actions disabled:

- live IA calls
- source probes
- downloads and uploads
- extraction
- model/provider calls
- deployment or public fanout
- master-index mutation
- production or public-launch claims

## WorkUnits

IA Hunt bridge WorkUnits are machine-readable bridge packets over the existing IA pipeline. They intentionally do not broaden the generic WorkUnit enum in this task.

Required WorkUnit types:

- `ia_metadata_search`
- `ia_item_metadata_read`
- `ia_file_manifest_metadata`
- `ia_source_cache_write`
- `ia_evidence_candidate_write`
- `ia_candidate_index_write`
- `ia_review_queue_write`
- `ia_promotion_dry_run`
- `ia_reviewed_index_rebuild`
- `ia_result_lane_project`

Each WorkUnit records its Hunt reference, source family, state, policy reference, write posture, blocked actions, and limitations.

## Result Lanes

The bridge uses the existing Workbench result lane builder for:

- reviewed local results
- IA metadata candidates
- source-cache hits
- review queue items
- known absence
- blocked actions
- running WorkUnits
- deferred deepening
- future extraction work

Projection policy remains owned by the Workbench result lane layer. Public and native read-only projections hide operator-only fields and keep mutating actions disabled.

## Non-Claim

This is not full Archive.org integration. It is a local bridge proving that IA metadata pilot outputs can be planned, queued, dry-run, temp-instance-applied, and projected into Workbench lanes without enabling live calls, downloads, extraction, models, deployment, or public launch posture.

# Hunt-to-WorkUnit Pipeline

HUNT-06 converts durable SearchNeeds into WorkUnit plans and local WorkUnit queue records.

The pipeline is deliberately bounded:

- WorkUnit records may be created.
- WorkUnit records are linked to SearchNeed, Search Hunt, and exhaustion report IDs.
- Local-safe WorkUnits are queued.
- Policy-gated WorkUnits are created blocked.
- No WorkUnit is run by this pipeline.
- No source probe, extraction, model/provider call, review mutation, index mutation, or deployment is performed.

SearchNeed kind mapping lives in `runtime/search/need/workunit_plan.py` and is summarized in `control/inventory/hunt_to_workunit_kind_matrix.json`.

HUNT-07 adds that deterministic background runner integration. It consumes linked WorkUnits from the HUNT-06 pipeline, runs only safe local worker kinds, and leaves policy-gated future work blocked.

The HUNT-06 contract remains intact: WorkUnit creation is separate from running workers, and source probe, extraction, model/provider, acquisition, deployment, and review/index mutation gates remain closed unless a later reviewed task explicitly opens them.
## Workbench Smoke Integration

HUNT-08 uses the Hunt-to-WorkUnit pipeline as part of the local workflow smoke. WorkUnit records are created and linked back to SearchNeeds, Hunts, and exhaustion reports, while execution remains limited to safe deterministic local workers through the background runner.

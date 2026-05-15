# Hunt-to-WorkUnit Pipeline

HUNT-06 converts durable SearchNeeds into WorkUnit plans and local WorkUnit queue records.

The pipeline is deliberately bounded:

- WorkUnit records may be created.
- WorkUnit records are linked to SearchNeed, Search Hunt, and exhaustion report IDs.
- Local-safe WorkUnits are queued.
- Policy-gated WorkUnits are created blocked.
- No WorkUnit is run by this pipeline.
- No source probe, extraction, model/provider call, review mutation, index mutation, or deployment is performed.

SearchNeed kind mapping lives in `runtime/search_need/workunit_plan.py` and is summarized in `control/inventory/hunt_to_workunit_kind_matrix.json`.

HUNT-07 is the next step for deterministic background runner integration.

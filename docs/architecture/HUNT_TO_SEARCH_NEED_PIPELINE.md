# Hunt To SearchNeed Pipeline

The HUNT-05 pipeline converts an unresolved local Search Hunt Session into a durable SearchNeed.

Creation requires a localhost operator token, an existing hunt, and an exhaustion report. If the hunt has no report, the pipeline may generate the deterministic local/current-index exhaustion report after the operator token has been accepted.

The pipeline links:

- `SearchNeed.hunt_id` to the source hunt.
- `SearchNeed.exhaustion_report_id` to the local exhaustion report.
- checked and deferred layers from the exhaustion report.
- future-work categories without creating WorkUnits.

The pipeline deduplicates by idempotency key when supplied, and by hunt plus normalized query otherwise.

HUNT-05 stops at demand persistence. HUNT-06 is responsible for the separate WorkUnit pipeline.
## Downstream WorkUnit Pipeline

HUNT-06 consumes SearchNeeds created by this pipeline and can persist linked local WorkUnits. The handoff remains local-only: no source probe, extraction, AI/model call, or index mutation is authorized by SearchNeed creation.

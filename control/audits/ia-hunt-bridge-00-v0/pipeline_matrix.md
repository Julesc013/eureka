# Pipeline Matrix

The IA Hunt bridge orchestrates existing fixture-backed IA metadata pieces rather than adding a new connector framework.

Pipeline:

- Query or SearchNeed to Search Hunt.
- Search Hunt to IA WorkUnits.
- Fixture metadata replay.
- Optional temp-instance source-cache write.
- Optional temp-instance evidence candidate write.
- Optional temp-instance candidate index write.
- Optional temp-instance review queue write.
- Promotion dry-run.
- Optional temp-instance reviewed-index rebuild.
- Workbench result-lane projection.

Blocked by default:

- live IA calls
- source probes
- downloads/uploads
- extraction
- model/provider calls
- deployment
- master-index mutation
- operator-instance mutation

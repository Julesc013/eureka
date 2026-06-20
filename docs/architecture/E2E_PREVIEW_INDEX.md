# E2E Preview Index

The E2E Preview Index is the Preview Plane projection for the local reference
system. It consolidates reviewed inputs, candidate deltas, source observations,
evidence summaries, and ResolutionRun lane bundles into one searchable derived
index.

It is not an authoritative store.

## Inputs

- reviewed-record JSONL fixtures or local reviewed inputs;
- IA candidate-index delta manifests;
- IA evidence-summary delta manifests;
- IA source-observation delta manifests;
- E2E ResolutionRun bundle roots.

## Outputs

Each generation writes:

- `preview_records.jsonl`
- `manifest.json`
- `source_manifest.json`
- `stats.json`
- `validation_report.json`

The current pointer is `current.json` at the preview index root. Rollback changes
only this pointer. Immutable generation content is content-addressed by the
record and source material.

## Boundaries

The index may rank, filter, and expose provisional states, but it must keep
authority visible on every record. It must not convert candidates, evidence,
source observations, or synthetic run material into reviewed truth.

Generated `.eureka/e2e-reference/preview-index/**` output remains local
rebuildable state and is ignored by git unless a future task changes the
retention convention.

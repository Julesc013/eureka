# Repair Plan

## Completed Steps

1. Identify exact `source_snapshot_baseline_drift` family from the ingest.
2. Rerun the targeted LOCAL-09 and source-observation labels.
3. Run direct validators to inspect structured payloads.
4. Remove the IA transport alternate shell fallback.
5. Add regression coverage for TLS failure degradation.
6. Rerun focused validators and tests.
7. Update queue metadata for the next repair family.
8. Write this repair package.

## Not Done

No full unittest discovery was run inside the AI session.

No generated artifacts, public snapshots, reviewed records, public indexes, or
master indexes were mutated.

No public launch or branch promotion was attempted.


# GENERATED-ARTIFACT-DRIFT-REPAIR-01

This package records the focused repair of the residual
`generated_artifact_drift` family from the external full-discovery ingest.

The repair did not regenerate `site/dist`, snapshots, checksums, or public
indexes. Current generated-artifact validators already pass. The concrete drift
was in the compact full-discovery summary parser, which misread expected
negative-path validator output as a unittest failure.

Read `REPAIR_REPORT.md` for the result and `NEXT_TASK_RECOMMENDATION.md` for
the next repair family.


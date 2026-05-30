# Legacy Software Seed Batch

`SEED-BATCH-LEGACY-SOFTWARE-00` is the second curated discovery wedge. It
exercises query planning, metadata candidate fixtures, candidate memory, SCOUT,
and batch review over legacy software and driver/support-media searches.

The batch flow is:

```text
legacy software query set
-> QueryPlan
-> SourceActionPlan
-> metadata candidate lanes
-> CandidateRecord
-> CandidateIndex
-> SCOUT relations and trails
-> ReviewBatch packet
-> PromotionPreview and handoffs
```

The batch intentionally blocks distribution behavior. It does not download,
extract, install, execute, fetch package blobs, create malware-clean claims,
support cracks/keygens/serials/warez, create reviewed truth, mutate public
indexes, deploy, or claim production/public launch readiness.

Fixture mode is the default. Future live metadata pilots must be separately
operator-approved, metadata-only, bounded, redacted, and review-only.

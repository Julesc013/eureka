# Frontier Media Seed Batch

`SEED-BATCH-FRONTIER-MEDIA-00` is the first curated discovery wedge for
frontier-resolution media. It runs the existing active discovery stack over a
small hard-query set and produces review-only outputs.

The batch flow is:

```text
frontier media query set
-> QueryPlan
-> SourceActionPlan
-> fixture Archive.org metadata candidate lane
-> CandidateRecord
-> CandidateIndex
-> SCOUT relations and trails
-> ReviewBatch packet
-> PromotionPreview and handoffs
```

The seed batch does not create reviewed truth, mutate public indexes, download
files, extract content, call model providers, deploy, or make launch readiness
claims. Review, local apply, snapshot refresh, and public alpha reassessment are
separate gates.

The default execution mode is deterministic fixture mode. A future
operator-approved live Archive.org metadata pilot may use the same query set,
but it must remain metadata-only, bounded, redacted, and review-only.

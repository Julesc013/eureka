# Driver Support Seed Batch

`SEED-BATCH-DRIVER-SUPPORT-00` adds `driver_support_media` as a curated
discovery domain. It exercises the existing query planner, candidate index,
SCOUT runtime, review batch packet, snapshot handoff, public-alpha reassess
input, and public search UX model using fixture and descriptor-only evidence.

The batch flow is:

```text
driver/support query set
-> QueryPlan
-> SourceActionPlan
-> metadata-only driver/support candidate lanes
-> CandidateRecord
-> CandidateIndex
-> SCOUT relations and trails
-> ReviewBatch packet
-> snapshot and public-alpha handoffs
```

The batch is deliberately metadata-only. It does not download driver packages,
fetch support files, extract archives, install or execute software, assert
malware-clean status, guarantee compatibility, clear rights, create accepted
truth, mutate reviewed/public/master indexes, deploy, or claim production or
public launch readiness.

Fixture mode is the default. Future live metadata pilots must be separately
operator-approved, bounded, redacted, and still metadata-only.

# Manuals and Scanned Documents Seed Batch

`SEED-BATCH-MANUALS-SCANS-00` is the third curated discovery domain. It
exercises query planning, metadata candidate fixtures, candidate memory, SCOUT,
and batch review over manuals, user guides, service manuals, deployment guides,
setup notes, and scanned-document leads.

The batch flow is:

```text
manuals/docs/scans query set
-> QueryPlan
-> SourceActionPlan
-> metadata-only document candidate lanes
-> CandidateRecord
-> CandidateIndex
-> SCOUT relations and trails
-> ReviewBatch packet
-> snapshot and public-alpha handoffs
```

The batch is deliberately metadata-only. It does not download documents, fetch
files, run OCR, extract text, assert scan completeness, assert OCR quality,
clear rights, create reviewed truth, mutate public indexes, deploy, or claim
production/public launch readiness.

Fixture mode is the default. Future live metadata pilots must be separately
operator-approved, bounded, redacted, and still metadata-only.

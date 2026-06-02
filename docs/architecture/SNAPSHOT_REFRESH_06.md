# SNAPSHOT-REFRESH-06

`SNAPSHOT-REFRESH-06` projects the temp-only `REVIEW-BATCH-APPLY-NEXT-00`
result into snapshot, relay, public-search, and public-alpha reassessment
handoffs.

The refresh packages the previous snapshot with newly applied limited reviewed
metadata records, limited reviewed source leads, reviewed known needs, reviewed
bounded absences, and non-applied candidates. It does not mutate the reviewed,
master, or public indexes.

Expected projection counts:

- previous limited reviewed projection count: 4
- new limited metadata records: 4
- new limited source leads: 4
- total limited reviewed projection count: 12
- reviewed known needs: 2
- reviewed bounded absences: 2
- remaining review-only candidates: 60

Boundaries:

- limited records are not verified artifacts
- reviewed known needs are not resolved objects
- reviewed bounded absences are bounded, not universal
- non-applied candidates remain candidates
- no downloads, file fetches, OCR, extraction, execution, install, or model calls
- no deployment, site/dist write, public mutation, or launch/readiness claim

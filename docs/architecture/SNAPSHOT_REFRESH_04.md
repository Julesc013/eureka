# Snapshot Refresh 04

`SNAPSHOT-REFRESH-04` projects the manuals/scans and driver/support seed-batch
handoffs into the snapshot layer after `SNAPSHOT-REFRESH-03`.

The refresh packages:

- existing reviewed records
- limited reviewed metadata records
- limited reviewed source leads
- frontier media candidates
- legacy software candidates
- manuals/scans candidates
- driver/support candidates
- live metadata candidates
- review queues
- known needs and bounded absences
- relay and public search view-model projections
- public alpha reassessment input

Snapshot refresh is projection only. Seed-batch candidates are not accepted
truth and are not reviewed artifacts. Manuals/scans candidates are not fetched
documents, OCR text, complete scans, or rights-cleared materials. Driver/support
candidates are not verified drivers, safe installers, compatible hardware
packages, or malware-clean files.

This refresh does not mutate reviewed, master, or public indexes; does not write
`site/dist`; does not deploy; and does not claim production or public launch
readiness.

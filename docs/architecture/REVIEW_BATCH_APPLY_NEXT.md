# REVIEW-BATCH-APPLY-NEXT-00

`REVIEW-BATCH-APPLY-NEXT-00` is the gate that applies eligible review-batch
outputs into a temporary explicit store so the limited reviewed corpus can grow.

The task uses existing deterministic review packets, candidate summaries, SCOUT
context, known needs, and bounded absences. It does not run live sources, fetch
files, mutate an operator instance, or write public/master indexes.

Allowed apply outputs are limited to:

- limited reviewed metadata records
- limited reviewed source leads
- reviewed known needs
- reviewed bounded absences

The gate does not create verified artifacts, safe installers, malware-clean
records, rights-cleared records, compatibility guarantees, OCR-quality claims,
scan-completeness claims, extracted files, or public truth.

The next projection gate is `SNAPSHOT-REFRESH-06`.

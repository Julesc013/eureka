# Candidate Snapshot Section

A candidate snapshot section is a read-only projection of seed candidates. Each
item carries its candidate id, domain, source family, title, query references,
SCOUT trail references, limitations, and action posture.

Every item must keep `accepted_truth: false` and `reviewed_record_ref: null`
unless the record was reviewed before the seed batch. Public projections may
display candidate summaries, but they cannot accept, reject, promote, download,
install, or execute them.

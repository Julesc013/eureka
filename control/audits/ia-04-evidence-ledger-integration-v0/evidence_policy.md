# Evidence Policy

IA-04 enables evidence-ledger writes only for Internet Archive metadata
source-cache records and only in temporary or explicit local instances.

The policy requires:

- dry-run by default
- explicit `--apply`
- operator token for mutation
- review-required candidates
- no accepted truth
- no candidate, reviewed, or master index mutation
- no raw live response writes
- no downloads, extraction, model/provider calls, or deployment

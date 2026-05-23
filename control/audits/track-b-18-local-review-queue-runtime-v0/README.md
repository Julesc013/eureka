# TRACK-B-18 Local Review Queue Runtime

This audit pack records the first bounded local review queue runtime for Track B.

The review queue follows the candidate store, source cache, evidence ledger, and source-cache-to-evidence bridge runtimes. It reads explicit committed review fixtures or repo-local candidate/evidence/source-cache/bridge/workunit records and records review envelopes that preserve decisions, evidence gaps, duplicate/conflict notes, blockers, and review gates.

The runtime cannot host moderation, accept evidence, accept candidates, promote records, mutate the master index, create private local state, call networks, run providers, or make rights/malware/installability claims.

## Added

- `runtime/local/foundry/review_queue.py`
- `scripts/record_review_queue.py`
- `scripts/summarize_review_queue.py`
- `scripts/validate_local_review_queue_runtime.py`
- Review runtime, status, subject, decision, output, path, and truth policies
- Review queue examples under `examples/review/queue_entries/`
- Runtime and script tests
- Reference, architecture, and operations docs
- Generated audit evidence under `generated/`

## Review Boundary

Review queue entries are governance records. They may approve a local promotion dry-run gate, request more evidence, mark duplicates, preserve conflicts, reject, defer, or block local review subjects. They do not accept evidence, accept public truth, mutate public indexes, or mutate the master index.

## Validation

See `validation.md` for command results.

## Next

TRACK-B-19 - Candidate promotion dry-run

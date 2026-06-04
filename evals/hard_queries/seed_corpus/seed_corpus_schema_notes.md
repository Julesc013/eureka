# Seed Corpus Schema Notes

Task ID: `REVIEWED-SEED-CORPUS-00`

## File Format

This package uses JSON files rather than `.yml` because the current runnable
eval lanes are stdlib-only and existing eval assets already use JSON or the
JSON subset of YAML.

## Reviewed Rule

`verified` seed items require:

```text
review_event_ref
evidence_refs
```

The current package intentionally contains no `verified` items because the hard
query seed items are not review-event-backed.

## Runtime `unavailable`

The planning status list includes `unknown`. Current runtime/surface code also
uses `unavailable` as a degraded public-safe state. This package keeps
`unavailable` for the article/scan hard query and reports it separately in
readiness counts.

## Truth Boundary

Candidate, need, near_miss, policy_blocked, unknown, and unavailable items do
not count as reviewed truth.

Backlog items are requested review work. They are not review decisions.

Each seed item must keep these flags false:

```text
reviewed_seed_material
accepted_truth
reviewed_record_created
reviewed_index_mutated
public_index_mutated
master_index_mutated
live_source_calls
```

# TRACK-B-19 Candidate Promotion Dry-Run

This audit pack records the first bounded candidate promotion dry-run for Track B.

The dry-run follows the local review queue runtime. It reads explicit local candidate, evidence, and review records and produces a readiness report. It can identify ready, missing-evidence, missing-review, conflict, duplicate, policy, rights, risk, identity, source, representation, and not-evaluable outcomes.

The dry-run cannot promote candidates, accept evidence, create public records, write public indexes, mutate the master index, host moderation, create private local state, call networks, run providers, or make rights/malware/installability claims.

## Added

- `runtime/local_foundry/candidate_promotion_dry_run.py`
- `scripts/run_candidate_promotion_dry_run.py`
- `scripts/validate_candidate_promotion_dry_run.py`
- Promotion dry-run, readiness, blocker, output, path, and truth policies
- Promotion dry-run examples under `examples/candidate_promotion_dry_runs/`
- Runtime and script tests
- Reference, architecture, and operations docs
- Generated audit evidence under `generated/`

## Review Boundary

Ready means ready to seed a future reviewed-record proposal. It does not accept a candidate, accept evidence, mutate the public index, mutate the master index, or create public truth.

## Validation

See `validation.md` for command results.

## Next

TRACK-B-20 - Reviewed public-index rebuild contract

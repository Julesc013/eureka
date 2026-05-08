# Candidate Store Runtime

The Candidate Store runtime is a local, explicit-input helper for provisional
candidate records. It can normalize candidate records from SearchNeeds, search
misses, query observations, WorkUnit results, node policy evaluations,
observation candidates, source leads, and future reviewed draft sources.

The runtime is not a public candidate index, not the master index, and not an
evidence ledger. A candidate remains a review item until a future governed
workflow accepts, rejects, defers, deduplicates, or requests more evidence.

## Current Scope

- Standard-library only.
- Explicit input only.
- Local-only for this milestone.
- Writes no files by default.
- Writes only to explicit audit/generated or temp-test paths.
- Performs exact-key duplicate reporting without merge or deletion.

## Candidate Status

Current examples may use `example_only`, `proposed`, `recorded_local`,
`candidate`, `needs_review`, `evidence_needed`, `duplicate_possible`,
`conflict_detected`, `policy_blocked`, `rejected`, or `deferred`.

`accepted_public_future` is vocabulary only for future reviewed planning and is
forbidden for current records.

## Candidate Types And Origins

Candidate types include object, source, evidence, compatibility, identity,
representation, member, version/state, source lead, SearchNeed, WorkUnit seed,
future pack/extraction/review item, policy-blocked, and not-evaluable
candidates.

Origins include SearchNeeds, search misses, query observations, observation
candidates, local evals, source leads, WorkUnit results, node policy
evaluations, and future reviewed source/evidence/pack drafts.

## Truth Boundary

Every candidate record preserves false values for:

- candidate store is master index
- candidate is public truth
- candidate is accepted evidence
- candidate can mutate the master index
- candidate can claim rights clearance
- candidate can claim malware safety
- candidate can claim verified installability
- candidate can claim exhaustive global search
- candidate can claim production readiness

Human review is required before downstream use.

## Validation

```bash
python scripts/record_candidate.py --input examples/search_needs/software_version_search_need_v0.json --check
python scripts/summarize_candidate_store.py --input examples/candidates --check
python scripts/validate_candidate_store_runtime.py
```


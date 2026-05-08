# SearchNeed Seed Review Guide

## What A Seed Is

A SearchNeed seed is a review-gated draft that describes a possible future user
search need. It can be derived from a local ObservationCandidate or review queue
entry when the local material is specific enough to name a topic, object family,
desired user action, limitations, and downstream dependency.

A seed is not a runtime SearchNeed. It is not evidence, not an observation, and
not source access permission.

## Review Questions

Reviewers should check:

- Does the seed describe a clear user action?
- Is the object family or topic specific enough?
- Does the seed preserve local evidence limitations?
- Does the seed avoid turning source leads into truth?
- Does the priority score reflect review order only?
- Is a source policy decision needed before any future source interaction?
- Is the seed blocked by missing Track B runtime contracts?
- Is it a duplicate of another seed or review item?

## Review Actions

Current OBS-AGENT-04 artifacts do not record decisions. Future reviewed actions
may include:

- Tune the seed label, aliases, or desired user action.
- Mark the seed as needing more evidence.
- Mark the seed as duplicate or policy-blocked.
- Defer the seed until Track B SearchNeed runtime exists.
- Approve the seed for a future Track B conversion packet.

Every current action remains human review work. No seed is accepted
automatically.

## Boundary Rules

Approving a seed later does not make it an observed baseline.

Approving a seed later does not make it accepted evidence.

Approving a seed later does not create a runtime SearchNeed until Track B
runtime accepts it.

Approving a seed later does not mutate the master index.

Approving a seed later does not approve live source access.

## Duplicate And Ambiguity Handling

Prefer one canonical need when multiple candidates describe the same user
action. Use aliases for wording variants. Keep separate seeds only when the
object family, source family, platform, artifact type, or desired action would
lead to distinct Track B planning.

If a seed is ambiguous, keep it in `needs_more_evidence` or `deferred` status.
Do not invent missing product names, versions, compatibility answers, or source
results.

## Track B Handoff

Track B can consume reviewed seeds only after matching contracts and runtime
semantics exist. Until then, these seeds are repo-local governance records and
should be treated as planning inputs, not runtime data.

## Validation

Run:

```powershell
python scripts/validate_search_need_seed_candidates.py
python scripts/summarize_search_need_seed_candidates.py
python -m unittest tests.contracts.test_search_need_seed_contracts tests.operations.test_search_need_seed_conversion
```

## No Goals

- No live external searches.
- No source approval.
- No SearchNeed runtime activation.
- No observed baseline or evidence truth.
- No master-index mutation.
- No product runtime changes.

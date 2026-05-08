# WorkUnit Seed Review Guide

## What A Seed Is

A WorkUnit seed is a review-gated draft that describes possible bounded future
work. It can be derived from a local ObservationCandidate, review queue entry,
or SearchNeed seed when the local material is specific enough to name inputs,
allowed actions, forbidden actions, output shape, source policy needs, and Track
B dependencies.

A WorkUnit seed is not an executable WorkUnit. It is not a runtime WorkUnit,
not evidence, not an observation, and not source access permission.

## Review Questions

Reviewers should check:

- Does the seed describe bounded work?
- Are allowed actions and forbidden actions clear?
- Does the seed avoid execution, probing, downloading, scraping, and API calls?
- Does the seed preserve local evidence limitations?
- Does the seed avoid turning source leads into approval?
- Does the priority score reflect review order only?
- Is a source policy decision needed before future work?
- Is the seed blocked by missing Track B runtime contracts?
- Is it a duplicate of another seed or review item?

## Review Actions

Current OBS-AGENT-05 artifacts do not record decisions. Future reviewed actions
may include:

- Tune the work label, scope, allowed actions, or forbidden actions.
- Mark the seed as needing more evidence.
- Mark the seed as duplicate or policy-blocked.
- Defer the seed until Track B WorkUnit runtime exists.
- Approve the seed for a future Track B conversion packet.

Every current action remains human review work. No seed is accepted
automatically.

## Boundary Rules

Approving a WorkUnit seed later does not execute it.

Approving a WorkUnit seed later does not make it an observed baseline.

Approving a WorkUnit seed later does not make it accepted evidence.

Approving a WorkUnit seed later does not create a runtime WorkUnit until Track B
accepts it.

Approving a WorkUnit seed later does not mutate the master index.

Approving a WorkUnit seed later does not approve live source access.

## Duplicate And Ambiguity Handling

Prefer one canonical WorkUnit seed when multiple candidates describe the same
future work. Keep separate seeds only when the proposed work type, input set,
source policy requirement, or output contract would lead to distinct Track B
planning.

If a seed is ambiguous, keep it in `needs_more_evidence` or `deferred` status.
Do not invent missing source results, compatibility answers, executable
behavior, or node capabilities.

## Source Policy Gates

Source leads can suggest work but cannot grant access. Metadata probe planning,
manual-only sources, forum/community leads, and broad web source gaps remain
blocked or future/deferred until source policy review explicitly changes the
posture in a later task.

## Track B Handoff

Track B can consume reviewed seeds only after matching WorkUnit contracts,
runtime semantics, node capability rules, and local state requirements exist.
Until then, these seeds are repo-local governance records and should be treated
as planning inputs, not runtime work.

## Validation

Run:

```powershell
python scripts/validate_workunit_seed_candidates.py
python scripts/summarize_workunit_seed_candidates.py
python -m unittest tests.contracts.test_workunit_seed_contracts tests.operations.test_workunit_seed_conversion
```

## No Goals

- No live external searches.
- No source approval.
- No WorkUnit runtime activation.
- No WorkUnit execution.
- No observed baseline or evidence truth.
- No master-index mutation.
- No product runtime changes.

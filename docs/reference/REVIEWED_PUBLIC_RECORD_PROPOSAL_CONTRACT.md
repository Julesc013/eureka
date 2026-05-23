# Reviewed Public Record Proposal Contract

`contracts/index/master/reviewed_public_record_proposal.v0.json` defines the shape of a future reviewed public record proposal.

A proposal is review material. It is not a public record, accepted evidence, accepted candidate truth, rights clearance, malware safety, verified installability, or permission to mutate a public or master index.

## Required Posture

Each proposal must include:

- source candidate, review, evidence, source cache, and future pack refs
- proposed public record summary
- public search card summary
- object, source, evidence, compatibility, rights, risk, limitation, review, conflict, and duplicate summaries
- publication constraints
- truth and product boundaries

## Statuses And Types

Proposal statuses include `example_only`, `proposed`, `ready_for_review`, `ready_for_future_rebuild_dry_run`, blocked statuses, `rejected`, `deferred`, and `accepted_public_future`.

Current examples must not use `accepted_public_future` as current behavior.

Proposal types include object, source, need, compatibility, representation, absence, evidence summary, future candidate/pack records, policy-blocked records, and not-evaluable records.

## No-Claim Rule

Public record proposals must expose limitations and no-claim summaries. They must not claim rights clearance, malware safety, verified installability, exhaustive search, or production readiness unless a future reviewed process explicitly permits and proves those claims.

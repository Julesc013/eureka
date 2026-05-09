# Candidate Promotion Dry-Run Model

The dry-run model sits after the local review queue and before any future reviewed public-index rebuild contract. It composes candidate records, evidence candidate records, and review queue entries into one local readiness report.

## Record Shape

A dry-run record includes:

- `promotion_dry_run_id`, status, and readiness
- candidate, evidence, review, source-cache, bridge, search-need, WorkUnit, and future pack refs
- requirement result groups for evidence, review, identity, conflict, duplicate, rights/risk, and policy checks
- blockers and warnings
- future proposal summary text
- allowed and forbidden next actions
- truth and product boundaries

Requirement result status values include `satisfied_for_dry_run`, `missing`, `partial`, `conflict_detected`, `duplicate_uncertain`, `blocked`, `deferred`, `not_applicable`, and `not_evaluable`.

## Dry-Run Evaluation

The runtime treats evidence records as candidates and review entries as governance records. A ready result requires fixture evidence and a local review decision that approves only a promotion dry-run. Conflict, duplicate, policy, rights, risk, and identity blockers prevent readiness.

## Boundaries

The model does not implement actual promotion, hosted moderation, public-index writes, master-index mutation, evidence acceptance, candidate acceptance, source access, telemetry, downloads, uploads, accounts, or provider calls.

This prepares a future reviewed public-index rebuild contract by defining what a proposal readiness report can contain without creating public truth.

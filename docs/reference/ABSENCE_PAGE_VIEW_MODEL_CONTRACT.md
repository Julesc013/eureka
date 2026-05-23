# AbsencePage View Model Contract

AbsencePageView v0 defines the public meaning layer for known absence,
unresolved needs, weak-result cases, source gaps, capability gaps, near matches,
policy blocks, and safe next work. It is contract and governance work only.

## Purpose

Absence is scoped, not omniscient. AbsencePageView makes absence identity,
related query and need refs, searched scope, sources checked, sources not
checked, source gaps, capability gaps, near matches, rejected matches,
candidates, policy blocks, evidence posture, next safe actions, rights/risk/
privacy posture, allowed actions, blocked actions, limitations, and warnings
visible to every renderer.

## Required Meaning

AbsencePageView preserves:

- canonical absence identity and route
- absence status and scope
- query and interpreted intent posture
- searched scope, sources checked, and sources not checked
- source gaps, capability gaps, near matches, rejected matches, and candidates
- policy blocked state and manual observation pending state
- next safe actions and unavailable runtime actions
- rights, risk, and privacy posture
- limitations, warnings, and unresolved gaps

## Scope Boundary

AbsencePageView must distinguish:

- no verified result
- candidate exists
- near match exists
- source gap exists
- capability gap exists
- policy blocked
- manual observation pending
- not searched yet

It must not claim exhaustive global search or global proof of absence.

## Current Boundary

Current examples must not claim hosted backend, live probes, source sync,
node-task runtime, public submissions, downloads, uploads, accounts, telemetry,
master-index mutation, or exhaustive global search.

## Related Contracts

- `contracts/view/pages/absence_page.v0.json`
- `control/inventory/publication/absence_page_view_model_policy.json`
- `docs/reference/NEED_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/CANDIDATE_PAGE_VIEW_MODEL_CONTRACT.md`
- `docs/reference/ROUTE_VIEW_REPRESENTATION_MATRIX.md`
- `docs/reference/SEMANTIC_RENDERER_PARITY_CONTRACT.md`

## No-Goals

- No runtime behavior changes.
- No public route activation.
- No live probes, source sync, node runtime, public submission runtime, or
  master-index mutation.
- No exhaustive global search claim.

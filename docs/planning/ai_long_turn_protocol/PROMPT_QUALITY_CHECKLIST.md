# Prompt Quality Checklist

Use this checklist before starting a long or connected turn.

## Identity

- Task id is explicit.
- Repository root is explicit.
- Mode is explicit: single task, connected queue turn, or long-turn controller.
- Turn budget is explicit.

## Authority And Context

- Required reading names current repo files, not chat history.
- Authority order is stated.
- Current known state is marked as refresh-required.
- Queue and gate files are included.

## Boundaries

- Allowed paths are named.
- Forbidden paths are named.
- Component boundary crossings are named.
- Product behavior changes are either explicitly allowed or forbidden.
- Public launch, deployment, and `dev -> main` promotion are explicitly gated.

## Evidence Honesty

- External artifact evidence cannot be fabricated.
- Manual observations cannot self-promote.
- Reviewed artifact records are distinct from verified artifacts.
- AI/model output is not truth.
- Synthetic fixtures are not external evidence.
- Rights, safety, download, install, and compatibility claims require evidence.

## Validation

- Validation ladder is named.
- Full unittest discovery is externalized.
- Focused test selection is required after changes.
- Actual tests, expected tests, and skipped tests must be separated.
- Commit check is required after commits when practical.

## Stop Conditions

- External full discovery stop is named.
- External artifact evidence stop is named.
- User-details stop is named.
- Public-alpha readiness and launch stops are named.
- Promotion stop is named.
- Broad failure-family stop is named.

## Reporting

- Final report format is specified.
- Gate table is required at start and end.
- Changed files and commits are required.
- Blocked/deferred items are required.
- Push/sync recommendation is required but does not authorize a push.

# AIDE-MERGE-01 - Merge Named Task Branch Into Main

Use this prompt only on the integration machine.

## Goal

Merge one reviewed task branch into `main`, validate, and push `main` normally.

## Required Steps

1. Start with a clean tree.
2. Fetch origin.
3. Switch to `main`.
4. Fast-forward local `main` from `origin/main`.
5. Merge the named task branch.
6. Resolve conflicts immediately if any appear.
7. Run validation.
8. Push `main` normally.

## Stop Conditions

- Local `main` cannot fast-forward from origin.
- Conflict cannot be resolved intentionally.
- Validation fails.
- Secret-like or private local paths appear.

## Forbidden

- No force push.
- No broad one-side conflict deletion.
- No branch deletion.
- No history rewrite.
- No product boundary changes unless the task explicitly allows them.

# DEV-TO-MAIN-PROMOTION-REVIEW-02

This promotion review verifies the completed local product-loop baseline on
`dev` before fast-forwarding `main`.

## Scope

The promotion scope is evidence-only. It includes the repository layout and
taxonomy cleanup, the test lane router, IA metadata pilot, IA-HUNT bridge,
Workbench foundation, search interaction contracts, Workbench result lanes, the
SYN/DOMAIN/SCOUT/F0/G0 foundations, the Resolution Run Kernel, Workbench Live
Run, IA Live Metadata Lane, Workbench Review/Promote, Local Apply Gate, and the
Workbench Local Loop Closeout.

## Gates

- `origin/main` must be an ancestor of `origin/dev`.
- Local `dev` must match `origin/dev` before promotion evidence is committed.
- Local Apply Gate and Workbench Local Loop must be `pass` or
  `pass_with_warnings`.
- Full unittest discovery must pass before main is promoted.
- No force push, rebase, history rewrite, branch deletion, deployment, source
  probe, download, extraction, model call, production readiness claim, or public
  launch claim is part of this task.

## Promotion Method

Promotion is fast-forward only:

1. Commit promotion evidence on `dev`.
2. Push `dev`.
3. Fast-forward local `main` to `origin/dev`.
4. Push `main`.
5. Return to `dev` and verify `origin/main == origin/dev`.

## Non-Claims

This is not production readiness, public hosted launch readiness, full
Archive.org integration, source expansion, marketplace readiness, or app-store
readiness.

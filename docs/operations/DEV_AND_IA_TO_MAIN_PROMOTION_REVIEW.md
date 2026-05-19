# Dev And IA To Main Promotion Review

This review evaluates the current `dev` baseline for promotion to `main`. The
promotion is blocked unless the full gate set passes.

The promotion scope is deliberately narrow:

- IA metadata-only local vertical slice through `IA-PILOT-CLOSEOUT-01`.
- Repo layout canon from `REPO-LAYOUT-CANON-01`.

The IA baseline is not production readiness, not public launch readiness, and
not full Archive.org integration. It is a reviewed metadata-only local vertical
slice with a bounded live metadata probe already committed as evidence.

The repo layout canon is policy and validation only. It is the repo layout canon
for root ownership, naming, generated artifact exceptions, and validator gates.
It is not a file-move task and does not perform repo layout moves.

## Boundaries

The promotion does not enable public source fanout, downloads, uploads,
extraction, AI/model-provider use, deployment, marketplace/app-store readiness,
or broad Archive.org crawling. It is explicitly not marketplace readiness and
not app-store readiness.

All write-capable IA stages remain scoped to temp explicit instance proof:

- source-cache write proof
- evidence-ledger write proof
- candidate-index write proof
- review queue write proof
- reviewed-index rebuild proof

No operator instance state, committed `data/public_index`, master index, or
hosted public state is mutated by this promotion review.

## Decision

The current decision is blocked. `origin/main` can fast-forward to `origin/dev`,
and the IA/layout focused gates pass, but full unittest discovery is red in
blocking lanes.

Promote by fast-forward only when:

- local `dev` equals `origin/dev`
- `origin/main` is an ancestor of `origin/dev`
- IA validators pass
- repo layout canon validator and focused tests pass
- architecture boundaries pass
- generated artifact cleanliness passes
- AIDE checks pass
- full discovery passes or has exact accepted non-blocking failures

Blocking full-discovery groups found in this review:

- candidate-index contract and record validators.
- contract taxonomy inventory for the new repo layout canon contracts.
- runtime/source-observation leakage gates.
- HUNT/LOCAL promotion-state expectations.

## Next

Before Workbench work, run `DEV-AND-IA-PROMOTION-BLOCKER-01`: resolve or
explicitly reclassify the blocking full-discovery failures, then rerun this
promotion review. After promotion, the next product-shaping task remains
`WORKBENCH-FOUNDATION-00`.

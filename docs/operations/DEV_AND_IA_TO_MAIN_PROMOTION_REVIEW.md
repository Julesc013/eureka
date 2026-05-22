# Dev And IA To Main Promotion Review

This review evaluates the repaired `dev` baseline for fast-forward promotion to
`main`. The promotion scope now includes three completed baselines:

- IA metadata-only local vertical slice through `IA-PILOT-CLOSEOUT-01`.
- Repo layout canon from `REPO-LAYOUT-CANON-01`.
- `DEV-AND-IA-PROMOTION-BLOCKER-01` full-discovery blocker repair.

This is a stable main-baseline promotion review. It is not production readiness,
not public launch readiness, not full Archive.org integration, and not
marketplace or app-store readiness. It is also not marketplace launch posture.

## Repaired Gate

The previous review was blocked by full unittest discovery failures in
candidate-index records, contract taxonomy inventory, runtime/source-observation
leakage, and HUNT/LOCAL promotion-state tests.

`DEV-AND-IA-PROMOTION-BLOCKER-01` repaired those lanes and recorded:

- full unittest discovery: pass
- current full-discovery failures: 0
- current full-discovery errors: 0
- candidate-index failures resolved
- contract taxonomy failures resolved
- runtime/source-observation leakage resolved
- HUNT/LOCAL promotion-state failures resolved

## Boundaries

The promotion does not enable public source fanout, downloads, uploads,
extraction, AI/model-provider use, deployment, marketplace/app-store readiness,
or broad Archive.org crawling.

All write-capable IA stages remain scoped to temp explicit instance proof:

- source-cache write proof
- evidence-ledger write proof
- candidate-index write proof
- review queue write proof
- reviewed-index rebuild proof

No operator instance state, committed `site/dist/data/public_index`, master index, hosted
public state, repo layout move, or `site/dist` regeneration is performed by this
promotion review.

## Decision

The current decision is to promote `dev` to `main` by fast-forward only if the
fresh gate run remains green:

- local `dev` equals `origin/dev`
- `origin/main` is an ancestor of `origin/dev`
- IA validators pass
- repo layout canon validator and focused tests pass
- blocker repair result confirms full discovery pass
- runtime leakage validators pass
- architecture boundaries pass
- generated artifact cleanliness passes
- AIDE checks pass
- full unittest discovery passes

## Next

After successful promotion, run `REPO-LAYOUT-CANON-01` as a verification pass
before Workbench Foundation. Workbench Foundation, Search Interaction, Workbench
Result Lanes, and IA-HUNT bridge remain after that verification step.

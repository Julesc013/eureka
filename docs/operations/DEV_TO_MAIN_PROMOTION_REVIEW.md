# Dev To Main Promotion Review

R0-10 creates a promotion plan only. It does not merge `dev` to `main` and does not mutate branches.

Promotion requires:

- all R0 review checks have no blockers
- full unit discovery passes
- architecture boundary checks pass
- repo state is clean
- `dev` contains current `main`
- remaining warnings are classified
- no production-readiness or public-launch claim is made
- an operator explicitly approves the branch promotion

Current R0-10 decision: `dev` remains blocked from promotion because the contract taxonomy is not clean enough for promotion.

## Rollback Plan

If a future promotion is approved and later must be reversed, use a normal revert commit on `main`. Do not rewrite `main` history. Keep the R0 audit evidence attached to the revert decision.

## Operator Action

After remediation passes, the operator should rerun the promotion review, push `dev`, open the dev-to-main review, and merge only after explicit approval.

# DEV-TO-MAIN-R0 Merge Evidence

The recovered R0 baseline was promoted from `dev` to `main` with a fast-forward merge.

## Branch State Before

- current branch: `dev`
- `HEAD`: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- `origin/dev`: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- `origin/main`: `c5e131da12a67b86259874f6ac7145de4d2d3661`
- `origin/main...origin/dev`: `0 89`
- `dev` contained `origin/main`: true

## Validation Gates

All required pre-merge validation gates passed. Full unittest discovery passed with 4044 tests. Generated artifact cleanliness and architecture boundaries passed. R0 validators passed with warning-only dispositions.

## Merge Method

The promotion used `git merge --ff-only origin/dev` on `main`. The merge was a fast-forward from `c5e131da12a67b86259874f6ac7145de4d2d3661` to `4cde57bd1004a384d7b0c9f83f73ced209bdc742`.

`main` was pushed to origin after the fast-forward.

## Branch State After

- `origin/dev`: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- `origin/main`: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- remote branches equal: true
- working tree clean: true

## Rollback Plan

Do not rewrite history and do not force-push. If the promotion must be backed out, use a normal revert commit on `main`, then fast-forward `dev` to the same revert commit and record the rollback decision.

## Claims

This branch promotion is not deployment, public launch, legal approval, rights clearance, exhaustive source coverage, malware-safety approval, installability certification, or production readiness.

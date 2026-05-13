# Dev-To-Main R0 Promotion Plan

This plan promotes the recovered R0 baseline from `dev` to `main` only after an explicit operator apply action. It is a git baseline update, not deployment, public launch, release tagging, source sync, package installation, or site generation.

## Preconditions

- Current branch is `dev`.
- Working tree has no non-review changes.
- `dev` is synced to `origin/dev`.
- `origin/main` is an ancestor of `origin/dev`.
- R0 final promotion review has `hard_blockers_remaining: 0`.
- Full unittest discovery, generated artifact cleanliness, architecture boundaries, and R0 validators pass.
- Warning disposition is complete.
- Final evidence makes no deployment, launch, legal, rights, malware-safety, or exhaustive-coverage claim.

## Plan-Only Command

```bash
python scripts/prepare_r0_dev_to_main_merge.py --output control/audits/r0-final-promotion-review-v0/generated/sample_merge_plan.json --json
```

## Apply Sequence

Run only when the operator explicitly requests branch mutation:

```bash
python scripts/prepare_r0_dev_to_main_merge.py --apply --json
```

The script checks gates, fetches origin, checks out `main`, fast-forwards local `main` to `origin/main`, fast-forwards local `main` to `origin/dev`, and returns to `dev`.

Pushing `main` is separate and must be explicit:

```bash
python scripts/prepare_r0_dev_to_main_merge.py --apply --push-main --json
```

## Rollback

- Never rewrite `main` history.
- Never force-push.
- If an applied promotion must be backed out after push, use a normal revert commit on `main`.
- Record rollback evidence in the promotion audit inventories.
- Do not tag or deploy as part of rollback.

## Non-Deployment

The plan does not run any deployment command, regenerate `site/dist`, make live source calls, install packages, publish packs, or claim public launch readiness.

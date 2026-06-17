# Dev To Main Promotion Decision

Task: `DEV-TO-MAIN-PROMOTION-READINESS-AND-SYNC-00`

## Selected Decision

```text
PROMOTE_DEV_TO_MAIN
```

## Rationale

`origin/main` has no commits that are absent from `origin/dev`, while
`origin/dev` is ahead by 131 commits. The branch comparison is therefore not an
unsafe divergence; it is a fast-forward promotion candidate.

Focused validators passed, public docs preserve non-claims, generated artifact
cleanliness passed before promotion reports were added, and the current
public-alpha posture remains read-only and not launched.

## Promotion Method

Use direct fast-forward branch sync from `dev` to `main` after the tracked
promotion reports are committed to `dev`:

```powershell
git push origin dev
git push origin dev:main
```

This does not force-push, delete branches, rewrite history, start exposure, or
create launch approval.

## Promotion Status

- Promotion performed: yes
- Promotion may proceed: yes
- Method: direct fast-forward branch sync
- Promoted commit:
  `a9f2a8c760a4603702d4d82ef77c9cd0cdb9c7dd`
- Post-promotion `origin/main...origin/dev`: `0 0`

The final build report records the post-promotion verification.

## Remaining Blockers After Promotion

- Provider/public URL decision is missing.
- Provider HTTPS/TLS posture is unvalidated.
- Actual tunnel/proxy rehearsal has not run.
- Full discovery is not claimed in this task.
- Release promotion report remains a separate launch-track blocker.
- Manual public launch approval is absent.
- Final public launch is not approved or performed.
- License remains unresolved.

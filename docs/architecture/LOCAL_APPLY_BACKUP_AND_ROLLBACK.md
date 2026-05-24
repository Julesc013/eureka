# Local Apply Backup And Rollback

LOCAL-APPLY-GATE-01 is a local-only controlled mutation boundary. The default is
dry-run preview. Mutation requires an explicit instance path outside the repo, an
operator token, the `--apply` flag, the exact confirmation string, a pre-apply
backup, a mutation manifest, an audit log, post-apply validation, and a rollback
plan.

Public and native read-only projections cannot apply. The gate does not mutate a
master index, committed public index, `site/dist`, or committed instance state. It
does not download, upload, extract, execute, call model providers, deploy, or claim
production/public launch readiness.

Primary commands:

```text
python scripts/eureka_local_apply.py --instance <path> --from-review-promote-fixture --dry-run --json
python scripts/eureka_local_apply.py --instance <path> --from-review-promote-fixture --apply --operator-token <token> --confirm APPLY_TO_LOCAL_INSTANCE --json
python scripts/eureka_local_apply_rollback.py --instance <path> --rollback-plan <path> --apply --operator-token <token> --confirm ROLLBACK_LOCAL_INSTANCE --json
```

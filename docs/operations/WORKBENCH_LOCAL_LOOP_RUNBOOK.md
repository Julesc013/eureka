# Workbench Local Loop Runbook

Run dry-run proof:

```text
python scripts/eureka_local_loop_closeout.py --query sampleproject --projection operator_workbench --dry-run --json
```

Run temp-instance apply proof:

```text
python scripts/eureka_local_loop_closeout.py --query sampleproject --projection operator_workbench --use-temp-instance --apply-to-temp --operator-token local-dev-token --confirm APPLY_TO_LOCAL_INSTANCE --json
```

This document describes the governed Workbench local product loop. The loop is local-only, uses a temp explicit instance for automated proof, and depends on the Local Apply Gate for any mutation.

Required safety posture:
- dry-run is the default
- review happens before apply
- apply requires operator token and confirmation
- automated validation uses temp instances only
- public and native projections are read-only
- backup, mutation manifest, audit log, rollback plan, post-apply validation, and rollback proof are required
- no master index or committed public index mutation occurs
- no downloads, uploads, extraction, model calls, deployment, production readiness, or public launch readiness are claimed

# Post Workbench Local Loop Plan

Next recommended task: DEV-TO-MAIN-PROMOTION-REVIEW-02. After that, continue with SOURCE-ACTION-KERNEL-00, SOURCE-WAVE-00, SNAPSHOT-RELAY-00, and PUBLIC-ALPHA-READONLY-00.

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

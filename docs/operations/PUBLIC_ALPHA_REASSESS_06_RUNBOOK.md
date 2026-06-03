# PUBLIC-ALPHA-REASSESS-06 Runbook

1. Confirm `dev` is clean and current with `origin/dev`.
2. Run `python scripts/check_git_task_state.py --mode start-task --task-id PUBLIC-ALPHA-REASSESS-06`.
3. Build the reassessment from committed examples:
   `python scripts/eureka_public_alpha_reassess.py --from-review-batch-apply-refresh-examples --json`.
4. Write examples and inventory only when intentionally refreshing evidence:
   `python scripts/eureka_public_alpha_reassess.py --from-review-batch-apply-refresh-examples --write-examples --json`.
5. Validate with `python scripts/validate_public_alpha_reassess.py` plus the focused snapshot, review-batch apply, UX, readonly, relay, architecture, generated-artifact, and unittest lanes.

Do not run full unittest discovery inside the AI session. Do not deploy, publish,
write public indexes, call live sources, fetch files, OCR, extract, or claim
public launch readiness.

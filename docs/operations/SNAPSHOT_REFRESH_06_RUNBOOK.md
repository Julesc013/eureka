# SNAPSHOT-REFRESH-06 Runbook

1. Confirm `dev` is clean and current with `origin/dev`.
2. Verify `review_batch_apply_next_result.json` and `snapshot_refresh_05_result.json`.
3. Run `python scripts/eureka_snapshot_refresh.py --from-review-batch-apply-examples --json`.
4. Run `python scripts/eureka_snapshot_refresh.py --from-review-batch-apply-examples --write-examples --json`.
5. Run `python scripts/eureka_snapshot_refresh_report.py --from-review-batch-apply-examples --json`.
6. Run focused validators and tests only.

Do not run full unittest discovery inside an AI session. Do not write
`site/dist`, mutate public/master/reviewed indexes, download, fetch files, OCR,
extract, install, execute, call model providers, deploy, publish, or claim public
launch readiness.

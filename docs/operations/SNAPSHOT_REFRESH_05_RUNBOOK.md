# SNAPSHOT-REFRESH-05 Runbook

Use this lane to refresh public UX projection examples after the public search UX MVP.

1. Verify the repo starts on clean `dev`.
2. Run `python scripts/eureka_snapshot_refresh.py --from-public-search-ux-examples --write-examples --json`.
3. Run `python scripts/eureka_snapshot_refresh_report.py --from-public-search-ux-examples --json`.
4. Run `python scripts/validate_snapshot_refresh.py`.
5. Run the focused snapshot refresh 05 unit tests.

Do not run deployment, public launch, full discovery, live source calls, downloads, file fetches, OCR, extraction, model calls, or site/dist writes in this lane.

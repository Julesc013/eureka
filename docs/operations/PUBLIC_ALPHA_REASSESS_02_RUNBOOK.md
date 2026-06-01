# Public Alpha Reassess 02 Runbook

Run the deterministic reassessment from committed examples:

```text
python scripts/eureka_public_alpha_reassess.py --from-live-metadata-review-refresh-examples --json
python scripts/eureka_public_alpha_reassess_report.py --from-live-metadata-review-examples --json
python scripts/eureka_public_alpha_route_smoke.py --from-examples --json
python scripts/validate_public_alpha_reassess.py
```

Use `--write-examples` only when intentionally refreshing public-safe example,
inventory, and audit evidence.

The reassessment is examples-only. It starts no server, performs no live source
calls, writes no public index, writes no `site/dist`, and does not execute
local apply.

Passing output should leave launch deferred and recommend
`LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00`.

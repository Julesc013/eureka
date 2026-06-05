# Next Task Recommendation

## Recommended Next Task

`EXTERNAL-FULL-DISCOVERY-RUN-01`

## Why

No full-discovery summary matching current `HEAD` exists. Older summaries are
stale and cannot support public-alpha readiness or `dev -> main` promotion.

## Do Not Run Yet

- `PUBLIC-ALPHA-READINESS-00`
- `PUBLIC-ALPHA-LAUNCH-00`
- `DEV-TO-MAIN-PROMOTION-REVIEW-*`
- Broad directory/refactor tasks

## Branch After External Summary

If external full discovery is green and current, reassess release gates.

If external full discovery is red, run the targeted repair task for the current
failure family reported by that summary.

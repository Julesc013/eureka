# Branch Inventory

Current branch: `sync/preserve-dirty-work-20260509`

Local head: `8a091f64eb1a1a61d808e6be557d291a015e7a4d` (`audit(sync): record active merge rescue`)

Origin main: `f83b005dcd68bc9710bccefe8d788b64c5fce461` (`ops(observation): prepare human candidate review packet`)

Merge base: `103012082a0d6df98dd9dfc227c61b34218afa22`

## Local Branches

- `main`: `2f63e190964d19bd7f7d6c9130e716ecbd61b6ac`, tracking `origin/main`, ahead 8 and behind 7.
- `sync/preserve-dirty-work-20260509`: `8a091f64eb1a1a61d808e6be557d291a015e7a4d`, current safety branch, ahead 10 and behind 7 relative to `origin/main`.

## Remote Branches

- `origin/HEAD`: points to `origin/main`.
- `origin/main`: `f83b005dcd68bc9710bccefe8d788b64c5fce461`.

No remote `sync/*` branch was observed after fetch.

## Merge State

- Working tree was clean before fetch.
- `MERGE_HEAD` was absent before fetch and remained absent during validation.

## Stale AIDE State

The safety branch `.aide/context/latest-task-packet.md` still points at TRACK-B-23. That is stale relative to the active repo sync task and should be handled after convergence planning, not silently rewritten during this audit.

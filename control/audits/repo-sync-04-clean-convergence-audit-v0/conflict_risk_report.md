# Conflict Risk Report

Risk: HIGH

## Evidence

- `git merge-tree <base> HEAD origin/main` reported zero mechanical conflict markers.
- Path comparison still found `68` overlapping paths changed on both sides since the merge base.
- The overlapping paths include contracts, control inventories, OBS audit files, scripts, examples, and tests.
- The branch tips represent different lanes: local Track B spine preservation versus remote OBS human review/seed work.

## Why No Merge Was Attempted

The task policy treats overlapping contracts, validators, tests, inventories, and AIDE state as high risk even when Git can produce an automatic textual merge. A clean textual merge could still silently replace or mix task semantics.

## Recommended Handling

- Do not merge into `main`.
- Do not create a convergence merge until OBS seed/review artifacts and Track B runtime artifacts are reviewed together.
- Prefer a dedicated convergence branch after manual file-level review.
- Preserve both lanes unless a reviewer explicitly marks an artifact superseded.

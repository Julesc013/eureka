# AIDE-RESCUE-01 - Preserve Dirty Tree And Stop

Use this prompt when the repo is dirty or interrupted before normal work can continue.

## Goal

Preserve current local work safely, avoid destructive operations, and stop before merge or review decisions.

## Required Steps

1. Inspect `git status --short`.
2. Inspect active merge/rebase/cherry-pick/revert state.
3. Inspect unmerged entries.
4. Screen path names for secrets, credentials, private local roots, and caches.
5. Create a rescue branch if safe.
6. Commit preservation evidence only if safe.

## Stop Conditions

- Unmerged conflict entries remain.
- Secret-like or private local paths are present.
- The requested operation would discard work.

## Forbidden

- No pull, merge, or rebase.
- No force push.
- No hard reset.
- No destructive clean.
- No stash-pop.
- No branch deletion.
- No semantic approval of preserved work.

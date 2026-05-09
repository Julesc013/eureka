# Preservation Plan

## Decision

Use one preservation commit for the pre-existing dirty work because the tree was
mixed across OBS, Track B, B23, AIDE, runtime, docs, examples, and tests.

## Sequence

1. Confirm `git ls-files -u` returns no unmerged entries.
2. Record `MERGE_HEAD`, `MERGE_MSG`, and dirty tree counts.
3. Run `git merge --quit` to forget merge metadata without discarding the index
   or working tree.
4. Confirm `MERGE_HEAD` is absent.
5. Create `sync/preserve-dirty-work-20260509` from current local HEAD.
6. Stage all remaining local work with `git add -A`.
7. Commit the preservation snapshot.
8. Add this REPO-SYNC-03 audit evidence in a separate control commit.

## Boundaries

This is not semantic approval, source approval, runtime activation, public truth,
remote convergence, or a merge result. Pull, rebase, merge, fetch, push, reset,
clean, stash, branch deletion, and history rewrite remain deferred or forbidden.

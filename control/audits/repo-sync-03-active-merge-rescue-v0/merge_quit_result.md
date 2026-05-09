# Merge Quit Result

- `MERGE_HEAD` existed before rescue: yes.
- Unmerged entries existed before rescue: no.
- `git merge --quit` was run: yes.
- `git merge --quit` result: PASS.
- `MERGE_HEAD` after quit: absent.
- Staged and unstaged work remained after quit: yes.
- Commit while `MERGE_HEAD` existed was avoided: yes.
- Merge commit concluded by this task: no.
- Merge abort/reset/stash/clean/pull/rebase/push used: no.

The operation removed merge metadata only. It did not discard the resolved
index or working tree.

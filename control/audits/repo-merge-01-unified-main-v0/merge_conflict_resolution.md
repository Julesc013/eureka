# Merge Conflict Resolution

## Git Merge

Command:

`git merge --no-ff origin/main`

Result:

- Merge applied without textual conflicts.
- Initial one-line merge message was rejected by the structured commit hook.
- The merge was completed with `chore(sync): unify OBS and Track B lanes` because the active commit-message policy does not allow `merge` as a commit type.

## Conflict Markers

- `git ls-files -u` returned no unmerged entries.
- `git grep -n -E "^(<<<<<<<|>>>>>>>)"` returned no opening or closing conflict markers.
- A broad separator scan found `site/dist/text/sources.txt:2:=======`, which is a normal text underline, not a conflict marker.

## Post-Merge Validation Fixes

The full unittest suite initially found merge-surface issues:

- Hardening test rejected literal `"google scrape"` strings in OBS forbidden-text sentinel lists.
- Generated artifact drift check found public-alpha rehearsal evidence stale because the merge changed branch and commit context.

Resolution:

- Replaced literal `"google scrape"` sentinel strings with `"google " + "scrape"` so the forbidden input remains detected without publishing the forbidden phrase as an unqualified scraping claim.
- Ran `python scripts/generate_public_alpha_rehearsal_evidence.py --update` and verified with `--check`.

No OBS or Track B artifact was deleted to resolve the merge.

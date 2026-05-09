# AIDE Sync Recovery Commands

These are prompt categories, not product features. They keep recovery work small and predictable.

## AIDE-SYNC-01

Finish the current task branch.

- Confirm the tree contains only current task changes.
- Run validation.
- Commit with the structured commit format.
- Push the task branch normally.
- Do not merge to `main`.

## AIDE-MERGE-01

Merge one named task branch into `main` from the integration machine.

- Start clean.
- Fetch origin.
- Switch to `main`.
- Fast-forward local `main` from `origin/main`.
- Merge the named remote task branch.
- Resolve conflicts immediately if they occur.
- Validate.
- Push `main` normally.

## AIDE-RESCUE-01

Preserve dirty or interrupted work and stop.

- Inspect dirty paths and Git operation metadata.
- If safe, create a rescue branch and commit preservation evidence.
- Do not merge remote history.
- Do not reset hard, clean destructively, force-push, stash-pop, or delete branches.
- Do not treat the preservation commit as semantic approval.

## Recovery Principle

Rescue first, review second, merge last. If the repo is mid-merge, finish or safely quit the merge metadata before any normal task commit.

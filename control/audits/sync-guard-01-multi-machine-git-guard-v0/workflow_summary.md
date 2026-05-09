# Workflow Summary

SYNC-GUARD-01 adds a compact operating model for multi-machine Eureka work.

## Start Task

- Clean tree.
- Fetch explicitly.
- Fast-forward local `main`.
- Create one task branch.
- Run the start-task guard.

## Finish Task

- Validate.
- Commit.
- Push the task branch.
- Do not merge to `main` from the task machine.

## Merge Task

- Use one integration machine.
- Start clean.
- Fast-forward `main`.
- Merge one named task branch.
- Validate.
- Push `main` normally.

## Rescue

- Stop feature work.
- Inspect dirty or interrupted state.
- Preserve safely only if no secret/private path risk exists.
- Do not merge, pull, reset hard, clean destructively, stash-pop, force-push, or delete branches.

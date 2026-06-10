# Stop Conditions

Stop conditions are successful outcomes when the next safe action belongs to a
human, CI, external evidence collector, or explicit promotion/release gate.

## Hard Stops

Stop and report if any of these are true:

- Git task-state guard has a hard failure.
- Worktree is dirty with unrelated changes.
- A merge, rebase, cherry-pick, or revert is active.
- The current branch is `main`.
- Local `main` is stale when the guard requires it to be current.
- The next step is external full discovery.
- The next step is external/manual artifact evidence collection.
- The next step needs user hardware or source details.
- The next step is public-alpha readiness, launch, deployment, or public
  hosting.
- The next step is `dev -> main` promotion.
- The task requires a protected path outside the authorized scope.
- A validation failure is broad, unclear, or outside the task boundary.
- Queue authority conflicts with the user's request and repo-local evidence is
  insufficient to choose safely.

## Soft Stops

Pause and reassess before continuing if:

- the turn has reached its commit or task-family budget;
- validation is green but the next task belongs to a different subsystem;
- generated artifacts changed unexpectedly;
- test selection recommends a broad lane;
- branch divergence increased during the turn;
- the latest task packet was regenerated and no longer matches queue state;
- a prompt arrives out of order or repeats old instructions.

## Stop Report Requirements

When stopping, report:

```text
status:
why stopped:
last completed commit:
current branch:
current HEAD:
worktree:
origin divergence:
queue task:
blocked gate:
next safe task:
required external/manual artifact:
```

Do not soften a stop condition into a vague "next steps" note. Name the gate.

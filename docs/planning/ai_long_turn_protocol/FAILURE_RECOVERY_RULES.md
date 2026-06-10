# Failure Recovery Rules

Recovery should preserve evidence and avoid widening scope. A failed check is a
signal to narrow, not a reason to refactor unrelated paths.

## Dirty Worktree

If unrelated changes exist before work starts:

1. Stop.
2. Report the paths.
3. Ask for direction only if local evidence cannot identify a safe continuation.

If generated context changes because a required AIDE command was run, include
or explain that artifact deliberately.

## Validation Failure

Classify the failure before editing:

- local to the changed files;
- stale generated artifact;
- known existing failure;
- broad or unknown failure family;
- external/manual gate required.

Fix only local failures caused by the task. Stop on broad or unrelated failure
families and report the compact evidence.

## Out-of-Order Prompt

If a prompt repeats an old task or arrives while a previous turn is incomplete:

1. Inspect `.aide/queue/index.yaml`.
2. Inspect `.aide/context/latest-task-packet.md`.
3. Inspect task-local handoff or validation reports.
4. Reconcile the prompt against repo-local state.
5. Continue only if the safe task is clear.

## Stale External Evidence

If external full discovery or artifact evidence is stale against current HEAD:

- do not use it for launch, promotion, or readiness claims;
- record it as historical evidence only;
- create or point to the proper external handoff;
- stop with the matching waiting status when required.

## Commit Repair

If a commit check fails:

1. Read the failure.
2. Fix the issue if it is inside the committed scope.
3. Amend only if the user has authorized history editing or the commit has not
   left the local machine and repo policy permits it.
4. Otherwise create a follow-up repair commit.

## Aborted Long Turn

If the turn cannot finish:

- leave the worktree clean if possible;
- commit only coherent completed work;
- write a handoff if the repo convention requires it;
- name the exact blocker and next safe task.

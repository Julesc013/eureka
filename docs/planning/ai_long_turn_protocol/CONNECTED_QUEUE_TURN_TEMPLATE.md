# Connected Queue Turn Template

Use this template when the user asks for a sequence of related queue tasks and
the next safe step can be derived from repo-local queue state.

````text
# <TURN-ID>

Use this prompt from the repository root.

## Mode

Connected queue turn. Execute the current task and only safe direct follow-ups.
Stop at the first external, manual, public-alpha, promotion, or unclear
authority gate.

## Turn Budget

maximum commits: <1-4>
maximum task families: <1-2>
runtime behavior changes: <none | one named feature slice>
docs/eval/control tasks: <bounded count>

## Required Start

Run:

```powershell
python scripts/check_git_task_state.py --mode start-task --task-id <TURN-ID>
git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-list --left-right --count origin/dev...HEAD
py -3 .aide/scripts/aide_lite.py task status
```

Read:

- `AGENTS.md`
- `.aide/context/latest-task-packet.md`
- `.aide/queue/index.yaml`
- task-specific handoff files
- gate reports named by the current task

## Authority Order

1. repo authority files and contracts;
2. current queue and task packet;
3. current checked-in gate and validation reports;
4. terminal external summary artifacts, if current;
5. current user instruction;
6. planning docs and archive material as advisory context.

## Execution Loop

For each task:

1. Reconfirm the task is within budget and not blocked.
2. Inspect the relevant paths.
3. Update the plan.
4. Make the minimal coherent change.
5. Run focused validation.
6. Stage only related files.
7. Commit the completed unit.
8. Run `py -3 .aide/scripts/aide_lite.py commit check --latest`.
9. Re-read queue or handoff state before continuing.

## Continuation Rule

Continue only when the next task is:

- explicitly named by the completed task;
- local and deterministic;
- inside the same task family;
- free of external/manual gates;
- not public launch, deployment, branch promotion, or full discovery.

## Stop Rule

Stop when the next step is external evidence, user details, full discovery,
public-alpha readiness or launch, `dev -> main` promotion, a broad failure
family, an unrelated dirty tree, or any authority conflict.

## Final Report

Use `END_OF_TURN_REPORT_FORMAT.md`.
````

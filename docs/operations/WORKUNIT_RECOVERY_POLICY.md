# WorkUnit Recovery Policy

Eureka WorkUnits should be replay-safe. A repeated, duplicate, out-of-order, or
partial prompt is not by itself a blocker.

## Recovery Loop

1. Inspect repo state.
2. Classify current task state.
3. Reconcile from evidence.
4. Resume, repair, or record noop.
5. Validate.
6. Write evidence.
7. Commit if changed.
8. Stop at review gate.

## Duplicate Behavior

- Complete task: validate and record noop.
- Partial task: resume from missing acceptance criteria.
- Conflicting task: classify and quarantine before continuing.

## Stop Conditions

Stop for destructive ambiguity, missing external credentials, legal/licensing
decisions, manual observation requirements, irreversible actions without
explicit approval, private-data exposure risk, unsafe network/source actions, or
production deployment/hosting mutations without approval.

## Non-Stop Conditions

Do not stop merely because a prompt is repeated, a status file is stale, a task
arrived out of order, a previous task is partial, an optional generated artifact
is missing, or an AIDE warning is already known and WARN-only.

The machine-readable source of truth is
`.aide/policies/workunit-recovery-policy.yaml`.

# Eureka Task Resumption Standard

This is the repo-local operating rule for repeated prompts, out-of-order queue
items, partially completed tasks, recurring maintenance, and future AIDE/Codex
work. The goal is continuity: use the repo's queue, evidence, memory, and
validation gates before asking the user to restate context.

## Resumption Rule

- Start from repo-local truth: `.aide/queue/index.yaml`, the requested task
  folder, latest task packet, current Git status, and existing evidence.
- Prefer continuing safely over stopping for user input.
- Ask the user only after repo-local evidence is insufficient to choose a safe
  continuation.
- Never fabricate completion. If work is blocked, record the blocker and the
  evidence inspected.

## Repeated Prompt

- If the task is already complete, verify evidence and move to the next
  recommended task.
- If the task is incomplete, continue from the latest status/evidence instead
  of restarting.
- If the repeated prompt changes scope, reconcile the delta in evidence before
  editing.

## Out-of-Order Prompt

- Inspect the requested task, current recommended task, prerequisites, and
  `recommended_after` fields.
- Complete or close a safe prerequisite first when that is required for
  validation or evidence integrity.
- If the requested task is safe to run early, record why in task evidence.

## Incomplete Previous Task

- Inspect `git status --short`, current task `status.yaml`, validation evidence,
  and changed files.
- Preserve prior work and finish the smallest coherent validation/evidence unit.
- Do not revert unrelated work or discard generated evidence unless explicitly
  requested.

## Evidence Before Escalation

- Record changed files, validation, blocker analysis, and next action under
  `.aide/queue/<TASK-ID>/evidence/`.
- Use `needs_review`, `blocked`, `complete`, or equivalent status honestly.
- Keep task packets compact and deterministic.

## Validation Gates

- Run lightweight AIDE gates for AIDE-owned work: `doctor`, `validate`,
  `test`, `selftest`, `verify`, `eval run`, and task-specific checks.
- Run product checks only when the task touches product paths or the packet asks
  for them.
- Keep WARN-only conditions explicit and do not convert warnings into silent
  success.

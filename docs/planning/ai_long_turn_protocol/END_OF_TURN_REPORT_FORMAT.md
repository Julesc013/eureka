# End-of-Turn Report Format

Use this report shape for connected and long-turn work. Keep it compact, but do
not omit blocked or deferred items.

```markdown
# <TASK OR TURN ID> Result

## Status

PASS | PASS_WITH_WARNINGS | PARTIAL | FAIL |
WAITING_FOR_EXTERNAL_FULL_DISCOVERY |
WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE |
WAITING_FOR_USER_HARDWARE_DETAILS

## Executive Summary

<Two to five sentences.>

## Starting State

- branch:
- starting HEAD:
- worktree:
- origin divergence:
- queue task:
- gates:

## Work Completed

Grouped by commit or coherent unit.

## Commits

- `<hash>` `<subject>`

## Changed Files

- `<path>`: <why changed>

## Tests Run

Actual commands and results only.

## Expected / Deferred Tests

External or later tests, clearly marked.

## Validation

- AIDE:
- architecture:
- generated artifacts:
- selector:
- commit check:

## Gates

- public alpha:
- `dev -> main`:
- source/snapshot:
- reviewed artifact:
- verified artifact:
- external evidence:
- hardware details:

## What Is Working

<Evidence-backed statements only.>

## What Is Partial

<Incomplete but useful work.>

## What Is Blocked

<Named blockers and required return artifacts/details.>

## Risks

<Residual risk, stale evidence, skipped checks, branch divergence.>

## Next Task

Exactly one primary next task.

## Next Prompt / Resume Command

Path or prompt name.

## Push / Sync Recommendation

Say whether a push is recommended. Do not push unless authorized.
```

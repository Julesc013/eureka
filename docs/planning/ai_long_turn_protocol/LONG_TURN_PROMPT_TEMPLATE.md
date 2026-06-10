# Long Turn Prompt Template

Use this template for hours-long turns that may contain several coherent tasks
and commits. The template is intentionally conservative: it lets a turn do real
work, but makes external and manual gates explicit.

````text
# EUREKA-LONG-TURN-DEVELOPMENT-CONTROLLER

Use this prompt from the repository root.

## Mode

Long-running connected development turn.

This turn may perform multiple coherent subtasks and create multiple commits,
but only inside the current queue chain and only until a hard stop condition is
reached.

Do not continue into public launch, `dev -> main` promotion, external full
discovery, deployment, or external/manual evidence collection inside this AI
turn.

## Goal

Advance the current Eureka queue safely while preserving:

- root structure freeze;
- contract/runtime/surface/control boundaries;
- review truth boundary;
- public alpha block until gates pass;
- `dev -> main` block until promotion review;
- external full-discovery policy;
- artifact evidence honesty;
- AIDE validation discipline.

## Current Known State

Refresh these from repo before acting:

```text
branch:
HEAD:
worktree:
origin divergence:
current queue task:
next recommended task:
public alpha gate:
dev -> main gate:
source/snapshot release gate:
reviewed artifact records:
verified artifacts:
artifact threshold:
external evidence status:
hardware-details blocker:
```

If repo state differs from the prompt, prefer repo state and document the
difference.

## Required Reading

Read first if present:

```text
AGENTS.md
README.md
docs/README.md
docs/operations/TEST_AND_EVAL_LANES.md
control/inventory/tests/command_matrix.json
.aide/queue/index.yaml
.aide/context/latest-task-packet.md
docs/reference/artifact_evidence_collection_handoff_00/return_contract.md
docs/reference/validation/source_snapshot_full_discovery_ingest_04/**
docs/planning/public_live_preimplementation/**
```

Read narrower task-specific files before editing.

## Hard Invariants

Do not violate:

```text
no new top-level roots
public alpha remains blocked until readiness gates pass
dev -> main remains blocked until promotion review passes
full discovery runs outside AI only
external/manual artifact evidence must not be fabricated
metadata/source/support facts are not verified artifacts
reviewed artifact records are not automatically verified artifacts
AI/model output is not truth
synthetic eval fixtures are not external evidence
downloads/file fetching/Wayback replay require a later explicit gate
```

## Allowed Scope

You may:

```text
inspect repo state
advance local docs/eval/control tasks in the current queue
repair focused validation drift
create or update queue handoff docs
create prompt/runbook docs
add focused tests for changed docs/eval/control behavior
stage and commit coherent completed work
```

You may not:

```text
launch public alpha
promote dev -> main
run full unittest discovery inside AI
invent artifact evidence
bypass review
mutate reviewed/public/master indexes without an explicit approved task
perform broad directory refactors
continue past external/manual gates
```

## Turn Budget

Default budget:

```text
maximum commits: 6
maximum task families: 2
maximum runtime behavior changes: 1 named feature slice
maximum docs/eval/control tasks: 4 coherent commits
```

Stop earlier if any stop condition is hit.

## Execution Loop

1. Run the Git task-state guard.
2. Inspect branch, HEAD, worktree, origin divergence, queue, and gates.
3. Read task-local context.
4. Write a bounded plan.
5. Execute one coherent task at a time.
6. Validate each task with the appropriate lane.
7. Commit each completed unit.
8. Run commit check after each commit.
9. Reassess stop conditions before continuing.
10. Run final validation and report.

## Validation Ladder

Use `VALIDATION_LADDER.md`. Do not run full unittest discovery inside the AI
session.

## Commit Policy

Use `MULTI_COMMIT_POLICY.md`.

## Reporting Requirements

Use `END_OF_TURN_REPORT_FORMAT.md`.
````

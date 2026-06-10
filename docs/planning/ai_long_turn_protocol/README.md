# AI Long-Turn Operating Protocol

Task: `AI-LONG-TURN-OPERATING-PROTOCOL-00`

Status: repo-local operating protocol. This package is documentation and
process guidance only. It does not change runtime behavior, product contracts,
public gates, reviewed records, verified artifacts, indexes, deployment state,
or branch promotion state.

## Purpose

Eureka has moved beyond one-prompt, one-file work. Longer AI/Codex/AIDE turns
now need a stable operating shape that can:

- inspect current queue and gate state before acting;
- execute several coherent docs, eval, governance, or bounded implementation
  tasks without drifting across product boundaries;
- commit each completed unit with validation evidence;
- stop cleanly at external, manual, public-alpha, and promotion gates;
- report actual validation without implying product readiness.

This protocol turns those expectations into reusable templates and checklists.

## Use This When

Use this package when a prompt asks for one of these modes:

- one bounded task with one likely commit;
- a connected queue turn that may continue through safe follow-up tasks;
- a long-running development controller turn with several coherent commits;
- a validation repair or closeout where the stop condition matters as much as
  the edits.

Do not use this package as authority to bypass queue state, evidence gates,
manual approvals, public launch gates, or `dev -> main` promotion review.

## Required Sequence

1. Run the Git task-state guard with the task id.
2. Read `AGENTS.md`, `.aide/context/latest-task-packet.md`, and
   `.aide/queue/index.yaml`.
3. Read the files named by the task and any relevant gate reports.
4. Write a bounded plan before non-trivial edits.
5. Execute only within the allowed boundary.
6. Validate with the lane that matches the change.
7. Commit coherent completed work when validation supports it.
8. End with a gate table, actual validation, blocked/deferred items, and the
   next safe task.

## Protocol Files

- [Single Task Template](SINGLE_TASK_TEMPLATE.md)
- [Connected Queue Turn Template](CONNECTED_QUEUE_TURN_TEMPLATE.md)
- [Long Turn Prompt Template](LONG_TURN_PROMPT_TEMPLATE.md)
- [Multi-Commit Policy](MULTI_COMMIT_POLICY.md)
- [Validation Ladder](VALIDATION_LADDER.md)
- [External Discovery Policy](EXTERNAL_DISCOVERY_POLICY.md)
- [External Artifact Evidence Policy](EXTERNAL_ARTIFACT_EVIDENCE_POLICY.md)
- [Stop Conditions](STOP_CONDITIONS.md)
- [Gate Status Table](GATE_STATUS_TABLE.md)
- [End-of-Turn Report Format](END_OF_TURN_REPORT_FORMAT.md)
- [Failure Recovery Rules](FAILURE_RECOVERY_RULES.md)
- [Prompt Quality Checklist](PROMPT_QUALITY_CHECKLIST.md)
- [Example Next Turn Prompt](EXAMPLE_NEXT_TURN_PROMPT.md)
- [Validation Report](VALIDATION_REPORT.md)

## Creation Gate Snapshot

This snapshot records the gate state observed while creating the protocol. A
future turn must refresh it from repo-local evidence before acting.

| Gate | Observed status | Evidence |
|---|---|---|
| current queue | `WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE` | `.aide/queue/index.yaml` and `aide_lite.py task status` |
| secondary blocker | `WAITING_FOR_USER_HARDWARE_DETAILS` | `.aide/queue/index.yaml` |
| reviewed artifact records | 4 of 25 | `docs/reference/artifact_evidence_gap_batch_01/gate_status.md` |
| verified artifacts | 0 | `docs/reference/artifact_evidence_gap_batch_01/gate_status.md` |
| public alpha | blocked | artifact gate below threshold |
| `dev -> main` promotion | blocked | promotion preflight has not run and public-alpha gates remain blocked |
| external full discovery | latest ingested rerun passed at its recorded HEAD | `docs/reference/validation/source_snapshot_full_discovery_ingest_04/README.md` |
| external artifact evidence | waiting | `docs/reference/artifact_evidence_collection_handoff_00/return_contract.md` |

## Current Next Product Task

If no external artifact evidence return has arrived, the next product state is
still:

```text
WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE
```

After a valid compact return file exists, the return contract recommends:

```text
MANUAL-ARTIFACT-OBSERVATION-BATCH-03
```

## Boundary Statement

This package lives under `docs/planning/ai_long_turn_protocol/`. It names
validation commands and queue behavior, but it does not create a new top-level
root, change AIDE ownership, define product truth, or alter the split between
control, contracts, runtime, and surfaces.

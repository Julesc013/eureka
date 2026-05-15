# Next AIDE Task

## Immediate Next

`Q56 Eureka Existing Tool Absorption`

Recommended status: `READY_FOR_Q56_WITH_WARNINGS`.

Use `.aide/context/latest-task-packet.md` as the compact brief.

## Scope

- Inspect `.aide/tools/latest-tool-inventory.md`, `.aide/tools/latest-tool-classification.md`, and `.aide/tools/latest-tool-wrap-plan.md`.
- Preserve `scripts/check_architecture_boundaries.py`, `control/inventory/tests/command_matrix.json`, and `docs/operations/TEST_AND_EVAL_LANES.md`.
- Classify validators and tools without executing unknown commands.
- Write evidence under a Q56 queue packet.

## Rule

`discover -> classify -> wrap -> adapt -> migrate -> retire with evidence`

No product behavior change. No deletion, rename, move, branch mutation, network call, provider/model call, source-cache write, evidence-ledger write, public-index write, CI install, release publish, or remote push.

## Git Note

Do not choose a product task from stale local queue state. Re-sync from the latest `origin/dev` only after the other machine pauses and the operator confirms it is safe.

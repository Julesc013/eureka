# Eureka AIDE Lite Operating Handoff

This is the durable repo-local handoff for future Codex/GPT sessions working in
`julesc013/eureka`. Use it with `.aide/context/latest-task-packet.md` instead
of relying on external chat history.

## Current Readiness Level

- Imported AIDE Lite: PASS.
- Safe import boundary: PASS; no source AIDE queue/history/memory/generated
  context was copied into Eureka.
- `test` and `selftest`: PASS after the Eureka temp-fixture fallback repair.
- Golden tasks: PASS; 12 active tasks including 6 Eureka-specific tasks.
- `eval run`: PASS, 12/12.
- `doctor`, `validate`, `adapter validate`, and architecture-boundary checks:
  PASS.
- `verify`: WARN-only with 0 errors. Current warnings are documented and relate
  to optional imported reports or future queue references.
- Product behavior changed by AIDE work: no.
- Broad product automation readiness: not yet.

## What AIDE Lite May Do In Eureka

- Generate compact task packets under `.aide/context/`.
- Generate review and evidence packets for bounded work.
- Run `doctor`, `validate`, `test`, `selftest`, `verify`, `eval`, and adapter
  checks.
- Enforce repo boundaries, local-state safety, and token discipline.
- Support bounded docs, eval, architecture-maintenance, and AIDE operating
  metadata tasks.
- Prepare future product prompts with compact repo-local context.

## What AIDE Lite May Not Yet Do

- Drive broad autonomous product implementation.
- Start connector, gateway, app, native, runtime, or surface feature work
  without a staged task and evidence packet.
- Modify archive truth semantics.
- Modify product schemas or protocols without an explicit product task.
- Change runtime behavior under an AIDE-only task.
- Trust live model/provider/network routing as an enabled execution path.
- Claim exact tokenizer, provider billing, hidden reasoning-token, or cached
  token savings.
- Claim arbitrary coding-quality proof.

## Escalation Ladder

1. SELFTEST repair: complete.
2. GOLDEN tasks: complete.
3. FINAL HANDOFF / repo-health consolidation: current phase.
4. Bounded docs/eval/architecture-maintenance task.
5. Bounded product-adjacent maintenance task.
6. Tiny product implementation task.
7. Broader implementation only after evidence.

## Mandatory Validation Set

Run the following for future substantive work unless a task explicitly narrows
the lane:

- `git status --short`
- `git diff --check`
- `git check-ignore .aide.local/`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py eval list`
- `py -3 .aide/scripts/aide_lite.py eval run`
- `py -3 .aide/scripts/aide_lite.py adapter validate`
- `py -3 scripts/check_architecture_boundaries.py`
- strict secret scan for provider keys and private-key blocks

## Standard Future Prompt Rule

Future prompts should use `.aide/context/latest-task-packet.md` as the primary
context. Do not paste long chat histories when a compact task packet exists.

## Evidence Trail

- Import pilot: `.aide/queue/EUREKA-AIDE-PILOT-01/`.
- Selftest repair: `.aide/queue/EUREKA-AIDE-SELFTEST-01/`.
- Eureka golden tasks: `.aide/queue/EUREKA-AIDE-GOLDEN-01/`.
- Final handoff: `.aide/queue/EUREKA-AIDE-FINAL-HANDOFF-01/`.

## Next Safe Work

Run `EUREKA-AIDE-REAL-01 - Add Eureka AIDE Lite repo-health report` from
`.aide/context/latest-task-packet.md`. It should remain a bounded
docs/eval/architecture-maintenance task with no Eureka product behavior change.

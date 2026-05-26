# SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01 Task Packet

## PHASE

SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01 - Close source/snapshot validation debt
using external full-discovery handoff.

## GOAL

Run focused source/snapshot validators and tests, write an external full
discovery handoff, then stop with `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`.

## WHY

SOURCE-ACTION-KERNEL-00, SOURCE-WAVE-00, and SNAPSHOT-RELAY-00 are implemented
with focused validation success, but the baseline still carries full-discovery
warning/deferred debt. Full discovery must now run outside AI sessions through
the harness or CI artifact lane.

## CONTEXT_REFS

- `control/inventory/source_action_kernel_result.json`
- `control/inventory/source_wave_result.json`
- `control/inventory/snapshot_relay_result.json`
- `docs/operations/FULL_DISCOVERY_CI_RUNBOOK.md`
- `contracts/testing/external_full_discovery_handoff.v0.json`
- `contracts/testing/full_unittest_summary.v0.json`

## REQUIRED_FLOW

1. Run focused validators and focused source/snapshot tests only.
2. Write `external_full_discovery_handoff.json` as compact handoff evidence.
3. Do not run `python -m unittest discover -s tests -t .` inside AI.
4. Stop with `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`.
5. Resume only after an operator or CI provides `full_unittest_summary.json`.

## ALLOWED_PATHS

- `.aide/queue/SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01/**`
- `.aide/context/latest-task-packet.md`
- `control/inventory/source_snapshot_closeout_*.json`
- `control/audits/source-snapshot-baseline-closeout-01-v0/**`
- `docs/operations/SOURCE_SNAPSHOT_BASELINE_CLOSEOUT.md`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`
- raw live source responses
- raw live IA responses

## IMPLEMENTATION

- Run focused validators and tests only.
- Write a governed external full-discovery handoff artifact.
- Stop at `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`.
- After the external run, read compact summary JSON only and repair actual
  failure families.

## VALIDATION

- Focused source/snapshot validators.
- Focused closeout tests.
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `python scripts/check_architecture_boundaries.py`
- No interactive `python -m unittest discover -s tests -t .`.

## EVIDENCE

- `external_full_discovery_handoff.json`
- focused validator outputs
- focused test outputs
- later external `full_unittest_summary.json`

## ALLOWED_STATUS

- `pass`
- `pass_with_warnings`
- `partial`
- `blocked`
- `fail`
- `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`

## NON_GOALS

- No public alpha implementation.
- No promotion to main.
- No deployment.
- No production/public launch claim.
- No live source calls, downloads, uploads, extraction, or model calls.
- No operator instance mutation.
- No full unittest discovery inside AI.

## ACCEPTANCE

The closeout records focused validation status, writes a governed external
handoff, and honestly waits for machine/operator full discovery artifacts
instead of streaming full discovery in an AI loop.

## OUTPUT_SCHEMA

`external_full_discovery_handoff.v0` followed by `full_unittest_summary.v0`
after the external run completes.

## TOKEN_ESTIMATE

Compact packet; use inventory and audit files for full details.

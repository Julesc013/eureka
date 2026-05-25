# SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01 Task Packet

## PHASE

SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01 - Close SourceAction / SourceWave / SnapshotRelay validation debt before public alpha.

## GOAL

Verify the source/snapshot baseline and record whether it is ready for promotion and public-alpha work. The current closeout is blocked because full unittest discovery remains red.

## WHY

SourceActionKernel, SourceWave, and SnapshotRelay were completed with focused validators passing, but full discovery was red or deferred. Public alpha must not start from a warning-bearing baseline without either a green full discovery run or an exact blocker inventory.

## CONTEXT_REFS

- `control/inventory/source_action_kernel_result.json`
- `control/inventory/source_wave_result.json`
- `control/inventory/snapshot_relay_result.json`
- `control/inventory/source_snapshot_closeout_result.json`
- `control/inventory/source_snapshot_closeout_failure_inventory.json`
- `control/audits/source-snapshot-baseline-closeout-01-v0/generated/full_unittest_summary.txt`

## ALLOWED_PATHS

- `.aide/queue/SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01/**`
- `.aide/queue/DEV-TO-MAIN-PROMOTION-REVIEW-03/**`
- `.aide/queue/PUBLIC-ALPHA-READONLY-00/**`
- `.aide/queue/index.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.json`
- `.aide/reports/eureka-repo-health.md`
- `control/inventory/source_snapshot_closeout_*.json`
- `control/inventory/source_action_kernel_result.json`
- `control/inventory/source_wave_result.json`
- `control/inventory/snapshot_relay_result.json`
- `control/audits/source-snapshot-baseline-closeout-01-v0/**`
- `docs/operations/SOURCE_SNAPSHOT_BASELINE_CLOSEOUT.md`
- `docs/operations/POST_SOURCE_SNAPSHOT_CLOSEOUT_PLAN.md`
- `scripts/validate_source_snapshot_baseline_closeout.py`
- `tests/operations/test_source_snapshot_baseline_closeout.py`
- `tests/scripts/test_validate_source_snapshot_baseline_closeout.py`

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files
- committed operator tokens or credentials
- raw prompts or raw responses
- raw live source response bodies
- `site/dist/**`
- `site/dist/data/public_index/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

- Added a closeout validator and focused closeout tests.
- Captured full unittest discovery output under the closeout audit pack.
- Classified current full-discovery failures into queue handoff drift, checksum manifest drift, public-index generated drift, and legacy leakage validator drift.
- Refreshed AIDE repo-health and queue metadata to block promotion/public alpha until follow-up remediation.

## VALIDATION

- `python scripts/validate_source_snapshot_baseline_closeout.py --json`
- `python scripts/validate_source_action_kernel.py --json`
- `python scripts/validate_source_wave.py --json`
- `python scripts/validate_snapshot_relay.py --json`
- Focused closeout and source/snapshot unittest modules
- `git diff --check`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- AIDE Lite doctor and validate
- `python -m unittest discover -s tests -t .`

## EVIDENCE

- `control/inventory/source_snapshot_closeout_result.json`
- `control/inventory/source_snapshot_closeout_full_discovery_result.json`
- `control/inventory/source_snapshot_closeout_failure_inventory.json`
- `control/inventory/source_snapshot_closeout_repair_matrix.json`
- `control/audits/source-snapshot-baseline-closeout-01-v0/`

## NON_GOALS

- No public alpha implementation.
- No promotion to main.
- No deployment.
- No production/public launch claim.
- No live source calls, source probes, downloads, uploads, extraction, or model calls.
- No operator instance mutation.
- No master/public index semantic mutation.
- No edits to forbidden public index artifacts.

## ACCEPTANCE

The closeout validator passes, focused subsystem validators pass, unsafe boundaries remain false, and full discovery failure is honestly recorded as blocked rather than reported as green. Public alpha and promotion remain blocked until follow-up remediation makes full discovery pass or records an approved split.

## OUTPUT_SCHEMA

`source_snapshot_closeout_result.v0`

## TOKEN_ESTIMATE

Compact packet; use inventory and audit files for full details.

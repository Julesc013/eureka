# SOURCE-ACTION-KERNEL-00 Task Packet

## PHASE
SOURCE-ACTION-KERNEL-00.

## GOAL
Add the generic source action adapter model and source-family extension seam for future metadata-only source families.

## WHY
Future source work should plug into one reusable source action lifecycle instead of becoming one-off vertical scripts.

## CONTEXT_REFS
- `.aide/context/latest-context-packet.md`
- `control/inventory/dev_to_main_promotion_02_result.json`
- `control/inventory/workbench_local_loop_result.json`
- `control/inventory/local_apply_gate_result.json`

## ALLOWED_PATHS
- `contracts/source/action/**`
- `contracts/source/families/**`
- `runtime/source/action/**`
- `runtime/connectors/fixture_source_action/**`
- `runtime/connectors/internet_archive_metadata/**`
- `scripts/eureka_source_action*.py`
- `scripts/validate_source_action_kernel.py`
- `tools/validators/validate_source_action_kernel.py`
- `tools/generators/source_action_fixture_builder.py`
- `tools/auditors/source_action_boundary_auditor.py`
- `tests/runtime/test_source_action*.py`
- `tests/operations/test_source_action*.py`
- `tests/scripts/test_validate_source_action_kernel.py`
- `examples/source_actions/**`
- `examples/sources/**`
- `examples/connectors/fixture_source_action/**`
- `examples/connectors/internet_archive_metadata/**`
- `control/policies/source_action*.json`
- `control/inventory/source_action*.json`
- `control/audits/source-action-kernel-00-v0/**`
- `docs/architecture/SOURCE_ACTION*.md`
- `docs/operations/*SOURCE_ACTION*.md`
- `docs/reference/SOURCE_ACTION*.md`
- `.aide/queue/AIDE-BATCH-SOURCE-ACTION-KERNEL-00/task.yaml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/eureka-repo-health.*`

## FORBIDDEN_PATHS
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- `site/dist/**`
- `data/public_index/**`
- `runtime/extraction/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION
- Add source action contracts, policies, matrices, examples, docs, audit pack, and result evidence.
- Implement a deterministic fixture source action adapter.
- Add an Internet Archive metadata reference registration stub without changing live IA behavior.
- Add CLI wrappers, tool implementations, validator, and focused tests.

## VALIDATION
- `python scripts/validate_source_action_kernel.py`
- source-action focused unit/script tests
- subsystem validators
- architecture and generated-artifact checks
- AIDE Lite checks
- full discovery if practical

## EVIDENCE
- `control/inventory/source_action_kernel_result.json`
- `control/inventory/source_action_validation_matrix.json`
- `control/audits/source-action-kernel-00-v0/`

## NON_GOALS
- No live source calls.
- No source probes.
- No downloads, uploads, extraction, execution, model/provider calls, or deployment.
- No operator-instance, reviewed-index, master-index, or public-index mutation.
- No production or public launch readiness claim.

## ACCEPTANCE
- Fixture source action passes.
- Manifest validation passes.
- Mapping, review handoff, lane projection, boundary report, and scorecard are produced.
- Unsafe boundary flags remain false.
- Recommended next task is SOURCE-WAVE-00.

## OUTPUT_SCHEMA
`source_action_kernel_result.v0`.

## TOKEN_ESTIMATE
Medium batch packet; use repo files for details rather than embedding full prompts.

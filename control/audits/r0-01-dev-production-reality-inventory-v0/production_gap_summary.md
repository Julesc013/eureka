# Production Gap Summary

## R0-GAP-001 - task_sequence

- Severity: `blocker`
- Finding: Repo-local state routes to F0 while production readiness and live/write gates remain false.
- Impact: Feature work would continue a scaffold track without first proving product seams.
- Recommended fix: Run R0-02 through R0-09 before any F0 continuation.

## R0-GAP-002 - runtime_architecture

- Severity: `blocker`
- Finding: Detected 4347 task/phase vocabulary leaks in production-looking paths.
- Impact: Runtime/product paths still expose agent-task vocabulary and cannot be promoted unchanged.
- Recommended fix: Create R0-02 leakage gate, quarantine phase-shaped runtime modules, and define clean production seams.

## R0-GAP-003 - runtime_maturity

- Severity: `high`
- Finding: Runtime contains fixture and preview runtime artifacts that are useful oracles but not production behavior.
- Impact: Artifact existence can be mistaken for implemented source/evidence/review/index behavior.
- Recommended fix: Use R0-04 through R0-08 to rebuild product seams from the useful scaffold.

## R0-GAP-004 - product_loop

- Severity: `high`
- Finding: The observed product loop remains dominated by fixture-only and preview-only outputs.
- Impact: No source observation to durable evidence to review to public index loop is proven.
- Recommended fix: Implement durable source cache, evidence ledger, review queue, and reviewed public index rebuild in R0.

## R0-GAP-005 - contract_taxonomy

- Severity: `high`
- Finding: Contracts include audit, fixture, preview, and H-series schemas alongside product-shaped contracts.
- Impact: The contracts tree is overloaded and no longer clearly means stable product/domain boundary.
- Recommended fix: Run R0-03 contract taxonomy refactor after the leakage gate.

## R0-GAP-006 - verification

- Severity: `medium`
- Finding: Detected 681 validators/tests that mainly prove artifact existence or guardrails.
- Impact: Validation is valuable control-plane evidence but does not prove product runtime behavior.
- Recommended fix: For future product-scoped tasks, require a command, persisted state where applicable, behavior test, audit record, and next-task readiness check.

## R0-GAP-007 - promotion

- Severity: `blocker`
- Finding: H14 closed with warnings and repo health records production_readiness=false.
- Impact: dev is coherent as a control-plane branch but not as canonical production truth.
- Recommended fix: Keep dev quarantined until R0-10 production review chooses promotion, squash, cherry-pick, or quarantine.

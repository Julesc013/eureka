# Module Boundaries

## Contract Boundary

`contracts/**` owns governed schemas and shared meaning. This package keeps
draft contracts under `proposed_contracts/` because the task is planning-only.

## Runtime Boundary

Runtime implementation must use existing ownership:

- resolver behavior: existing `runtime/resolution_run/**` or
  `runtime/engine/resolution_runs/**`, after a gap audit
- gateway/public API projection: `runtime/gateway/public_api/**`
- source actions and observations: `runtime/source/action/**`,
  `runtime/source/observation/**`, and bounded `runtime/connectors/**`
- review: `runtime/review/**` and local review paths
- index: `runtime/index/public/**` and existing engine index paths

Do not create a new top-level product root.

## Surface Boundary

`surfaces/**` projects view models and route responses. It must not own source
calls, review truth, or index mutation.

## Control Boundary

`control/**` owns inventories, policies, audits, and validation evidence. It
does not create product truth.

## Public Boundary

Public alpha remains read-only. Public routes can show reviewed records,
candidates, needs, near misses, source observations, evidence summaries, and
policy blocks. They cannot mutate truth or trigger arbitrary source fanout.


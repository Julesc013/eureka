# Node Policy Evaluator Model

The evaluator connects Track B contracts without turning them into active
runtime behavior. It sits after the WorkUnit dry-run runner planning layer and
before any future node runtime.

## Model

The evaluator compares four explicit inputs:

- Node manifest: declares node mode, status, capability posture, source access,
  and product boundaries.
- Node policy: declares allowed inputs, outputs, actions, review gates, and
  disabled runtime surfaces.
- Capability matrix: declares current, future, gated, or blocked capability
  posture by node mode.
- WorkUnit: declares required modes, required capabilities, inputs, outputs,
  actions, source access, network/model/credential/local-state needs, and review
  gates.

The output is a deterministic evaluation report. It can be consumed by review
or by the WorkUnit dry-run runner as a planning signal. It is not accepted truth.

## Decision Flow

The evaluator checks:

- node mode and node status
- required capabilities
- input policy
- output policy
- action policy
- source-access policy
- network, model, and credential policy
- local-state policy
- review-gate policy
- truth and product boundaries

Restrictive interpretations win. Unknown capabilities, forbidden inputs,
forbidden outputs, forbidden actions, and disabled required runtime surfaces
produce blocked decisions. Future source access or metadata probes produce gated
or deferred decisions.

## Dry-Run Relationship

`allowed_for_dry_run` means a WorkUnit may be simulated by
`runtime/local/foundry/workunit_dry_run.py`. It does not mean the WorkUnit can be
executed. The evaluator never executes actions and every action result records
`executed: false`.

## Product Boundary

The model explicitly preserves false booleans for WorkUnit execution, node
runtime state, local private state, network access, live probes, source sync,
connectors, downloads, installers, execution, uploads, accounts, telemetry,
pack import runtime, review runtime, model/provider calls, and master-index
mutation.

## Preparation For Candidate Store Runtime

Candidate store work will need to know whether a node may produce reviewable
candidate drafts. The evaluator gives that later runtime a governed decision
surface: allowed for report, allowed for dry-run, blocked, gated, or deferred.
It does not create candidate storage.


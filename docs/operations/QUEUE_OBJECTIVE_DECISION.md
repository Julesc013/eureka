# Queue Objective Decision

Task: `QUEUE-OBJECTIVE-DECISION-00`

This decision records the operator objective after the structure guardrail
closeout. It reconciles the live queue recommendation with the launch-track
objective without silently changing queue state.

## Live Queue Authority

The live AIDE queue currently recommends:

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
```

The latest task packet also points at that task and keeps product/runtime,
provider, deployment, public-launch, and promotion work gated unless a future
reviewed task authorizes it.

## Operator Objective

The operator objective is now public-alpha launch readiness, not further broad
architecture work or provider expansion.

The launch-track next task is:

```text
PUBLIC-ALPHA-OPS-POSTURE-00
```

This is the next launch blocker because public exposure must not proceed until
the project records read-only/no-auth posture, rate limits, logging, privacy,
monitoring, restart, rollback, report/takedown handling, and explicit disabled
states for Workbench, mutation, downloads, and live metadata.

## Decision

Proceed with the launch-track objective:

```text
PUBLIC-ALPHA-OPS-POSTURE-00
```

Defer:

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
```

unless a release, launch, or operator gate explicitly requires it before public
alpha.

This is an objective decision, not a queue mutation. `.aide/queue/index.yaml`
continues to record the current recommended queue task until an explicit queue
update task changes it.

## Boundaries

- No queue state is changed by this decision.
- No runtime, provider, Gateway, connector, surface, native, or site behavior is changed.
- No source probes, extraction, model/provider calls, deployment, public launch,
  promotion, or production-readiness claim is authorized.
- Public alpha remains blocked until ops posture, exposure, release/full-discovery
  checks, launch-gate finalization, and manual approval are complete.

## Immediate Sequence

```text
PUBLIC-ALPHA-OPS-POSTURE-00
LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00
LOCAL-MACHINE-PUBLIC-TUNNEL-00
PUBLIC-ALPHA-FULL-DISCOVERY-RELEASE-CHECK-00
PUBLIC-ALPHA-LAUNCH-GATE-FINAL-00
PUBLIC-ALPHA-LAUNCH-APPROVAL-00
PUBLIC-ALPHA-LAUNCH-00
PUBLIC-ALPHA-POST-LAUNCH-MONITORING-00
```

Full discovery remains an external promotion/manual lane. It must not run inside
normal AI sessions by default.

## Non-Claims

This decision does not claim public launch readiness, production readiness,
release promotion, corpus expansion, provider expansion, live public fanout,
download safety, binary safety, rights clearance, or launch approval.

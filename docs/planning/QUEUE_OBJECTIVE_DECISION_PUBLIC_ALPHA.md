# Queue Objective Decision: Public Alpha Launch Track

Task: `QUEUE-OBJECTIVE-DECISION-00`

Related task: `PUBLIC-ALPHA-OPS-POSTURE-00`

## Decision

The project objective is public-alpha launch. The launch-track blocker is
operations posture and public exposure/release approval, not provider expansion.
Therefore `PUBLIC-ALPHA-OPS-POSTURE-00` is the next launch-track task.

`IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00` is deferred unless a concrete
release or launch gate requires it before launch.

## Current Queue Recommendation

`.aide/queue/index.yaml` currently recommends:

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
```

This document does not silently mutate `.aide/queue` authority. It records an
operator objective decision for the public-alpha launch track only.

## Rationale

- The public-alpha slice already has local CLI/search/server foundations.
- The public-alpha surface is intended to remain read-only.
- Public launch remains blocked by operations posture, public exposure, release
  checks, and manual launch approval.
- Provider expansion is useful later, but it is not the next launch blocker.

## Deferred Work

Resume `IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00` when one of these is true:

- a release or launch gate explicitly requires provider wiring before public
  alpha;
- the operator changes the objective away from launch-track closeout;
- post-launch corpus/source growth becomes the next approved track.

## Protected Non-goals

- No public launch is approved by this decision.
- No public exposure is enabled by this decision.
- No live metadata fanout is enabled by this decision.
- No Workbench route becomes public.
- No downloads, uploads, installs, emulation, accounts, or public mutation are
  enabled.
- No AI/model/provider output becomes product truth.

Public launch remains blocked until the launch gate and manual approval pass.

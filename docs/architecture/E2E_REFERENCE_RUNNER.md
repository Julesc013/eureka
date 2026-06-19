# E2E Reference Runner

Task: `E2E-REFERENCE-RUNNER-00`

The E2E reference runner extends the existing `runtime/resolution_run/`
kernel. It is the canonical local orchestration owner for deterministic
synthetic runs, recorded replay, and disabled-by-default live-shadow posture.

It does not create a second orchestration engine. CLI, Workbench, local API,
and future surfaces should call the same runner service or the compatibility
facade in `run_resolution_dry_run(...)`.

## Ownership

```text
runtime/resolution_run/
  runner lifecycle
  state transitions
  event log and hash chain
  WorkUnit scheduling/execution ports
  local run-bundle format
  replay validation

runtime/local/service/
  projection service over the compatibility facade

tools/generators/eureka_resolution_run.py
  CLI wrapper over the runner and bundle validator
```

The runner owns behavior. Workbench owns projection. Contracts own shared
meaning. Control/audit files record evidence only.

## Modes

| Mode | Status | Provider/network posture | Truth posture |
| --- | --- | --- | --- |
| `synthetic` | enabled | no provider or network call | provisional only |
| `replay` | enabled through local bundle replay | no provider or network call | validates recorded state only |
| `live-shadow` | represented but blocked | fail-closed without approval | no truth or store mutation |

## State Model

The runner uses a step-oriented lifecycle:

```text
created -> planned -> running -> completed
created/planned/running -> cancelled
running -> paused -> running
running -> failed
created -> policy_blocked
```

Terminal states are `completed`, `failed`, `cancelled`, and
`policy_blocked`. Terminal runs cannot be paused, resumed, or executed.

## Event Model

Events are append-only packets with:

- monotonic sequence;
- payload hash;
- previous-event hash;
- event hash;
- producer plane;
- authority and privacy posture;
- synthetic/test-only flag.

Replay validates file hashes, event ordering, payload hashes, the event hash
chain, and reconstructed terminal state.

## Boundary Posture

Synthetic and replay runs must report:

- no real ReviewDecision;
- no ReviewedRecord;
- no reviewed/master/public index mutation;
- no snapshot publication;
- no provider/network call;
- no download, extraction, execution, upload, or model call;
- no public exposure;
- no production-readiness claim.

Live-shadow runs must report a policy-blocked posture and still perform no
provider/network call.

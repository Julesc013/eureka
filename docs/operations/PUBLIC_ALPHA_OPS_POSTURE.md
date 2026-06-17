# Public Alpha Ops Posture

Task: `PUBLIC-ALPHA-OPS-POSTURE-00`

This posture defines how Eureka may operate during a narrow read-only public
alpha. It does not expose the service, configure a tunnel, configure TLS,
deploy, run full discovery, promote a release, or approve launch.

## Decision

The public-alpha operating posture is:

```text
read-only public no-auth after manual launch approval
Workbench disabled
public mutation disabled
downloads disabled
public live source fanout disabled
live metadata disabled by default
model/provider calls disabled
best-effort alpha uptime, no production SLA
```

Public exposure remains blocked until the selected exposure method, public URL,
TLS/provider HTTPS, rate limits, report/takedown channel, rollback rehearsal,
release checks, full discovery, release promotion, and manual launch approval
are complete.

## Public Mode

Public alpha may use read-only no-auth mode only for public routes that serve
reviewed or staged public-safe data:

```text
/
/health
/status
/api/status
/about
/method
/search?q=
/api/search?q=
/record/{id}
```

No public route may expose Workbench, review, promotion, mutation, live metadata
fanout, downloads, uploads, install/emulation behavior, or private/local state.

## Rate Limits

Rate limiting is required at the public edge, tunnel provider, or reverse proxy
before public exposure.

Initial recommended limits:

```text
60 requests/minute/IP
20 search requests/minute/IP
20 burst requests/10 seconds/IP
```

These are alpha defaults. They may be tightened if the tunnel/proxy provider has
lower practical limits or if abuse appears.

## Logging

Allowed:

- minimal access logs needed to operate the alpha;
- aggregate health, request, error, and route counts;
- short-window operational logs or provider defaults until explicit retention is set.

Forbidden:

- raw query retention in committed artifacts;
- operator token logging;
- private path logging;
- private local state logging;
- raw provider credentials;
- raw source responses.

All public logs must be redacted before becoming committed evidence.

## Privacy

Public alpha does not require accounts and must not collect private local data.

Raw public queries must not become product truth automatically. If future demand
signals are collected, they must be minimized, redacted or aggregated, and routed
through a separate reviewed task.

A privacy notice is required before public exposure.

## Monitoring

Minimum launch monitoring:

```text
/health
/status
/api/status
/search?q=manual%20for%20Sound%20Blaster%20CT1740
/record/{id}
```

First monitoring window:

```text
72 hours
```

The alpha may be best-effort. It must not claim production uptime or SLA.

## Restart

Public alpha may use manual restart for the first launch window. A process
supervisor is required before any production-readiness claim.

Restart instructions must name the local server command, selected exposure
command, and the order for stopping and starting each process once the exposure
method is selected.

## Rollback

Rollback for public alpha means:

```text
disable public edge or tunnel
stop local public-alpha server
return to loopback-only
rerun health/status locally
record rollback result
```

Because public alpha is read-only, rollback must not need data mutation. If any
future task adds mutation, that task must provide a separate mutation rollback
plan before launch.

## Report Or Takedown Channel

A public report/takedown channel is required before public exposure. The
operator must select the channel in a future exposure or approval task.

Until that channel is selected, launch remains blocked.

## Gate Integration

The active policy is:

```text
control/policies/public_alpha_ops_posture_policy.json
```

The decision inventory is:

```text
control/inventory/public_alpha_ops_posture_00.json
```

Current gate effect:

```text
ops posture defined
public exposure still blocked
launch approval still missing
```

The existing local-machine exposure planner currently reports missing ops
posture unless its exposure report is produced by a future authorized task that
can consume or mirror these decisions. Do not hand-edit generated `.eureka`
reports to bypass that gate.

## Next Task

The next launch-track task is:

```text
LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00
```

That task should select the public exposure method and report/takedown channel,
then decide what code or operator wiring is needed for the exposure planner to
mark the ops posture as configured or validated.

## Non-Claims

This posture does not claim public launch readiness, production readiness,
release promotion, full-discovery completion, public URL availability, TLS
readiness, rights clearance, binary safety, download safety, or malware safety.

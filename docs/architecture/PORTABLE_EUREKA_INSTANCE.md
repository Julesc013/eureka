# Portable Eureka Instance

`PORTABLE-EUREKA-INSTANCE-00` defines the local source-checkout portability layer for Eureka Local Reference System v0.

It is intentionally a composition layer:

```text
scripts/eureka.py
-> runtime/local/portable_instance.py
-> existing local instance, runner, Preview Index, exploration, oracle, replay, and service router modules
```

It does not introduce a second runner, Preview Index, route registry, oracle, review system, or local instance format.

## Instance Model

Instance root resolution order:

1. `--instance <path>`
2. `EUREKA_INSTANCE`
3. repo-adjacent `../instances/default`

The instance root is resolved to an absolute local path. Repo roots, product roots, hidden/private roots, and home-root state are rejected. The portable profile is written to:

```text
<instance>/config/portable_instance.json
```

The profile records local-private paths relative to the instance where practical:

```text
run/e2e-reference/runs/
db/e2e-reference/preview-index/
run/e2e-reference/eval/
run/e2e-reference/portable-instance/
logs/eureka-portable.log
tmp/e2e-reference/
exports/backups/
```

No credential or operator token is stored in the profile.

## Command Ownership

`scripts/eureka.py` is a thin stable entrypoint. The portable module performs instance resolution, path mapping, status aggregation, and command composition. Substantive behavior remains in:

- `tools/generators/eureka_init_instance.py`
- `tools/generators/eureka_validate_instance.py`
- `tools/generators/eureka_instance_status.py`
- `runtime/resolution_run/**`
- `runtime/index/preview/**`
- `runtime/local/e2e_hunt_exploration.py`
- `runtime/local/service/**`
- `evals/e2e_reference/oracle/**`

## Server Boundary

`serve --mode exploration` uses the canonical local service router and exposes `/explore` plus `/api/v1/explore` on loopback only. It rejects non-loopback binds, does not enable LAN mode, does not enable public alpha, and does not enable live providers.

Operator tokens are accepted from `--operator-token` or `EUREKA_OPERATOR_TOKEN`; otherwise one is generated for the current process. Tokens are not written to the profile, status, server-state file, or logs.

## Degraded Modes

Portable v0 reports degraded states rather than repairing silently:

- missing instance: `bootstrap_required`
- invalid instance: `instance_validation_failed`
- migration needed: reported, not migrated
- missing Preview Index: `/explore` stays available with an empty/degraded state
- invalid Preview Index: not searched or activated
- corrupt run bundle: listed as corrupt
- invalid oracle registry: `test` is blocked
- port conflict or live/public mode: fail closed

## Non-Claims

Portable v0 means:

```text
Python source checkout + supported Python runtime + explicit local instance
```

It does not claim packaged binary portability, production readiness, public launch readiness, reviewed IA truth, downloads, execution, or cloud sync.

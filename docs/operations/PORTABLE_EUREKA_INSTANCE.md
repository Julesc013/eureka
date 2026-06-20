# Portable Eureka Instance Operations

Portable Eureka gives the local reference system one entrypoint over existing commands:

```powershell
python scripts/eureka.py bootstrap
python scripts/eureka.py doctor
python scripts/eureka.py test
python scripts/eureka.py hunt "old blue FTP client for XP"
python scripts/eureka.py serve --mode exploration
```

Use an explicit local instance whenever possible:

```powershell
python scripts/eureka.py --instance ../instances/default bootstrap
```

Instance resolution order is `--instance`, then `EUREKA_INSTANCE`, then `../instances/default`.

## Bootstrap

```powershell
python scripts/eureka.py --instance ../instances/default bootstrap --json
```

Bootstrap initializes the existing local instance layout, writes `config/portable_instance.json`, creates E2E local roots, generates one synthetic run bundle unless `--no-demo` is supplied, builds an activated Preview Index generation, and writes portable status. It does not start a server, call providers, create reviewed truth, or mutate public indexes.

Use `--dry-run` to write nothing.

## Doctor

```powershell
python scripts/eureka.py --instance ../instances/default doctor --strict --json
```

Doctor is read-only. It checks the local instance, portable profile, Preview Index pointer, oracle registry, exploration route registration, stale server locks, backup path, and disk-space warning posture.

## Test

```powershell
python scripts/eureka.py --instance ../instances/default test --suite core --json
```

`test` delegates to the autonomous E2E oracle and writes results under:

```text
<instance>/run/e2e-reference/eval/
```

It is a local product smoke/eval command. It is not full unittest discovery and does not claim production or public-launch readiness.

## Hunt

```powershell
python scripts/eureka.py --instance ../instances/default hunt "old blue FTP client for XP" --json
```

Portable v0 supports synthetic Hunts only. It searches the current Preview Index for immediate context, creates a durable run bundle through the shared runner, and returns a replay command.

Live provider modes fail closed.

## Replay

```powershell
python scripts/eureka.py --instance ../instances/default replay <run-id> --strict --json
```

Replay validates a direct child run bundle, verifies hashes and event chain, writes only the runner replay report, and performs no provider, review, or index mutation.

## Serve

```powershell
python scripts/eureka.py --instance ../instances/default serve --mode exploration
```

Startup output includes:

```text
Eureka local exploration:
http://127.0.0.1:8765/explore
```

Only loopback hosts are allowed. Public alpha, LAN mode, live providers, downloads, and execution remain disabled. Use smoke mode for a bounded local check:

```powershell
python scripts/eureka.py --instance ../instances/default serve --mode exploration --host 127.0.0.1 --port 0 --smoke --json
```

## Status

```powershell
python scripts/eureka.py --instance ../instances/default status --json
```

Status is read-only. It aggregates instance schema, store posture, Preview Index generation, run bundles, latest oracle result, server state, backup posture, provider/public posture, and next command.

## Troubleshooting

- `bootstrap_required`: run `bootstrap` with the same explicit instance path.
- `instance_validation_failed`: inspect `doctor --strict`; do not auto-repair stores.
- `preview_index_absent`: rerun `bootstrap` or a future Preview Index build command.
- `server_already_running`: use the existing loopback URL or stop the process.
- `live_mode_forbidden`: portable v0 is synthetic-only.

Generated local state remains under the explicit instance root and is not committed.

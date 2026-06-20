# Portable Eureka Backup And Recovery

Portable v0 does not implement upload, sync, or cloud backup. Backup posture is an explicit local filesystem copy.

## Authoritative Instance State

Treat these instance directories as authoritative local state:

```text
config/
db/
run/
logs/
exports/
imports/
```

Generated or rebuildable roots include:

```text
tmp/
run/e2e-reference/eval/
db/e2e-reference/preview-index/
```

Run bundles under `run/e2e-reference/runs/` are durable local evidence for replay and should be copied when preserving local exploration history.

## Backup Root

Portable status reports:

```text
<instance>/exports/backups/
```

This is a conventional local destination for manual backups. Nothing is uploaded automatically.

## Offline Copy Procedure

1. Stop the local server with `Ctrl+C`.
2. Confirm no stale server lock remains:

   ```powershell
   python scripts/eureka.py --instance <instance> doctor --strict --json
   ```

3. Copy the entire instance directory to offline storage.
4. Keep the copy private; it may contain local paths, logs, query history, run bundles, and private overlays in future versions.

## Restore Procedure

1. Restore the instance directory to a local path outside the Git repository.
2. Run:

   ```powershell
   python scripts/eureka.py --instance <restored-instance> doctor --strict --json
   ```

3. If the Preview Index is missing or invalid, rebuild through `bootstrap` or a future dedicated Preview Index command.
4. Validate important run bundles:

   ```powershell
   python scripts/eureka.py --instance <restored-instance> replay <run-id> --strict --json
   ```

5. Run the local oracle smoke:

   ```powershell
   python scripts/eureka.py --instance <restored-instance> test --suite core --json
   ```

## Temporary State

Temporary files under `tmp/` and old oracle result runs may be deleted when storage is constrained. Do not delete `config/`, primary `db/` stores, or run bundles you need for replay evidence.

## Public Output Rule

Never copy private instance state into public outputs. Do not publish:

- operator tokens;
- query history;
- private local paths;
- logs with local paths;
- raw local run bundles;
- private overlays;
- unreviewed candidate material labelled as truth.

Public exposure remains paused unless a separate launch gate explicitly changes that posture.

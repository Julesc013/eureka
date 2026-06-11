# Start Command

Run from the repository root outside the AI session:

```powershell
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/source_snapshot_full_discovery_rerun_08
```

The harness runs the underlying full discovery command:

```powershell
python -m unittest discover -s tests -t .
```

The AI-assisted session must not run full unittest discovery inline.

Check status with:

```powershell
python scripts/check_full_discovery.py --run-id source_snapshot_full_discovery_rerun_08 --json
```


# Start Command

Run this outside the AI session from the repository root:

```powershell
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/source_snapshot_full_discovery_rerun_05
```

Before running, confirm:

```powershell
git status --short --branch
git rev-parse HEAD
```

Expected head for this handoff:

```text
4f2b18863d7b5df2bf2f0b242f6aafa06933ae98
```

If the operator intentionally runs from a later continuation head, record that
head in the returned summary and treat this handoff head as stale provenance.

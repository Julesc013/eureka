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

Handoff base head:

```text
4f2b18863d7b5df2bf2f0b242f6aafa06933ae98
```

The external summary must match the operator's current checked-out `dev` HEAD
at run time. This handoff commit and any later explicit continuation commits
will naturally advance `HEAD`.

# Full Discovery Evidence

Current status: `WAITING_FOR_EXTERNAL_FULL_DISCOVERY`

Required command:

```powershell
python scripts/eureka_test_gate.py --gate promotion_gate --watch --clean
```

Alternative command:

```powershell
python scripts/run_full_unittest_discovery.py --out ../eureka-test-runs/dev_to_main_promotion_05
```

Return either the `ai_handoff.md` from the gate command or the compact summary,
failure families, failed tests, and `git status --short --branch`.

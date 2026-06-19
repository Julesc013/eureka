# Start Command

Run from the repo root outside the AI session:

```powershell
python scripts/run_full_unittest_discovery.py `
  --run-id source_foundry_preview_v0_post_historical_repair_02 `
  --out ../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02 `
  --quiet

python scripts/check_full_discovery.py `
  --run-id source_foundry_preview_v0_post_historical_repair_02 `
  --json
```

Do not reuse the previous run ID:

```text
source_foundry_preview_v0_checkpoint_00
```

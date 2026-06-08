# Files Changed

| Path | Change | Reason |
|---|---|---|
| `tools/reporters/summarize_unittest_log.py` | Modified | Require a unittest separator before parsing `FAIL:` / `ERROR:` as a unittest failure block. |
| `tests/scripts/test_summarize_unittest_log.py` | Modified | Add regression coverage for plain validator output containing `ERROR: refusing forbidden output root`. |
| `.aide/queue/index.yaml` | Modified | Mark this repair complete and recommend `CONTRACT-SCHEMA-DRIFT-REPAIR-01`. |
| `.aide/context/latest-task-packet.md` | Modified | Refresh compact task handoff after repair. |
| `docs/planning/public_live_preimplementation/repair/generated_artifact_drift_repair_01/**` | Added | Required repair evidence package. |

## Files Deliberately Not Changed

- `site/dist/**`
- `snapshots/**`
- `contracts/**`
- `runtime/**`
- `release/**`

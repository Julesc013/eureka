# Validation and Repair Guide

Validator commands:

```powershell
python scripts/validate_external_baseline_observations.py
python scripts/validate_external_baseline_observations.py --json
python scripts/list_external_baseline_observations.py --batch batch_0
python scripts/run_external_baseline_comparison.py --batch batch_0 --json
python scripts/validate_external_baseline_comparison_report.py
python scripts/validate_manual_observation_batch_0_follow_up.py
```

Common failures and repairs:

| Failure | Repair |
|---|---|
| Missing `task_id`/`query_id` | Use a selected query id from `batch_manifest.json`. |
| Unknown `system_id` | Use one of the current systems: `google_web_search`, `internet_archive_metadata_search`, `internet_archive_full_text_search`. |
| Placeholder values in an observed record | Replace every placeholder with human-entered observation data before setting `observation_status` to `observed`. |
| Invalid enum value | Use the enum from `observation.schema.json`. |
| Pending record contains top results | Keep pending records empty, or finish the record and mark it observed with all required metadata. |
| Missing source or exact query | Enter the exact external source and exact query used by the human operator. |
| Overlong quote | Replace with paraphrase and a short bounded quote only if necessary. |
| Missing usefulness scores | Fill all score fields with integers from 0 to 3. |
| Invalid or private attachment reference | Remove it or replace with a repo-approved relative reference. |
| Pending observations remain | Comparison is not complete; run comparison only for status awareness or after valid observations exist. |

Rerun comparison only after validation passes:

```powershell
python scripts/run_external_baseline_comparison.py --batch batch_0 --json
```

If invalid records remain, repair them first. Do not delete evidence to make counts look better; preserve limitations and blockers honestly.

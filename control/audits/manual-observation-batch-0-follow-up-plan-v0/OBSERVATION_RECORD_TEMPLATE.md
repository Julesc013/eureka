# Observation Record Template

The JSON below is a placeholder template. Placeholders are invalid until replaced by a human manual observation.

```json
{
  "observation_id": "manual_entry::batch_0::batch_0_task_id_here::external_source_here",
  "query_id": "batch_0_task_id_here",
  "query_text": "replace_with_task_query_text",
  "system_id": "google_web_search|internet_archive_metadata_search|internet_archive_full_text_search",
  "observation_status": "pending_manual_observation",
  "operator": "replace_with_human_operator",
  "observed_at": "YYYY-MM-DDTHH:MM:SS local timezone or UTC",
  "browser_or_tool": "manual browser name and version if appropriate",
  "location_context_optional": "omit private account, IP, session, or location details",
  "exact_query_submitted": "replace_with_actual_query",
  "filters_or_scope": "replace_with_visible_filters_or_scope",
  "result_count_visible_optional": null,
  "collection_method": "manual",
  "top_results": [],
  "first_useful_result_rank": null,
  "first_useful_result_reason": "replace_after_manual_observation",
  "usefulness_scores": {
    "object_type_fit": 0,
    "smallest_actionable_unit": 0,
    "evidence_quality": 0,
    "compatibility_clarity": 0,
    "actionability": 0,
    "absence_explanation": 0,
    "duplicate_handling": 0,
    "user_cost_reduction": 0,
    "overall": 0
  },
  "failure_modes": [
    "replace_after_manual_observation"
  ],
  "comparison_notes": [
    "Replace placeholders after manual observation."
  ],
  "next_eureka_work": [],
  "evidence_limitations": [
    "Replace placeholders after manual observation."
  ],
  "staleness_notes": [
    "External results are time-sensitive and may vary by operator/browser/location."
  ],
  "created_by": "manual_observation_batch_0_human_operator",
  "schema_version": "manual_external_baseline_observation.v0"
}
```

For a fillable pending record, prefer:

```powershell
python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout
```

The helper creates a pending record only. A human must replace pending fields before changing `observation_status` to `observed`.

Task-brief field mapping:

- `observed_result_quality` is a worksheet label, not a current schema field. Record it through `first_useful_result_rank`, `first_useful_result_reason`, `failure_modes`, `comparison_notes`, and `usefulness_scores`.
- `observed_results` maps to the current schema field `top_results`.

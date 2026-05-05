# Manual Observation Batch 0 Follow-up

Manual Observation Batch 0 is the human-operated external baseline workflow for selected Search Usefulness queries. It is intentionally manual because it involves observing external search engines or archive/search sites and recording what a human saw.

Codex may inspect local files, produce worksheets and templates, and run local validators. Codex must not browse, scrape, call external APIs, perform external searches, fabricate observations, or mark pending records complete.

Current Batch 0 status:

- Batch: `batch_0`
- Selected queries: 13
- Selected systems: 3
- Observation slots: 39
- Valid observed records: 0
- Pending records: 39
- Invalid records: 0
- Readiness: `comparison_not_eligible`

## Execute Batch 0

1. Review `evals/search_usefulness/external_baselines/batches/batch_0/batch_manifest.json`.
2. List pending records:

   ```powershell
   python scripts/list_external_baseline_observations.py --batch batch_0 --status pending_manual_observation
   ```

3. For each pending task/source pair, perform the search manually in a browser.
4. Record exact query, source/site, observation date and timezone, visible scope/filters, top relevant results, usefulness scores, limitations, and staleness notes.
5. Keep quotes short and prefer paraphrase plus source reference.
6. Avoid private account/session/browser data and private local paths.
7. Do not record downloads, installs, source archive contents, credentials, or private URLs.
8. Validate records:

   ```powershell
   python scripts/validate_external_baseline_observations.py
   ```

9. Rerun comparison only after valid observations exist:

   ```powershell
   python scripts/run_external_baseline_comparison.py --batch batch_0 --json
   ```

## Fill Observation Records

Use the existing helper to create a pending record for editing:

```powershell
python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout
```

The helper performs no external calls. It creates a pending local JSON shape only. A human must replace placeholders and complete the record before setting it to `observed`.

## Screenshots and Quotes

Screenshots are optional unless a future schema requires them. Do not include private account, session, browser, or notification data. Crop or redact before committing. Screenshots are evidence of one observation, not truth.

Do not include long copyrighted excerpts. Prefer paraphrase. When a quote is necessary, keep it short and tied to the structured observation.

## Interpret Readiness

- `comparison_not_eligible`: no valid observations exist.
- `partial`: some valid observations exist but pending slots remain.
- `ready_for_comparison`: all required records are valid enough for comparison.
- `blocked`: invalid records or missing batch/schema files must be repaired first.

Batch 0 is currently `comparison_not_eligible`.

## Next Steps

Human/operator:

- Execute Manual Observation Batch 0.
- Validate observation records.
- Rerun external baseline comparison.
- Continue hosted deployment verification separately.

Codex:

- Maintain local validators, docs, and workflow artifacts.
- Do not perform the observations.


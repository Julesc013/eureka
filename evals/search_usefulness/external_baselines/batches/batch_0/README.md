# Manual Observation Batch 0

Manual Observation Batch 0 is the first prioritized set of pending external
baseline observation slots. It prepares human comparison work only.

This batch does not contain observed Google or Internet Archive results. It
does not perform searches, scrape external systems, call APIs, crawl, or
automate result collection. Every slot remains `pending_manual_observation`
until a human operator records evidence with the required metadata.

## Files

- `batch_manifest.json`: selected query IDs, systems, rationale, and expected
  slot count.
- `pending_batch_0_observations.json`: compact pending query/system slots.
- `observation_template.batch_0.json`: fillable template for one manual
  observation.
- `observation_instructions.md`: step-by-step human procedure.
- `observation_checklist.md`: operator checklist before committing an observed
  record.
- `observations/`: reserved for future human-filled Batch 0 observations.
- `reports/`: reserved for future Batch 0 status or comparison reports.

## Entry Helpers

Manual Observation Entry Helper v0 supports this batch with local scripts:

```bash
python scripts/list_external_baseline_observations.py --batch batch_0
python scripts/report_external_baseline_status.py --batch batch_0 --next-pending
python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout
python scripts/validate_external_baseline_observations.py --file <path>
```

The create helper emits a fillable pending JSON record for a human to edit. It
does not submit searches, fetch URLs, open a browser, copy results, or mark the
record observed. Observed status still requires explicit human-entered
metadata, manually recorded top results, scores, limitations, and staleness
notes.

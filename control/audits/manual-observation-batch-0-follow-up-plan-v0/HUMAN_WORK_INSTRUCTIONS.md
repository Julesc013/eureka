# Human Work Instructions

Status classification: `ready_for_human_operation`

1. Open `evals/search_usefulness/external_baselines/batches/batch_0/batch_manifest.json`.
2. For each pending task, perform the external search manually in a browser.
3. Record the exact query used.
4. Record the external source/site used.
5. Record the observation date and local timezone.
6. Record top relevant result summaries.
7. Record whether an exact artifact, partial result, near miss, or no useful result was found.
8. Record source URLs or stable identifiers if allowed by the schema and safe to commit.
9. Attach screenshot or evidence only according to `SCREENSHOT_AND_EVIDENCE_ATTACHMENT_POLICY.md`.
10. Avoid long copyrighted quotes.
11. Run `python scripts/validate_external_baseline_observations.py`.
12. Rerun `python scripts/run_external_baseline_comparison.py --batch batch_0 --json` after valid observations exist.

Recommended local helper flow:

```powershell
python scripts/list_external_baseline_observations.py --batch batch_0 --status pending_manual_observation
python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout
python scripts/validate_external_baseline_observations.py
python scripts/run_external_baseline_comparison.py --batch batch_0 --json
```

Before any comparison refresh, run the validator and repair all reported errors.

Do not mark a record `observed` until a human has entered actual observed fields, top results, scores, limitations, and staleness notes.

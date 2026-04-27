# Search Usefulness Audit Delta v1

Search Usefulness Audit Delta v1 records the measured movement after
Old-Platform Source Coverage Expansion v0.

This is an audit/reporting pack only. It does not change retrieval behavior,
add source connectors, call live sources, crawl, scrape external systems,
ingest arbitrary local files, add fuzzy/vector/LLM retrieval, add Rust behavior,
or change external-baseline policy.

## Files

| File | Purpose |
| --- | --- |
| `BASELINE.md` | Baseline source and limitations. |
| `CURRENT_RESULTS.md` | Current Search Usefulness Audit and archive eval summaries. |
| `DELTA_SUMMARY.md` | Aggregate status-count movement and conclusion. |
| `WEDGE_DELTA.md` | Old-platform and member-discovery wedge movement. |
| `ARCHIVE_EVAL_DELTA.md` | Archive-resolution hard eval movement and remaining failures. |
| `FAILURE_MODE_DELTA.md` | Failure-mode count comparison. |
| `QUERY_MOVEMENT.md` | Query movement, current gaps, and hard-test candidates. |
| `NEXT_RECOMMENDATIONS.md` | Recommended next milestone and alternatives. |
| `delta_report.json` | Machine-readable compact delta report. |

## Report Shape

`delta_report.json` reuses the v0 compact delta shape and adds archive-eval
fields:

- `report_id`
- `created_by_slice`
- `baseline`
- `current`
- `delta`
- `selected_wedges`
- `conclusions`
- `recommended_next_milestone`
- `alternatives_considered`
- `do_not_do`
- `limitations`

The search-usefulness baseline is machine-derived from
`control/audits/search-usefulness-delta-v0/delta_report.json`. Archive-eval
baseline counts are historical/reported because v0 did not commit
machine-readable archive-eval counts.

## Baseline Policy

The baseline is not external baseline data. It is not Google, Internet Archive,
or other external search observation data. External baselines remain
`pending_manual_observation` unless a human operator records reviewed
observation files under the governed search-usefulness observation path.

## Reproduce Current Results

Run:

```bash
python scripts/run_search_usefulness_audit.py --json
python scripts/run_archive_resolution_evals.py --json
```

The committed pack uses normalized summary values from those commands rather
than committing volatile local run dumps.

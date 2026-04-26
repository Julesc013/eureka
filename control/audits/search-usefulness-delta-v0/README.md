# Search Usefulness Audit Delta v0

Search Usefulness Audit Delta v0 records the usefulness movement after the
recent old-platform/member-discovery implementation sequence:

- Source Coverage and Capability Model v0
- Real Source Coverage Pack v0
- Old-Platform Software Planner Pack v0
- Member-Level Synthetic Records v0
- Result Lanes + User-Cost Ranking v0
- Compatibility Evidence Pack v0

This is an audit/reporting pack only. It does not change retrieval behavior,
add source connectors, add live source probing, add crawling, add fuzzy/vector
retrieval, add LLM behavior, or change external-baseline policy.

## Files

| File | Purpose |
| --- | --- |
| `BASELINE.md` | Historical reported baseline used for the delta. |
| `CURRENT_RESULTS.md` | Current Search Usefulness Audit output summary. |
| `DELTA_SUMMARY.md` | Aggregate before/after movement and conclusion. |
| `WEDGE_DELTA.md` | Old-platform and member-discovery wedge analysis. |
| `FAILURE_MODE_DELTA.md` | Failure-mode counts and baseline limitations. |
| `QUERY_MOVEMENT.md` | Query-family movement and inferred per-query notes. |
| `NEXT_RECOMMENDATIONS.md` | Recommended next milestone and alternatives. |
| `delta_report.json` | Machine-readable compact delta report. |

## Report Shape

`delta_report.json` is intentionally compact and JSON-compatible:

- `report_id`
- `created_by_slice`
- `baseline`
- `current`
- `delta`
- `selected_wedges`
- `conclusions`
- `recommended_next_milestone`
- `do_not_do`
- `limitations`

The baseline in this pack is a historical reported baseline because no
committed machine-derived per-query before snapshot existed. Future delta packs
should prefer machine-derived reports from committed `--json` outputs.

## Baseline Policy

The baseline is not external baseline data. It is not Google, Internet Archive,
or other external search observation data. External baselines remain
`pending_manual_observation` unless a human operator records reviewed
observation files under the governed search-usefulness observation path.

## Reproduce Current Results

Run:

```bash
python scripts/run_search_usefulness_audit.py --json
```

The committed pack uses normalized summary values from that command rather than
committing a volatile local run dump.

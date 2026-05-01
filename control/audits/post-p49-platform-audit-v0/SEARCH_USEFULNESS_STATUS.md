# Search Usefulness Status

| Area | Evidence | Classification | Notes |
|---|---|---|---|
| Archive resolution evals | `run_archive_resolution_evals.py` | `implemented_runtime` | 6 tasks, `satisfied=6`. |
| Search usefulness audit | `run_search_usefulness_audit.py` | `implemented_runtime` | 64 queries. |
| Source expansion v2 | `source_expansion_v2_report.json` | `fixture_only` | Six recorded-fixture source families added. |
| Search usefulness delta v2 | `delta_report.json` | `planning_only` | Audit-only measurement, no behavior added. |
| External baseline comparison | baseline status report | `manual_pending` | Not eligible: 0 observed external baseline slots. |

Current counts from Search Usefulness Delta v2:

| Status | Count |
|---|---:|
| covered | 5 |
| partial | 40 |
| source_gap | 10 |
| capability_gap | 7 |
| unknown | 2 |
| total | 64 |

Remaining named source gaps include article scans, old drivers, retro magazine
content, dead vendor pages, DOS/Mac utilities, and specific legacy driver
queries. Current claims are fixture-bounded.

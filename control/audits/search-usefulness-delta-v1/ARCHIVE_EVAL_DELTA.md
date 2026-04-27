# Archive Eval Delta

Current archive-resolution eval status counts:

| Status | Count |
| --- | ---: |
| capability_gap | 1 |
| not_satisfied | 5 |

The prior reported archive baseline was:

| Status | Count |
| --- | ---: |
| capability_gap | 5 |
| not_satisfied | 1 |

## Why `not_satisfied` Is Progress

`not_satisfied` is not success. It means the hard eval runner found bounded
local results, but those results did not satisfy the exact expected-result
checks.

The movement is useful because it shows:

- source/planner/evidence now exists for more hard tasks
- the local index returns candidates for old-platform software queries
- result lanes, member records, and compatibility evidence are visible
- hard expected-result checks still prevent fake wins

## Current Hard Task Outcomes

| Task | Current status | Interpretation |
| --- | --- | --- |
| `article_inside_magazine_scan` | capability_gap | Still lacks article/page/OCR source coverage. |
| `driver_inside_support_cd` | not_satisfied | Source/member evidence exists, but hard expected-result matching still fails. |
| `latest_firefox_before_xp_drop` | not_satisfied | Source evidence exists, but exact latest-compatible answer is not established. |
| `old_blue_ftp_client_xp` | not_satisfied | Candidate evidence exists, but identity remains unresolved. |
| `win98_registry_repair` | not_satisfied | Source-backed registry-repair evidence exists, but hard result expectations are not satisfied. |
| `windows_7_apps` | not_satisfied | Windows 7 utility evidence exists, but direct best-answer expectations are not satisfied. |

## Next Implication

The next milestone should focus on satisfying hard eval expectations where
source-backed candidates now exist. That likely requires tighter expected-result
hint alignment, result-lane/user-cost refinement, member target selection, and
compatibility evidence surfacing. It should not weaken hard evals.

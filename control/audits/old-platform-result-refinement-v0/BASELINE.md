# Baseline

Baseline source: Hard Eval Satisfaction Pack v0 and the live
`python scripts/run_archive_resolution_evals.py --json` output before this
refinement.

Baseline aggregate:

| Status | Count |
| --- | ---: |
| capability_gap | 1 |
| partial | 5 |

Baseline targeted partial tasks:

- `driver_inside_support_cd`
- `latest_firefox_before_xp_drop`
- `old_blue_ftp_client_xp`
- `win98_registry_repair`
- `windows_7_apps`

Baseline capability gap:

- `article_inside_magazine_scan`

The baseline already had source-backed candidates for the five old-platform
tasks. It did not yet score result-shape, lane, or bad-result checks.
External Google and Internet Archive baselines remain pending/manual and are
not part of this pack.

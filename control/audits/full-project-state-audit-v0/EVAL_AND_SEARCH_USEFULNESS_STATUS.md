# Eval and Search Usefulness Status

Archive Resolution Eval:

- Command: `python scripts/run_archive_resolution_evals.py`
- Status: passed
- Task count: 6
- Status counts: satisfied=6
- Satisfied tasks: `article_inside_magazine_scan`, `driver_inside_support_cd`, `latest_firefox_before_xp_drop`, `old_blue_ftp_client_xp`, `win98_registry_repair`, `windows_7_apps`
- Hard eval weakening observed: none

Search Usefulness Audit:

- Command: `python scripts/run_search_usefulness_audit.py`
- Status: passed
- Query count: 64
- Eureka status counts: capability_gap=9, covered=5, partial=22, source_gap=26, unknown=2
- External pending counts: Google=64, Internet Archive full text=64, Internet Archive metadata=64
- Top failure modes: source_coverage_gap=49, compatibility_evidence_gap=25, planner_gap=24, query_interpretation_gap=21, representation_gap=14, decomposition_gap=12, member_access_gap=12, live_source_gap=10, ranking_gap=8

Interpretation:

- The hard archive evals are currently satisfied by local fixture-backed behavior.
- Broader search usefulness still has substantial source coverage and compatibility evidence gaps.
- External baseline comparison is not eligible until human observations exist.

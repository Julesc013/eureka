# Old-Platform Result Refinement Pack v0

This audit pack records the result-shape refinement after Hard Eval
Satisfaction Pack v0. It is an eval/reporting slice for the old-platform
software and member-discovery wedges.

The pack adds deterministic checks for:

- primary candidate shape
- expected result lanes
- bad-result pattern avoidance
- member-vs-parent granularity
- source-backed evidence visibility

It does not weaken hard evals, remove tasks, add live sources, add scraping,
add fuzzy/vector/LLM retrieval, add new connectors, or change public hosting
posture. External baselines remain pending/manual.

Current result:

- `driver_inside_support_cd` is now `satisfied`.
- `latest_firefox_before_xp_drop`, `old_blue_ftp_client_xp`,
  `win98_registry_repair`, and `windows_7_apps` remain `partial`.
- `article_inside_magazine_scan` remains `capability_gap`.

The JSON report shape is:

- `report_id`
- `created_by_slice`
- `baseline`
- `current`
- `targeted_tasks`
- `tasks_improved_to_satisfied`
- `tasks_remaining_partial`
- `tasks_still_capability_gap`
- `result_shape_checks_added`
- `bad_result_checks_added`
- `task_findings`
- `recommended_next_milestone`
- `alternatives_considered`
- `do_not_do`
- `limitations`

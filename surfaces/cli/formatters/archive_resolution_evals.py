from __future__ import annotations

from typing import Any, Mapping


def format_archive_resolution_evals(view_model: Mapping[str, Any]) -> str:
    suite = view_model.get("eval_suite")
    if not isinstance(suite, Mapping):
        return "Archive resolution evals\nstatus: blocked\n"

    lines = [
        "Archive resolution evals",
        f"status: {view_model.get('status', '(unknown)')}",
        f"created_by_slice: {suite.get('created_by_slice', '(unknown)')}",
        f"task_count: {suite.get('total_task_count', 0)}",
        f"status_counts: {_mapping_text(suite.get('status_counts'))}",
    ]

    tasks = suite.get("task_summaries")
    if isinstance(tasks, list) and tasks:
        lines.extend(["", "Tasks"])
        for task in tasks:
            if not isinstance(task, Mapping):
                continue
            lines.append(
                "- "
                f"{task.get('task_id', '(unknown)')}: {task.get('overall_status', '(unknown)')} "
                f"(planner={task.get('planner_status', '(unknown)')}, "
                f"search={task.get('search_mode', '(unknown)')}, "
                f"results={task.get('search_observed_result_count', 0)})"
            )

    full_tasks = suite.get("tasks")
    capability_gap_lines = _capability_gap_lines(full_tasks)
    if capability_gap_lines:
        lines.extend(["", "Capability gaps"])
        lines.extend(capability_gap_lines)

    notices = view_model.get("notices") or suite.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        for notice in notices:
            if not isinstance(notice, Mapping):
                continue
            line = f"- {notice.get('severity', '(unknown)')} {notice.get('code', '(unknown)')}"
            message = notice.get("message")
            if isinstance(message, str) and message:
                line += f": {message}"
            lines.append(line)
    return "\n".join(lines) + "\n"


def _capability_gap_lines(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    lines: list[str] = []
    for task in value:
        if not isinstance(task, Mapping):
            continue
        gaps = task.get("capability_gaps")
        if not isinstance(gaps, list) or not gaps:
            continue
        first_gap = gaps[0]
        if not isinstance(first_gap, Mapping):
            continue
        lines.append(
            f"- {task.get('task_id', '(unknown)')}: {first_gap.get('message', '(no message)')}"
        )
    return lines


def _mapping_text(value: Any) -> str:
    if not isinstance(value, Mapping) or not value:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in sorted(value.items()))

from __future__ import annotations

from typing import Any, Mapping


def format_local_tasks(local_tasks: Mapping[str, Any]) -> str:
    lines = [
        "Local tasks",
        f"status: {local_tasks.get('status', '(unknown)')}",
        f"task_count: {local_tasks.get('task_count', 0)}",
    ]
    selected_task_id = local_tasks.get("selected_task_id")
    if isinstance(selected_task_id, str) and selected_task_id:
        lines.append(f"selected_task_id: {selected_task_id}")

    tasks = local_tasks.get("tasks", [])
    if isinstance(tasks, list) and tasks:
        if len(tasks) == 1 and isinstance(selected_task_id, str) and selected_task_id:
            lines.extend(["", "Task"])
            lines.extend(_format_task_detail(tasks[0]))
        else:
            lines.extend(["", "Tasks"])
            for index, task in enumerate(tasks, start=1):
                if not isinstance(task, Mapping):
                    continue
                lines.append(f"{index}. {task.get('task_id', '(unknown)')}")
                lines.append(f"   task_kind: {task.get('task_kind', '(unknown)')}")
                lines.append(f"   status: {task.get('status', '(unknown)')}")
                result_summary = task.get("result_summary")
                error_summary = task.get("error_summary")
                if isinstance(result_summary, Mapping):
                    lines.append(f"   result_summary: {_mapping_text(result_summary)}")
                elif isinstance(error_summary, Mapping):
                    lines.append(f"   error_summary: {_mapping_text(error_summary)}")

    notices = local_tasks.get("notices")
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


def _format_task_detail(task: Mapping[str, Any]) -> list[str]:
    lines = [
        f"task_id: {task.get('task_id', '(unknown)')}",
        f"task_kind: {task.get('task_kind', '(unknown)')}",
        f"status: {task.get('status', '(unknown)')}",
        f"created_at: {task.get('created_at', '(unknown)')}",
        f"started_at: {task.get('started_at', '(none)')}",
        f"completed_at: {task.get('completed_at', '(none)')}",
        f"requested_inputs: {_mapping_text(task.get('requested_inputs'))}",
        f"created_by_slice: {task.get('created_by_slice', '(unknown)')}",
    ]
    result_summary = task.get("result_summary")
    if isinstance(result_summary, Mapping):
        lines.extend(["", "Result summary", _mapping_text(result_summary)])
    error_summary = task.get("error_summary")
    if isinstance(error_summary, Mapping):
        lines.extend(["", "Error summary", _mapping_text(error_summary)])
    output_references = task.get("output_references")
    if isinstance(output_references, Mapping):
        lines.extend(["", "Output references", _mapping_text(output_references)])
    notices = task.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Task notices"])
        for notice in notices:
            if not isinstance(notice, Mapping):
                continue
            line = f"- {notice.get('severity', '(unknown)')} {notice.get('code', '(unknown)')}"
            message = notice.get("message")
            if isinstance(message, str) and message:
                line += f": {message}"
            lines.append(line)
    return lines


def _mapping_text(value: Any) -> str:
    if not isinstance(value, Mapping) or not value:
        return "(none)"
    parts: list[str] = []
    for key, item in value.items():
        if isinstance(item, Mapping):
            nested = ", ".join(f"{nested_key}={nested_value}" for nested_key, nested_value in item.items())
            parts.append(f"{key}({nested})")
        elif isinstance(item, list):
            parts.append(f"{key}=[{', '.join(str(member) for member in item)}]")
        else:
            parts.append(f"{key}={item}")
    return "; ".join(parts) if parts else "(none)"

from __future__ import annotations

from typing import Any, Mapping


def format_query_plan(query_plan: Mapping[str, Any]) -> str:
    lines = [
        "Query plan",
        f"status: {query_plan.get('status', '(unknown)')}",
    ]
    plan = query_plan.get("query_plan")
    if isinstance(plan, Mapping):
        lines.extend(
            [
                "",
                "Plan",
                f"raw_query: {plan.get('raw_query', '(unknown)')}",
                f"task_kind: {plan.get('task_kind', '(unknown)')}",
                f"object_type: {plan.get('object_type', '(unknown)')}",
                f"planner_confidence: {plan.get('planner_confidence', '(unknown)')}",
                f"constraints: {_mapping_text(plan.get('constraints'))}",
                f"prefer: {_list_text(plan.get('prefer'))}",
                f"exclude: {_list_text(plan.get('exclude'))}",
                f"action_hints: {_list_text(plan.get('action_hints'))}",
                f"source_hints: {_list_text(plan.get('source_hints'))}",
                f"planner_notes: {_list_text(plan.get('planner_notes'))}",
            ]
        )
    notices = query_plan.get("notices")
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


def _mapping_text(value: Any) -> str:
    if not isinstance(value, Mapping) or not value:
        return "(none)"
    parts: list[str] = []
    for key, item in value.items():
        if isinstance(item, Mapping):
            nested = ", ".join(f"{nested_key}={nested_value}" for nested_key, nested_value in item.items())
            parts.append(f"{key}({nested})")
        else:
            parts.append(f"{key}={item}")
    return "; ".join(parts)


def _list_text(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "(none)"
    return ", ".join(str(item) for item in value)

from __future__ import annotations

from typing import Any, Mapping


def format_resolution_memory(resolution_memory: Mapping[str, Any]) -> str:
    lines = [
        "Resolution memory",
        f"status: {resolution_memory.get('status', '(unknown)')}",
        f"memory_count: {resolution_memory.get('memory_count', 0)}",
    ]
    selected_memory_id = resolution_memory.get("selected_memory_id")
    if isinstance(selected_memory_id, str) and selected_memory_id:
        lines.append(f"selected_memory_id: {selected_memory_id}")

    memories = resolution_memory.get("memories", [])
    if isinstance(memories, list) and memories:
        if len(memories) == 1 and isinstance(selected_memory_id, str) and selected_memory_id:
            lines.extend(["", "Memory"])
            lines.extend(_format_memory_detail(memories[0]))
        else:
            lines.extend(["", "Memories"])
            for index, memory in enumerate(memories, start=1):
                if not isinstance(memory, Mapping):
                    continue
                lines.append(f"{index}. {memory.get('memory_id', '(unknown)')}")
                lines.append(f"   memory_kind: {memory.get('memory_kind', '(unknown)')}")
                lines.append(f"   source_run_id: {memory.get('source_run_id', '(unknown)')}")
                lines.append(f"   checked_sources: {_checked_source_text(memory.get('checked_sources'))}")
                result_summaries = memory.get("result_summaries")
                absence_report = memory.get("absence_report")
                if isinstance(result_summaries, list) and result_summaries:
                    lines.append(f"   result_summaries: {len(result_summaries)} item(s)")
                elif isinstance(absence_report, Mapping):
                    lines.append(
                        f"   absence: {absence_report.get('likely_reason_code', '(unknown)')}"
                    )

    notices = resolution_memory.get("notices")
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


def _format_memory_detail(memory: Mapping[str, Any]) -> list[str]:
    lines = [
        f"memory_id: {memory.get('memory_id', '(unknown)')}",
        f"memory_kind: {memory.get('memory_kind', '(unknown)')}",
        f"source_run_id: {memory.get('source_run_id', '(unknown)')}",
        f"created_at: {memory.get('created_at', '(unknown)')}",
        f"raw_query: {memory.get('raw_query', '(none)')}",
        f"task_kind: {memory.get('task_kind', '(none)')}",
        f"requested_value: {memory.get('requested_value', '(none)')}",
        f"checked_source_ids: {_comma_text(memory.get('checked_source_ids'))}",
        f"checked_source_families: {_comma_text(memory.get('checked_source_families'))}",
        f"checked_sources: {_checked_source_text(memory.get('checked_sources'))}",
        f"useful_source_ids: {_comma_text(memory.get('useful_source_ids'))}",
        f"primary_resolved_resource_id: {memory.get('primary_resolved_resource_id', '(none)')}",
        f"created_by_slice: {memory.get('created_by_slice', '(unknown)')}",
    ]
    result_summaries = memory.get("result_summaries")
    if isinstance(result_summaries, list) and result_summaries:
        lines.extend(["", "Result summaries"])
        for index, item in enumerate(result_summaries, start=1):
            if not isinstance(item, Mapping):
                continue
            object_summary = item.get("object", {})
            label = "(unknown)"
            if isinstance(object_summary, Mapping):
                label = object_summary.get("label") or object_summary.get("id") or "(unknown)"
            lines.append(f"{index}. {label}")
            lines.append(f"   target_ref: {item.get('target_ref', '(unknown)')}")
            resolved_resource_id = item.get("resolved_resource_id")
            if isinstance(resolved_resource_id, str) and resolved_resource_id:
                lines.append(f"   resolved_resource_id: {resolved_resource_id}")
            source = item.get("source")
            if isinstance(source, Mapping):
                source_label = source.get("label") or source.get("source_id") or source.get("family")
                if isinstance(source_label, str) and source_label:
                    lines.append(f"   source: {source_label}")
    absence_report = memory.get("absence_report")
    if isinstance(absence_report, Mapping):
        lines.extend(
            [
                "",
                "Absence report",
                f"request_kind: {absence_report.get('request_kind', '(unknown)')}",
                f"likely_reason_code: {absence_report.get('likely_reason_code', '(unknown)')}",
                f"reason_message: {absence_report.get('reason_message', '(unknown)')}",
                f"checked_source_families: {_comma_text(absence_report.get('checked_source_families'))}",
            ]
        )
    evidence_summary = memory.get("evidence_summary")
    if isinstance(evidence_summary, list) and evidence_summary:
        lines.extend(["", "Evidence summary"])
        for index, evidence in enumerate(evidence_summary, start=1):
            if not isinstance(evidence, Mapping):
                continue
            lines.append(
                f"{index}. {evidence.get('claim_kind', '(unknown)')}={evidence.get('claim_value', '(unknown)')}"
            )
    invalidation_hints = memory.get("invalidation_hints")
    if isinstance(invalidation_hints, Mapping):
        lines.extend(["", "Invalidation hints", _mapping_text(invalidation_hints)])
    return lines


def _comma_text(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "(none)"
    return ", ".join(str(item) for item in value)


def _checked_source_text(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "(none)"
    labels: list[str] = []
    for entry in value:
        if not isinstance(entry, Mapping):
            continue
        name = entry.get("name") or entry.get("source_id") or "(unknown)"
        status = entry.get("status")
        if isinstance(status, str) and status:
            labels.append(f"{name} [{status}]")
        else:
            labels.append(str(name))
    return ", ".join(labels) if labels else "(none)"


def _mapping_text(value: Mapping[str, Any]) -> str:
    if not value:
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
    return "; ".join(parts)

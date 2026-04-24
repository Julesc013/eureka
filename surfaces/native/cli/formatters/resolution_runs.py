from __future__ import annotations

from typing import Any, Mapping


def format_resolution_runs(resolution_runs: Mapping[str, Any]) -> str:
    lines = [
        "Resolution runs",
        f"status: {resolution_runs.get('status', '(unknown)')}",
        f"run_count: {resolution_runs.get('run_count', 0)}",
    ]
    selected_run_id = resolution_runs.get("selected_run_id")
    if isinstance(selected_run_id, str) and selected_run_id:
        lines.append(f"selected_run_id: {selected_run_id}")

    runs = resolution_runs.get("runs", [])
    if isinstance(runs, list) and runs:
        if len(runs) == 1 and isinstance(selected_run_id, str) and selected_run_id:
            lines.extend(["", "Run"])
            lines.extend(_format_run_detail(runs[0]))
        else:
            lines.extend(["", "Runs"])
            for index, run in enumerate(runs, start=1):
                if not isinstance(run, Mapping):
                    continue
                result_summary = run.get("result_summary")
                absence_report = run.get("absence_report")
                lines.append(f"{index}. {run.get('run_id', '(unknown)')}")
                lines.append(f"   run_kind: {run.get('run_kind', '(unknown)')}")
                lines.append(f"   requested_value: {run.get('requested_value', '(unknown)')}")
                lines.append(f"   status: {run.get('status', '(unknown)')}")
                lines.append(f"   checked_sources: {_checked_source_text(run.get('checked_sources'))}")
                if isinstance(result_summary, Mapping):
                    lines.append(
                        f"   result_summary: {result_summary.get('result_count', 0)} result(s)"
                    )
                elif isinstance(absence_report, Mapping):
                    lines.append(
                        f"   absence: {absence_report.get('likely_reason_code', '(unknown)')}"
                    )

    notices = resolution_runs.get("notices")
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


def _format_run_detail(run: Mapping[str, Any]) -> list[str]:
    lines = [
        f"run_id: {run.get('run_id', '(unknown)')}",
        f"run_kind: {run.get('run_kind', '(unknown)')}",
        f"requested_value: {run.get('requested_value', '(unknown)')}",
        f"status: {run.get('status', '(unknown)')}",
        f"started_at: {run.get('started_at', '(unknown)')}",
        f"completed_at: {run.get('completed_at', '(unknown)')}",
        f"checked_source_ids: {_comma_text(run.get('checked_source_ids'))}",
        f"checked_source_families: {_comma_text(run.get('checked_source_families'))}",
        f"checked_sources: {_checked_source_text(run.get('checked_sources'))}",
        f"created_by_slice: {run.get('created_by_slice', '(unknown)')}",
    ]
    result_summary = run.get("result_summary")
    if isinstance(result_summary, Mapping):
        lines.extend(
            [
                "",
                "Result summary",
                f"result_kind: {result_summary.get('result_kind', '(unknown)')}",
                f"result_count: {result_summary.get('result_count', 0)}",
            ]
        )
        items = result_summary.get("items")
        if isinstance(items, list):
            lines.extend(["", "Results"])
            for index, item in enumerate(items, start=1):
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
    absence_report = run.get("absence_report")
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
    notices = run.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Run notices"])
        for notice in notices:
            if not isinstance(notice, Mapping):
                continue
            line = f"- {notice.get('severity', '(unknown)')} {notice.get('code', '(unknown)')}"
            message = notice.get("message")
            if isinstance(message, str) and message:
                line += f": {message}"
            lines.append(line)
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

from __future__ import annotations

from typing import Any, Mapping


def format_source_registry(source_registry: Mapping[str, Any]) -> str:
    lines = [
        "Source registry",
        f"status: {source_registry.get('status', '(unknown)')}",
        f"source_count: {source_registry.get('source_count', 0)}",
    ]
    applied_filters = source_registry.get("applied_filters")
    if isinstance(applied_filters, Mapping) and applied_filters:
        filter_text = ", ".join(f"{key}={value}" for key, value in applied_filters.items())
        lines.append(f"filters: {filter_text}")

    sources = source_registry.get("sources", [])
    selected_source_id = source_registry.get("selected_source_id")
    if isinstance(selected_source_id, str) and selected_source_id:
        lines.append(f"selected_source_id: {selected_source_id}")

    if isinstance(sources, list) and sources:
        if len(sources) == 1 and isinstance(selected_source_id, str) and selected_source_id:
            lines.extend(["", "Source"])
            lines.extend(_format_source_detail(sources[0]))
        else:
            lines.extend(["", "Sources"])
            for index, entry in enumerate(sources, start=1):
                if not isinstance(entry, Mapping):
                    continue
                lines.append(f"{index}. {entry.get('name', '(unknown)')}")
                lines.append(f"   source_id: {entry.get('source_id', '(unknown)')}")
                lines.append(f"   family: {entry.get('source_family', '(unknown)')}")
                lines.append(f"   status: {entry.get('status', '(unknown)')}")
                lines.append(f"   coverage: {entry.get('coverage_depth', '(unknown)')}")
                lines.append(f"   connector_mode: {entry.get('connector_mode', '(unknown)')}")
                lines.append(f"   trust_lane: {entry.get('trust_lane', '(unknown)')}")
                lines.append(f"   connector: {_connector_text(entry.get('connector'))}")
                lines.append(
                    f"   capabilities: {_comma_text(entry.get('capabilities_summary'))}"
                )
                lines.append(f"   roles: {_comma_text(entry.get('roles'))}")
                lines.append(f"   surfaces: {_comma_text(entry.get('surfaces'))}")
                lines.append(f"   summary: {entry.get('status_summary', '(unknown)')}")
                next_step = entry.get("next_coverage_step")
                if isinstance(next_step, str) and next_step:
                    lines.append(f"   next: {next_step}")
    notices = source_registry.get("notices")
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


def _format_source_detail(entry: Mapping[str, Any]) -> list[str]:
    lines = [
        f"name: {entry.get('name', '(unknown)')}",
        f"source_id: {entry.get('source_id', '(unknown)')}",
        f"family: {entry.get('source_family', '(unknown)')}",
        f"status: {entry.get('status', '(unknown)')}",
        f"summary: {entry.get('status_summary', '(unknown)')}",
        f"coverage_depth: {entry.get('coverage_depth', '(unknown)')}",
        f"coverage_status: {entry.get('coverage_status', '(unknown)')}",
        f"connector_mode: {entry.get('connector_mode', '(unknown)')}",
        f"capabilities: {_comma_text(entry.get('capabilities_summary'))}",
        f"indexed_scopes: {_comma_text(entry.get('indexed_scopes'))}",
        f"current_limitations: {_comma_text(entry.get('current_limitations'))}",
        f"next_coverage_step: {entry.get('next_coverage_step', '(unknown)')}",
        f"trust_lane: {entry.get('trust_lane', '(unknown)')}",
        f"authority_class: {entry.get('authority_class', '(unknown)')}",
        f"connector: {_connector_text(entry.get('connector'))}",
        f"roles: {_comma_text(entry.get('roles'))}",
        f"surfaces: {_comma_text(entry.get('surfaces'))}",
        f"object_types: {_comma_text(entry.get('object_types'))}",
        f"artifact_types: {_comma_text(entry.get('artifact_types'))}",
        f"identifier_types: {_comma_text(entry.get('identifier_types_emitted'))}",
        f"live_access_mode: {entry.get('live_access_mode', '(unknown)')}",
        f"extraction_mode: {entry.get('extraction_mode', '(unknown)')}",
        f"legal_posture: {entry.get('legal_posture', '(unknown)')}",
        f"freshness_model: {entry.get('freshness_model', '(unknown)')}",
        f"rights_notes: {entry.get('rights_notes', '(unknown)')}",
        f"notes: {entry.get('notes', '(unknown)')}",
    ]
    placeholder_warning = entry.get("placeholder_warning")
    if isinstance(placeholder_warning, str) and placeholder_warning:
        lines.append(f"placeholder_warning: {placeholder_warning}")
    return lines


def _comma_text(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "(none)"
    return ", ".join(str(item) for item in value)


def _connector_text(value: Any) -> str:
    if not isinstance(value, Mapping):
        return "(unknown)"
    label = value.get("label", "(unknown)")
    status = value.get("status", "(unknown)")
    return f"{label} [{status}]"

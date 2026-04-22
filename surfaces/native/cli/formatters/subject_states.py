from __future__ import annotations

from typing import Any, Mapping


def format_subject_states(subject_states: Mapping[str, Any]) -> str:
    lines = [
        "Subject states",
        f"status: {subject_states.get('status', '(unknown)')}",
        f"requested_subject_key: {subject_states.get('requested_subject_key', '(unknown)')}",
    ]

    subject = subject_states.get("subject")
    if isinstance(subject, Mapping):
        lines.extend(
            [
                "",
                "Subject",
                f"subject_key: {subject.get('subject_key', '(unknown)')}",
                f"subject_label: {subject.get('subject_label', '(unknown)')}",
                f"state_count: {subject.get('state_count', 0)}",
            ]
        )
        source_family_hint = subject.get("source_family_hint")
        if isinstance(source_family_hint, str) and source_family_hint:
            lines.append(f"source_family_hint: {source_family_hint}")

    states = subject_states.get("states")
    if isinstance(states, list) and states:
        lines.extend(["", "States"])
        for index, state in enumerate(states, start=1):
            if not isinstance(state, Mapping):
                continue
            object_summary = state.get("object", {})
            label = "(unknown)"
            if isinstance(object_summary, Mapping):
                label = object_summary.get("label") or object_summary.get("id") or label
            lines.append(f"{index}. {label}")
            lines.append(f"   target_ref: {state.get('target_ref', '(unknown)')}")
            lines.append(f"   resolved_resource_id: {state.get('resolved_resource_id', '(unknown)')}")
            version_or_state = state.get("version_or_state")
            if isinstance(version_or_state, str) and version_or_state:
                lines.append(f"   version_or_state: {version_or_state}")
            normalized_version_or_state = state.get("normalized_version_or_state")
            if isinstance(normalized_version_or_state, str) and normalized_version_or_state:
                lines.append(f"   normalized_version_or_state: {normalized_version_or_state}")
            source = state.get("source")
            if isinstance(source, Mapping):
                lines.append(f"   source_family: {source.get('family', '(unknown)')}")
                source_label = source.get("label")
                if isinstance(source_label, str) and source_label:
                    lines.append(f"   source_label: {source_label}")
                source_locator = source.get("locator")
                if isinstance(source_locator, str) and source_locator:
                    lines.append(f"   source_origin: {source_locator}")
            evidence = state.get("evidence")
            if isinstance(evidence, list) and evidence:
                lines.append(f"   evidence: {_compact_evidence_entry(evidence[0])}")

    notices = subject_states.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def _format_notice_lines(notices: list[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for notice in notices:
        code = notice.get("code", "(unknown)")
        severity = notice.get("severity", "(unknown)")
        message = notice.get("message")
        line = f"- {severity} {code}"
        if isinstance(message, str) and message:
            line += f": {message}"
        lines.append(line)
    return lines


def _compact_evidence_entry(entry: Any) -> str:
    if not isinstance(entry, Mapping):
        return "(unknown)"
    claim_kind = entry.get("claim_kind", "(unknown)")
    asserted_by = entry.get("asserted_by_label") or entry.get("asserted_by_family") or "(unknown)"
    return f"{claim_kind} via {asserted_by}"

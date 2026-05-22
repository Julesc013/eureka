from __future__ import annotations

from typing import Any, Mapping


def format_absence_report(absence_report: Mapping[str, Any]) -> str:
    lines = [
        "Absence report",
        f"request_kind: {absence_report.get('request_kind', '(unknown)')}",
        f"requested_value: {absence_report.get('requested_value', '(unknown)')}",
        f"status: {absence_report.get('status', '(unknown)')}",
        f"likely_reason_code: {absence_report.get('likely_reason_code', '(unknown)')}",
        f"reason_message: {absence_report.get('reason_message', '(unknown)')}",
        f"checked_record_count: {absence_report.get('checked_record_count', 0)}",
        f"checked_subject_count: {absence_report.get('checked_subject_count', 0)}",
    ]

    checked_source_families = absence_report.get("checked_source_families")
    if isinstance(checked_source_families, list) and checked_source_families:
        lines.append(f"checked_source_families: {', '.join(str(item) for item in checked_source_families)}")

    near_matches = absence_report.get("near_matches")
    lines.extend(["", "Near matches"])
    if isinstance(near_matches, list) and near_matches:
        for index, near_match in enumerate(near_matches, start=1):
            if not isinstance(near_match, Mapping):
                continue
            object_summary = near_match.get("object", {})
            label = "(unknown)"
            if isinstance(object_summary, Mapping):
                label = object_summary.get("label") or object_summary.get("id") or label
            lines.append(f"{index}. {label}")
            lines.append(f"   match_kind: {near_match.get('match_kind', '(unknown)')}")
            lines.append(f"   target_ref: {near_match.get('target_ref', '(unknown)')}")
            lines.append(
                f"   resolved_resource_id: {near_match.get('resolved_resource_id', '(unknown)')}"
            )
            subject_key = near_match.get("subject_key")
            if isinstance(subject_key, str) and subject_key:
                lines.append(f"   subject_key: {subject_key}")
            version_or_state = near_match.get("version_or_state")
            if isinstance(version_or_state, str) and version_or_state:
                lines.append(f"   version_or_state: {version_or_state}")
            source = near_match.get("source")
            if isinstance(source, Mapping):
                lines.append(f"   source_family: {source.get('family', '(unknown)')}")
                source_label = source.get("label")
                if isinstance(source_label, str) and source_label:
                    lines.append(f"   source_label: {source_label}")
                source_locator = source.get("locator")
                if isinstance(source_locator, str) and source_locator:
                    lines.append(f"   source_origin: {source_locator}")
            evidence = near_match.get("evidence")
            if isinstance(evidence, list) and evidence:
                lines.append(f"   evidence: {_compact_evidence_entry(evidence[0])}")
    else:
        lines.append("(no near matches)")

    next_steps = absence_report.get("next_steps")
    lines.extend(["", "Next steps"])
    if isinstance(next_steps, list) and next_steps:
        lines.extend(f"- {step}" for step in next_steps)
    else:
        lines.append("(no suggested next steps)")

    notices = absence_report.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def _compact_evidence_entry(entry: Any) -> str:
    if not isinstance(entry, Mapping):
        return "(unknown)"
    claim_kind = entry.get("claim_kind", "(unknown)")
    asserted_by = entry.get("asserted_by_label") or entry.get("asserted_by_family") or "(unknown)"
    return f"{claim_kind} via {asserted_by}"


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

from __future__ import annotations

from typing import Any, Mapping


def format_comparison(comparison: Mapping[str, Any]) -> str:
    lines = [
        "Comparison",
        f"status: {comparison.get('status', '(unknown)')}",
    ]
    lines.extend(["", "Left"])
    lines.extend(_format_side(comparison.get("left", {})))
    lines.extend(["", "Right"])
    lines.extend(_format_side(comparison.get("right", {})))

    agreements = comparison.get("agreements")
    lines.extend(["", "Agreements"])
    if isinstance(agreements, list) and agreements:
        for agreement in agreements:
            if isinstance(agreement, Mapping):
                lines.append(
                    f"- {agreement.get('category', '(unknown)')} = {agreement.get('value', '(unknown)')}"
                )
    else:
        lines.append("(no agreements)")

    disagreements = comparison.get("disagreements")
    lines.extend(["", "Disagreements"])
    if isinstance(disagreements, list) and disagreements:
        for disagreement in disagreements:
            if isinstance(disagreement, Mapping):
                lines.append(
                    "- "
                    f"{disagreement.get('category', '(unknown)')}: "
                    f"{disagreement.get('left_value', '(unknown)')} != "
                    f"{disagreement.get('right_value', '(unknown)')}"
                )
    else:
        lines.append("(no disagreements)")

    notices = comparison.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def _format_side(side: Any) -> list[str]:
    if not isinstance(side, Mapping):
        return ["status: (unknown)"]

    lines = [
        f"target_ref: {side.get('target_ref', '(unknown)')}",
        f"status: {side.get('status', '(unknown)')}",
    ]
    resolved_resource_id = side.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    object_summary = side.get("object")
    if isinstance(object_summary, Mapping):
        lines.append(f"object_id: {object_summary.get('id', '(unknown)')}")
        if object_summary.get("kind"):
            lines.append(f"object_kind: {object_summary['kind']}")
        if object_summary.get("label"):
            lines.append(f"object_label: {object_summary['label']}")

    version_or_state = side.get("version_or_state")
    if isinstance(version_or_state, str) and version_or_state:
        lines.append(f"version_or_state: {version_or_state}")

    source = side.get("source")
    if isinstance(source, Mapping):
        lines.append(f"source_family: {source.get('family', '(unknown)')}")
        if source.get("label"):
            lines.append(f"source_label: {source['label']}")
        if source.get("locator"):
            lines.append(f"source_origin: {source['locator']}")

    evidence = side.get("evidence")
    if isinstance(evidence, list) and evidence:
        lines.append("Evidence")
        lines.extend(f"- {_format_evidence_entry(entry)}" for entry in evidence if isinstance(entry, Mapping))

    notices = side.get("notices")
    if isinstance(notices, list) and notices:
        lines.append("Side notices")
        lines.extend(_format_notice_lines(notices))

    return lines


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


def _format_evidence_entry(entry: Mapping[str, Any]) -> str:
    claim_kind = entry.get("claim_kind", "(unknown)")
    claim_value = entry.get("claim_value", "(unknown)")
    asserted_by = entry.get("asserted_by_label") or entry.get("asserted_by_family") or "(unknown)"
    evidence_kind = entry.get("evidence_kind", "(unknown)")
    evidence_locator = entry.get("evidence_locator", "(unknown)")
    text = f"{claim_kind} = {claim_value} ({asserted_by}, {evidence_kind}, {evidence_locator})"
    asserted_at = entry.get("asserted_at")
    if asserted_at:
        text += f" @ {asserted_at}"
    return text

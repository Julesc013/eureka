from __future__ import annotations

from typing import Any, Mapping

from surfaces.native.cli.formatters.representations import format_representation_lines


def format_resolution_workspace(
    workbench_session: Mapping[str, Any],
    *,
    resolution_actions: Mapping[str, Any] | None = None,
) -> str:
    active_job = workbench_session["active_job"]
    lines = [
        "Resolution",
        f"session_id: {workbench_session.get('session_id', '(unknown)')}",
        f"target_ref: {active_job.get('target_ref', '(unknown)')}",
        f"status: {active_job.get('status', '(unknown)')}",
        f"job_id: {active_job.get('job_id', '(unknown)')}",
    ]
    resolved_resource_id = workbench_session.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    selected_object = workbench_session.get("selected_object")
    if isinstance(selected_object, Mapping):
        lines.extend(
            [
                "",
                "Selected object",
                f"id: {selected_object.get('id', '(unknown)')}",
            ]
        )
        if selected_object.get("kind"):
            lines.append(f"kind: {selected_object['kind']}")
        if selected_object.get("label"):
            lines.append(f"label: {selected_object['label']}")

    source = workbench_session.get("source")
    if isinstance(source, Mapping):
        lines.extend(
            [
                "",
                "Source",
                f"family: {source.get('family', '(unknown)')}",
            ]
        )
        if source.get("label"):
            lines.append(f"label: {source['label']}")
        if source.get("locator"):
            lines.append(f"origin: {source['locator']}")

    evidence = workbench_session.get("evidence")
    if isinstance(evidence, list) and evidence:
        lines.extend(["", "Evidence"])
        lines.extend(f"- {_format_evidence_entry(entry)}" for entry in evidence if isinstance(entry, Mapping))

    representations = workbench_session.get("representations")
    if isinstance(representations, list) and representations:
        lines.extend(["", "Known representations/access paths"])
        lines.extend(format_representation_lines(representations))

    if resolution_actions is not None:
        actions = resolution_actions.get("actions", [])
        lines.extend(["", "Actions"])
        available_actions = [
            action for action in actions if action.get("availability") == "available"
        ]
        unavailable_actions = [
            action for action in actions if action.get("availability") != "available"
        ]
        if available_actions:
            lines.extend(
                f"- available {action.get('action_id', '(unknown)')}: {action.get('label', '(unknown)')}"
                for action in available_actions
            )
        else:
            lines.append("(no available actions)")
        for action in unavailable_actions:
            lines.append(
                f"- unavailable {action.get('action_id', '(unknown)')}: {action.get('label', '(unknown)')}"
            )

        notices = resolution_actions.get("notices")
        if isinstance(notices, list) and notices:
            lines.extend(["", "Action notices"])
            lines.extend(_format_notice_lines(notices))

    notices = workbench_session.get("notices")
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

from __future__ import annotations

from typing import Any, Mapping


def format_handoff(handoff: Mapping[str, Any]) -> str:
    lines = [
        "Representation handoff",
        f"status: {handoff.get('status', '(unknown)')}",
        f"target_ref: {handoff.get('target_ref', '(unknown)')}",
    ]

    resolved_resource_id = handoff.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    preferred_representation_id = handoff.get("preferred_representation_id")
    if isinstance(preferred_representation_id, str) and preferred_representation_id:
        lines.append(f"preferred_representation_id: {preferred_representation_id}")

    compatibility_status = handoff.get("compatibility_status")
    if isinstance(compatibility_status, str) and compatibility_status:
        lines.append(f"compatibility_status: {compatibility_status}")

    strategy_profile = handoff.get("strategy_profile")
    if isinstance(strategy_profile, Mapping):
        lines.extend(
            [
                "",
                "Strategy",
                f"strategy_id: {strategy_profile.get('strategy_id', '(unknown)')}",
                f"label: {strategy_profile.get('label', '(unknown)')}",
            ]
        )

    host_profile = handoff.get("host_profile")
    if isinstance(host_profile, Mapping):
        lines.extend(
            [
                "",
                "Host profile",
                f"host_profile_id: {host_profile.get('host_profile_id', '(unknown)')}",
                f"os_family: {host_profile.get('os_family', '(unknown)')}",
                f"architecture: {host_profile.get('architecture', '(unknown)')}",
            ]
        )

    source = handoff.get("source")
    if isinstance(source, Mapping):
        lines.extend(
            [
                "",
                "Source",
                f"family: {source.get('family', '(unknown)')}",
            ]
        )
        label = source.get("label")
        if isinstance(label, str) and label:
            lines.append(f"label: {label}")
        locator = source.get("locator")
        if isinstance(locator, str) and locator:
            lines.append(f"origin: {locator}")

    compatibility_reasons = handoff.get("compatibility_reasons")
    if isinstance(compatibility_reasons, list) and compatibility_reasons:
        lines.extend(["", "Compatibility reasons"])
        for reason in compatibility_reasons:
            if not isinstance(reason, Mapping):
                continue
            lines.append(
                f"- {reason.get('code', '(unknown)')}: {reason.get('message', '(unknown)')}"
            )

    selections = handoff.get("selections")
    if isinstance(selections, list):
        for status in ("preferred", "available", "unsuitable", "unknown"):
            matching = [
                selection
                for selection in selections
                if isinstance(selection, Mapping) and selection.get("selection_status") == status
            ]
            lines.extend(["", status.capitalize()])
            if not matching:
                lines.append("(none)")
                continue
            lines.extend(_format_selection_lines(matching))

    notices = handoff.get("notices")
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


def _format_selection_lines(selections: list[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for index, selection in enumerate(selections, start=1):
        lines.append(f"{index}. {selection.get('label', '(unknown)')}")
        lines.append(
            f"   representation_id: {selection.get('representation_id', '(unknown)')}"
        )
        lines.append(
            f"   representation_kind: {selection.get('representation_kind', '(unknown)')}"
        )
        lines.append(f"   access_kind: {selection.get('access_kind', '(unknown)')}")
        lines.append(f"   source_family: {selection.get('source_family', '(unknown)')}")
        access_locator = selection.get("access_locator")
        if isinstance(access_locator, str) and access_locator:
            lines.append(f"   access_locator: {access_locator}")
        source_locator = selection.get("source_locator")
        if isinstance(source_locator, str) and source_locator:
            lines.append(f"   source_locator: {source_locator}")
        host_profile_id = selection.get("host_profile_id")
        if isinstance(host_profile_id, str) and host_profile_id:
            lines.append(f"   host_profile_id: {host_profile_id}")
        strategy_id = selection.get("strategy_id")
        if isinstance(strategy_id, str) and strategy_id:
            lines.append(f"   strategy_id: {strategy_id}")
        reason_codes = selection.get("reason_codes")
        reason_messages = selection.get("reason_messages")
        if isinstance(reason_codes, list) and isinstance(reason_messages, list):
            for reason_code, reason_message in zip(reason_codes, reason_messages):
                lines.append(f"   reason: {reason_code} - {reason_message}")
    return lines

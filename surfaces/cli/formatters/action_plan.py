from __future__ import annotations

from typing import Any, Mapping


def format_action_plan(action_plan: Mapping[str, Any]) -> str:
    lines = [
        "Action plan",
        f"status: {action_plan.get('status', '(unknown)')}",
        f"target_ref: {action_plan.get('target_ref', '(unknown)')}",
    ]

    resolved_resource_id = action_plan.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    compatibility_status = action_plan.get("compatibility_status")
    if isinstance(compatibility_status, str) and compatibility_status:
        lines.append(f"compatibility_status: {compatibility_status}")

    strategy_profile = action_plan.get("strategy_profile")
    if isinstance(strategy_profile, Mapping):
        lines.extend(
            [
                "",
                "Strategy",
                f"strategy_id: {strategy_profile.get('strategy_id', '(unknown)')}",
                f"label: {strategy_profile.get('label', '(unknown)')}",
            ]
        )
        description = strategy_profile.get("description")
        if isinstance(description, str) and description:
            lines.append(f"description: {description}")
        emphasis_hints = strategy_profile.get("emphasis_hints")
        if isinstance(emphasis_hints, list) and emphasis_hints:
            lines.append(f"emphasis_hints: {', '.join(str(hint) for hint in emphasis_hints)}")

    strategy_rationale = action_plan.get("strategy_rationale")
    if isinstance(strategy_rationale, list) and strategy_rationale:
        lines.extend(["", "Strategy rationale"])
        for rationale in strategy_rationale:
            lines.append(f"- {rationale}")

    host_profile = action_plan.get("host_profile")
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

    primary_object = action_plan.get("primary_object")
    if isinstance(primary_object, Mapping):
        lines.extend(
            [
                "",
                "Target",
                f"id: {primary_object.get('id', '(unknown)')}",
            ]
        )
        label = primary_object.get("label")
        if isinstance(label, str) and label:
            lines.append(f"label: {label}")
        kind = primary_object.get("kind")
        if isinstance(kind, str) and kind:
            lines.append(f"kind: {kind}")

    source = action_plan.get("source")
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

    compatibility_reasons = action_plan.get("compatibility_reasons")
    if isinstance(compatibility_reasons, list) and compatibility_reasons:
        lines.extend(["", "Compatibility reasons"])
        for reason in compatibility_reasons:
            if not isinstance(reason, Mapping):
                continue
            lines.append(f"- {reason.get('code', '(unknown)')}: {reason.get('message', '(unknown)')}")

    actions = action_plan.get("actions")
    if isinstance(actions, list) and actions:
        for status in ("recommended", "available", "unavailable"):
            matching = [
                action for action in actions
                if isinstance(action, Mapping) and action.get("status") == status
            ]
            lines.extend(["", status.capitalize()])
            if not matching:
                lines.append("(none)")
                continue
            lines.extend(_format_action_lines(matching))

    notices = action_plan.get("notices")
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


def _format_action_lines(actions: list[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for index, action in enumerate(actions, start=1):
        lines.append(f"{index}. {action.get('label', '(unknown)')}")
        lines.append(f"   action_id: {action.get('action_id', '(unknown)')}")
        lines.append(f"   kind: {action.get('kind', '(unknown)')}")
        representation_label = action.get("representation_label")
        if isinstance(representation_label, str) and representation_label:
            lines.append(f"   representation: {representation_label}")
        representation_kind = action.get("representation_kind")
        if isinstance(representation_kind, str) and representation_kind:
            lines.append(f"   representation_kind: {representation_kind}")
        access_kind = action.get("access_kind")
        if isinstance(access_kind, str) and access_kind:
            lines.append(f"   access_kind: {access_kind}")
        source_family = action.get("source_family")
        if isinstance(source_family, str) and source_family:
            lines.append(f"   source_family: {source_family}")
        access_locator = action.get("access_locator")
        if isinstance(access_locator, str) and access_locator:
            lines.append(f"   access_locator: {access_locator}")
        route_hint = action.get("route_hint")
        if isinstance(route_hint, str) and route_hint:
            lines.append(f"   route_hint: {route_hint}")
        parameter_hint = action.get("parameter_hint")
        if isinstance(parameter_hint, str) and parameter_hint:
            lines.append(f"   parameter_hint: {parameter_hint}")
        reason_codes = action.get("reason_codes")
        reason_messages = action.get("reason_messages")
        if isinstance(reason_codes, list) and isinstance(reason_messages, list):
            for reason_code, reason_message in zip(reason_codes, reason_messages):
                lines.append(f"   reason: {reason_code} - {reason_message}")
    return lines

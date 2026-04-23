from __future__ import annotations

from typing import Any, Mapping


def format_compatibility(compatibility: Mapping[str, Any]) -> str:
    lines = [
        "Compatibility",
        f"status: {compatibility.get('status', '(unknown)')}",
        f"target_ref: {compatibility.get('target_ref', '(unknown)')}",
    ]

    compatibility_status = compatibility.get("compatibility_status")
    if isinstance(compatibility_status, str) and compatibility_status:
        lines.append(f"compatibility_status: {compatibility_status}")

    resolved_resource_id = compatibility.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    host_profile = compatibility.get("host_profile")
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
        runtime_family = host_profile.get("runtime_family")
        if isinstance(runtime_family, str) and runtime_family:
            lines.append(f"runtime_family: {runtime_family}")
        features = host_profile.get("features")
        if isinstance(features, list) and features:
            lines.append(f"features: {', '.join(str(feature) for feature in features)}")

    primary_object = compatibility.get("primary_object")
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

    source = compatibility.get("source")
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

    reasons = compatibility.get("reasons")
    if isinstance(reasons, list) and reasons:
        lines.extend(["", "Reasons"])
        for reason in reasons:
            if not isinstance(reason, Mapping):
                continue
            lines.append(
                f"- {reason.get('code', '(unknown)')}: {reason.get('message', '(unknown)')}"
            )

    next_steps = compatibility.get("next_steps")
    if isinstance(next_steps, list) and next_steps:
        lines.extend(["", "Next steps"])
        for step in next_steps:
            lines.append(f"- {step}")

    notices = compatibility.get("notices")
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

from __future__ import annotations

from html import escape
from typing import Any, Mapping, Sequence


def render_action_plan_html(
    action_plan: Mapping[str, Any] | None,
    *,
    target_ref: str,
    host_profile_id: str | None,
    strategy_id: str | None,
    host_profile_presets: Sequence[Mapping[str, Any]],
    strategy_profiles: Sequence[Mapping[str, Any]],
    message: str | None = None,
) -> str:
    normalized_host_profile_id = host_profile_id or ""
    normalized_strategy_id = strategy_id or "inspect"
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Action Plan</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Action Plan</h1>",
        "      <p>Bounded recommended, available, and unavailable next steps derived from one resolved target.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/representations\">List known representations</a>",
        "        <a href=\"/compatibility\">Check compatibility</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Plan Actions</h2>",
        "        <form method=\"get\" action=\"/action-plan\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <label for=\"host\">Host profile</label>",
        "          <select id=\"host\" name=\"host\">",
        f"            <option value=\"\"{' selected' if not normalized_host_profile_id else ''}>(none)</option>",
    ]
    for preset in host_profile_presets:
        preset_id = _require_string(preset.get("host_profile_id"), "host_preset.host_profile_id")
        os_family = _require_string(preset.get("os_family"), "host_preset.os_family")
        architecture = _require_string(preset.get("architecture"), "host_preset.architecture")
        selected = " selected" if preset_id == normalized_host_profile_id else ""
        parts.append(
            f"            <option value=\"{escape(preset_id, quote=True)}\"{selected}>"
            f"{escape(preset_id)} ({escape(os_family)}, {escape(architecture)})"
            "</option>"
        )
    parts.extend(
        [
            "          </select>",
            "          <label for=\"strategy\">Strategy</label>",
            "          <select id=\"strategy\" name=\"strategy\">",
        ]
    )
    for profile in strategy_profiles:
        preset_id = _require_string(profile.get("strategy_id"), "strategy_profile.strategy_id")
        label = _require_string(profile.get("label"), "strategy_profile.label")
        selected = " selected" if preset_id == normalized_strategy_id else ""
        parts.append(
            f"            <option value=\"{escape(preset_id, quote=True)}\"{selected}>"
            f"{escape(preset_id)} ({escape(label)})"
            "</option>"
        )
    parts.extend(
        [
            "          </select>",
            "          <button type=\"submit\">Plan</button>",
            "        </form>",
            "      </section>",
        ]
    )

    if message is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Action Plan</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    elif action_plan is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Action Plan</h2>",
                "        <dl>",
                f"          <dt>Status</dt><dd>{escape(_require_string(action_plan.get('status'), 'action_plan.status'))}</dd>",
                f"          <dt>Target ref</dt><dd>{escape(_require_string(action_plan.get('target_ref'), 'action_plan.target_ref'))}</dd>",
            ]
        )
        strategy_profile = _optional_mapping(
            action_plan.get("strategy_profile"),
            "action_plan.strategy_profile",
        )
        if strategy_profile is not None:
            parts.append(
                f"          <dt>Strategy</dt><dd>{escape(_require_string(strategy_profile.get('strategy_id'), 'action_plan.strategy_profile.strategy_id'))}</dd>"
            )
        compatibility_status = _optional_string(
            action_plan.get("compatibility_status"),
            "action_plan.compatibility_status",
        )
        if compatibility_status is not None:
            parts.append(f"          <dt>Compatibility status</dt><dd>{escape(compatibility_status)}</dd>")
        resolved_resource_id = _optional_string(
            action_plan.get("resolved_resource_id"),
            "action_plan.resolved_resource_id",
        )
        if resolved_resource_id is not None:
            parts.append(f"          <dt>Resolved resource ID</dt><dd>{escape(resolved_resource_id)}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )

        strategy_rationale = _string_list(action_plan.get("strategy_rationale"), "action_plan.strategy_rationale")
        if strategy_profile is not None:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Strategy</h2>",
                    "        <dl>",
                    f"          <dt>ID</dt><dd>{escape(_require_string(strategy_profile.get('strategy_id'), 'action_plan.strategy_profile.strategy_id'))}</dd>",
                    f"          <dt>Label</dt><dd>{escape(_require_string(strategy_profile.get('label'), 'action_plan.strategy_profile.label'))}</dd>",
                    f"          <dt>Description</dt><dd>{escape(_require_string(strategy_profile.get('description'), 'action_plan.strategy_profile.description'))}</dd>",
                    "        </dl>",
                ]
            )
            emphasis_hints = _string_list(
                strategy_profile.get("emphasis_hints"),
                "action_plan.strategy_profile.emphasis_hints",
            )
            if emphasis_hints:
                parts.extend(
                    [
                        "        <ul>",
                    ]
                )
                for hint in emphasis_hints:
                    parts.append(f"          <li>{escape(hint)}</li>")
                parts.append("        </ul>")
            if strategy_rationale:
                parts.extend(
                    [
                        "        <ul>",
                    ]
                )
                for rationale in strategy_rationale:
                    parts.append(f"          <li>{escape(rationale)}</li>")
                parts.append("        </ul>")
            parts.append("      </section>")

        host_profile = _optional_mapping(action_plan.get("host_profile"), "action_plan.host_profile")
        if host_profile is not None:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Host Profile</h2>",
                    "        <dl>",
                    f"          <dt>ID</dt><dd>{escape(_require_string(host_profile.get('host_profile_id'), 'host_profile.host_profile_id'))}</dd>",
                    f"          <dt>OS family</dt><dd>{escape(_require_string(host_profile.get('os_family'), 'host_profile.os_family'))}</dd>",
                    f"          <dt>Architecture</dt><dd>{escape(_require_string(host_profile.get('architecture'), 'host_profile.architecture'))}</dd>",
                    "        </dl>",
                    "      </section>",
                ]
            )

        compatibility_reasons = _mapping_list(
            action_plan.get("compatibility_reasons"),
            "action_plan.compatibility_reasons",
            allow_none=True,
        )
        if compatibility_reasons:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Compatibility Reasons</h2>",
                    "        <ul>",
                ]
            )
            for reason in compatibility_reasons:
                parts.append(
                    "          <li>"
                    f"<strong>{escape(_require_string(reason.get('code'), 'compatibility_reason.code'))}</strong>: "
                    f"{escape(_require_string(reason.get('message'), 'compatibility_reason.message'))}</li>"
                )
            parts.extend(
                [
                    "        </ul>",
                    "      </section>",
                ]
            )

        actions = _mapping_list(action_plan.get("actions"), "action_plan.actions")
        for section_label, status in (
            ("Recommended", "recommended"),
            ("Available", "available"),
            ("Unavailable", "unavailable"),
        ):
            matching = [action for action in actions if action.get("status") == status]
            parts.extend(
                [
                    "      <section>",
                    f"        <h2>{escape(section_label)}</h2>",
                ]
            )
            if not matching:
                parts.append("        <p>(none)</p>")
            else:
                parts.append("        <ul>")
                for action in matching:
                    parts.append("          <li>")
                    route_hint = _optional_string(action.get("route_hint"), "action.route_hint")
                    label = _require_string(action.get("label"), "action.label")
                    if route_hint is not None:
                        parts.append(
                            f"            <strong><a href=\"{escape(route_hint, quote=True)}\">{escape(label)}</a></strong>"
                        )
                    else:
                        parts.append(f"            <strong>{escape(label)}</strong>")
                    parts.append("            <dl>")
                    parts.append(f"              <dt>Action ID</dt><dd>{escape(_require_string(action.get('action_id'), 'action.action_id'))}</dd>")
                    parts.append(f"              <dt>Kind</dt><dd>{escape(_require_string(action.get('kind'), 'action.kind'))}</dd>")
                    for key, field_name, label_text in (
                        ("representation_label", "action.representation_label", "Representation"),
                        ("representation_kind", "action.representation_kind", "Representation kind"),
                        ("access_kind", "action.access_kind", "Access kind"),
                        ("source_family", "action.source_family", "Source family"),
                        ("access_locator", "action.access_locator", "Access locator"),
                        ("parameter_hint", "action.parameter_hint", "Parameter hint"),
                    ):
                        optional = _optional_string(action.get(key), field_name)
                        if optional is not None:
                            parts.append(f"              <dt>{escape(label_text)}</dt><dd>{escape(optional)}</dd>")
                    parts.append("            </dl>")
                    reason_codes = _string_list(action.get("reason_codes"), "action.reason_codes")
                    reason_messages = _string_list(action.get("reason_messages"), "action.reason_messages")
                    if reason_codes and reason_messages:
                        parts.append("            <ul>")
                        for reason_code, reason_message in zip(reason_codes, reason_messages):
                            parts.append(
                                "              <li>"
                                f"<strong>{escape(reason_code)}</strong>: {escape(reason_message)}</li>"
                            )
                        parts.append("            </ul>")
                    parts.append("          </li>")
                parts.append("        </ul>")
            parts.append("      </section>")

        notices = _mapping_list(action_plan.get("notices"), "action_plan.notices", allow_none=True)
        if notices:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Notices</h2>",
                    "        <ul>",
                ]
            )
            for notice in notices:
                line = (
                    f"          <li><strong>{escape(_require_string(notice.get('code'), 'notice.code'))}</strong> "
                    f"({escape(_require_string(notice.get('severity'), 'notice.severity'))})"
                )
                message_text = _optional_string(notice.get("message"), "notice.message")
                if message_text is not None:
                    line += f": {escape(message_text)}"
                line += "</li>"
                parts.append(line)
            parts.extend(
                [
                    "        </ul>",
                    "      </section>",
                ]
            )

    parts.extend(
        [
            "    </main>",
            "  </body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object when provided.")
    return value


def _mapping_list(value: Any, field_name: str, *, allow_none: bool = False) -> list[Mapping[str, Any]]:
    if value is None:
        if allow_none:
            return []
        raise ValueError(f"{field_name} must be a list.")
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    items: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        items.append(item)
    return items


def _string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    items: list[str] = []
    for index, item in enumerate(value):
        items.append(_require_string(item, f"{field_name}[{index}]"))
    return items


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string when provided.")
    return value

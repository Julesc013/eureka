from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_handoff_html(
    handoff_view_model: Mapping[str, Any] | None,
    *,
    target_ref: str,
    host_profile_id: str | None,
    strategy_id: str | None,
    host_profile_presets: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    strategy_profiles: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    message: str | None = None,
    allow_payload_readback: bool = True,
) -> str:
    status = "(not evaluated)"
    preferred_representation_id = None
    compatibility_status = None
    selections: list[Mapping[str, Any]] = []
    notices: list[Mapping[str, Any]] = []
    source = None
    strategy_profile = None
    host_profile = None
    compatibility_reasons: list[Mapping[str, Any]] = []
    if handoff_view_model is not None:
        status = _require_string(handoff_view_model.get("status"), "handoff.status")
        preferred_representation_id = _optional_string(
            handoff_view_model.get("preferred_representation_id"),
            "handoff.preferred_representation_id",
        )
        compatibility_status = _optional_string(
            handoff_view_model.get("compatibility_status"),
            "handoff.compatibility_status",
        )
        selections = _selection_list(handoff_view_model.get("selections"))
        notices = _notice_list(handoff_view_model.get("notices"))
        source = _optional_mapping(handoff_view_model.get("source"), "handoff.source")
        strategy_profile = _optional_mapping(
            handoff_view_model.get("strategy_profile"),
            "handoff.strategy_profile",
        )
        host_profile = _optional_mapping(handoff_view_model.get("host_profile"), "handoff.host_profile")
        compatibility_reasons = _reason_list(handoff_view_model.get("compatibility_reasons"))

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Representation Handoff</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Representation Handoff</h1>",
        "      <p>Compatibility-first bounded representation-selection and handoff recommendation for one resolved target.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/representations\">List known representations</a>",
        "        <a href=\"/action-plan\">Plan bounded next steps</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Evaluate handoff</h2>",
        "        <form method=\"get\" action=\"/handoff\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <label for=\"host\">Host profile</label>",
        "          <select id=\"host\" name=\"host\">",
        "            <option value=\"\">(none)</option>",
    ]
    for preset in host_profile_presets:
        if not isinstance(preset, Mapping):
            continue
        preset_id = _require_string(preset.get("host_profile_id"), "host_profile_preset.host_profile_id")
        selected = " selected" if preset_id == host_profile_id else ""
        parts.append(
            f"            <option value=\"{escape(preset_id, quote=True)}\"{selected}>{escape(preset_id)}</option>"
        )
    parts.extend(
        [
            "          </select>",
            "          <label for=\"strategy\">Strategy</label>",
            "          <select id=\"strategy\" name=\"strategy\">",
            "            <option value=\"\">(default inspect)</option>",
        ]
    )
    for preset in strategy_profiles:
        if not isinstance(preset, Mapping):
            continue
        preset_id = _require_string(preset.get("strategy_id"), "strategy_profile.strategy_id")
        selected = " selected" if preset_id == strategy_id else ""
        parts.append(
            f"            <option value=\"{escape(preset_id, quote=True)}\"{selected}>{escape(preset_id)}</option>"
        )
    parts.extend(
        [
            "          </select>",
            "          <button type=\"submit\">Evaluate handoff</button>",
            "        </form>",
            "      </section>",
        ]
    )
    if message is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Message</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    parts.extend(
        [
            "      <section>",
            "        <h2>Summary</h2>",
            "        <dl>",
            f"          <dt>Status</dt><dd>{escape(status)}</dd>",
            f"          <dt>Target ref</dt><dd>{escape(target_ref)}</dd>",
        ]
    )
    if preferred_representation_id is not None:
        parts.append(f"          <dt>Preferred representation</dt><dd>{escape(preferred_representation_id)}</dd>")
    if compatibility_status is not None:
        parts.append(f"          <dt>Compatibility status</dt><dd>{escape(compatibility_status)}</dd>")
    if strategy_profile is not None:
        parts.append(
            f"          <dt>Strategy</dt><dd>{escape(_require_string(strategy_profile.get('strategy_id'), 'handoff.strategy_profile.strategy_id'))}</dd>"
        )
    if host_profile is not None:
        parts.append(
            f"          <dt>Host profile</dt><dd>{escape(_require_string(host_profile.get('host_profile_id'), 'handoff.host_profile.host_profile_id'))}</dd>"
        )
    parts.extend(["        </dl>", "      </section>"])

    if source is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Source</h2>",
                "        <dl>",
                f"          <dt>Family</dt><dd>{escape(_require_string(source.get('family'), 'handoff.source.family'))}</dd>",
            ]
        )
        label = _optional_string(source.get("label"), "handoff.source.label")
        if label is not None:
            parts.append(f"          <dt>Label</dt><dd>{escape(label)}</dd>")
        locator = _optional_string(source.get("locator"), "handoff.source.locator")
        if locator is not None:
            parts.append(f"          <dt>Origin</dt><dd>{escape(locator)}</dd>")
        parts.extend(["        </dl>", "      </section>"])

    for status_name, heading in (
        ("preferred", "Preferred bounded fit"),
        ("available", "Available alternatives"),
        ("unsuitable", "Unsuitable choices"),
        ("unknown", "Unknown choices"),
    ):
        matching = [
            selection for selection in selections if selection.get("selection_status") == status_name
        ]
        parts.extend(["      <section>", f"        <h2>{escape(heading)}</h2>"])
        if not matching:
            parts.append("        <p>(none)</p>")
            parts.append("      </section>")
            continue
        parts.append("        <ul>")
        for selection in matching:
            label = _require_string(selection.get("label"), "handoff.selection.label")
            access_locator = _optional_string(selection.get("access_locator"), "handoff.selection.access_locator")
            if access_locator is not None:
                parts.append(
                    "          <li>"
                    f"<strong><a href=\"{escape(access_locator, quote=True)}\">{escape(label)}</a></strong>"
                )
            else:
                parts.append(f"          <li><strong>{escape(label)}</strong>")
            parts.append("            <dl>")
            parts.append(
                f"              <dt>Representation kind</dt><dd>{escape(_require_string(selection.get('representation_kind'), 'handoff.selection.representation_kind'))}</dd>"
            )
            parts.append(
                f"              <dt>Access kind</dt><dd>{escape(_require_string(selection.get('access_kind'), 'handoff.selection.access_kind'))}</dd>"
            )
            parts.append(
                f"              <dt>Source family</dt><dd>{escape(_require_string(selection.get('source_family'), 'handoff.selection.source_family'))}</dd>"
            )
            source_locator = _optional_string(selection.get("source_locator"), "handoff.selection.source_locator")
            if source_locator is not None:
                parts.append(f"              <dt>Source locator</dt><dd>{escape(source_locator)}</dd>")
            filename = _optional_string(selection.get("filename"), "handoff.selection.filename")
            if filename is not None:
                parts.append(f"              <dt>Filename</dt><dd>{escape(filename)}</dd>")
            is_fetchable = selection.get("is_fetchable")
            if isinstance(is_fetchable, bool):
                parts.append(
                    f"              <dt>Fetchable</dt><dd>{escape(str(is_fetchable).lower())}</dd>"
                )
                if is_fetchable and allow_payload_readback:
                    fetch_href = (
                        "/fetch?target_ref="
                        + quote(target_ref, safe="")
                        + "&representation_id="
                        + quote(
                            _require_string(
                                selection.get("representation_id"),
                                "handoff.selection.representation_id",
                            ),
                            safe="",
                        )
                    )
                    parts.append(
                        f"              <dt>Bounded fetch</dt><dd><a href=\"{escape(fetch_href, quote=True)}\">Retrieve local fixture payload</a></dd>"
                    )
                elif is_fetchable:
                    parts.append(
                        "              <dt>Bounded fetch</dt><dd>Disabled in public-alpha mode.</dd>"
                    )
            parts.append("            </dl>")
            reason_codes = _string_list(selection.get("reason_codes"), "handoff.selection.reason_codes")
            reason_messages = _string_list(selection.get("reason_messages"), "handoff.selection.reason_messages")
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

    if compatibility_reasons:
        parts.extend(["      <section>", "        <h2>Compatibility reasons</h2>", "        <ul>"])
        for reason in compatibility_reasons:
            parts.append(
                "          <li>"
                f"<strong>{escape(_require_string(reason.get('code'), 'handoff.compatibility_reason.code'))}</strong>: "
                f"{escape(_require_string(reason.get('message'), 'handoff.compatibility_reason.message'))}</li>"
            )
        parts.extend(["        </ul>", "      </section>"])

    if notices:
        parts.extend(["      <section>", "        <h2>Notices</h2>", "        <ul>"])
        for notice in notices:
            code = _require_string(notice.get("code"), "handoff.notice.code")
            severity = _require_string(notice.get("severity"), "handoff.notice.severity")
            notice_message = _optional_string(notice.get("message"), "handoff.notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if notice_message is not None:
                item += f": {escape(notice_message)}"
            item += "</li>"
            parts.append(item)
        parts.extend(["        </ul>", "      </section>"])

    parts.extend(["    </main>", "  </body>", "</html>", ""])
    return "\n".join(parts)


def _selection_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("handoff.selections must be a list.")
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"handoff.selections[{index}] must be an object.")
        result.append(item)
    return result


def _reason_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("handoff.compatibility_reasons must be a list.")
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"handoff.compatibility_reasons[{index}] must be an object.")
        result.append(item)
    return result


def _notice_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("handoff.notices must be a list when provided.")
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"handoff.notices[{index}] must be an object.")
        result.append(item)
    return result


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object when provided.")
    return value


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


def _string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value)]

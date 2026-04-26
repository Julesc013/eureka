from __future__ import annotations

from html import escape
from typing import Any, Mapping, Sequence


def render_compatibility_html(
    compatibility: Mapping[str, Any] | None,
    *,
    target_ref: str,
    host_profile_id: str,
    host_profile_presets: Sequence[Mapping[str, Any]],
    message: str | None = None,
) -> str:
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Compatibility Check</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Compatibility Check</h1>",
        "      <p>Compatibility-first bounded verdicts for one resolved target and one bootstrap host profile preset.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/representations\">List known representations</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Evaluate Compatibility</h2>",
        "        <form method=\"get\" action=\"/compatibility\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <label for=\"host\">Host profile</label>",
        "          <select id=\"host\" name=\"host\">",
    ]
    for preset in host_profile_presets:
        preset_id = _require_string(preset.get("host_profile_id"), "host_preset.host_profile_id")
        os_family = _require_string(preset.get("os_family"), "host_preset.os_family")
        architecture = _require_string(preset.get("architecture"), "host_preset.architecture")
        selected = " selected" if preset_id == host_profile_id else ""
        parts.append(
            f"            <option value=\"{escape(preset_id, quote=True)}\"{selected}>"
            f"{escape(preset_id)} ({escape(os_family)}, {escape(architecture)})"
            "</option>"
        )
    parts.extend(
        [
            "          </select>",
            "          <button type=\"submit\">Evaluate</button>",
            "        </form>",
            "      </section>",
        ]
    )

    if message is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Compatibility Result</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    elif compatibility is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Compatibility Result</h2>",
                "        <dl>",
                f"          <dt>Status</dt><dd>{escape(_require_string(compatibility.get('status'), 'compatibility.status'))}</dd>",
                f"          <dt>Target ref</dt><dd>{escape(_require_string(compatibility.get('target_ref'), 'compatibility.target_ref'))}</dd>",
            ]
        )
        compatibility_status = _optional_string(
            compatibility.get("compatibility_status"),
            "compatibility.compatibility_status",
        )
        if compatibility_status is not None:
            parts.append(f"          <dt>Compatibility status</dt><dd>{escape(compatibility_status)}</dd>")
        resolved_resource_id = _optional_string(
            compatibility.get("resolved_resource_id"),
            "compatibility.resolved_resource_id",
        )
        if resolved_resource_id is not None:
            parts.append(f"          <dt>Resolved resource ID</dt><dd>{escape(resolved_resource_id)}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )

        host_profile = _require_mapping(compatibility.get("host_profile"), "compatibility.host_profile")
        parts.extend(
            [
                "      <section>",
                "        <h2>Host Profile</h2>",
                "        <dl>",
                f"          <dt>ID</dt><dd>{escape(_require_string(host_profile.get('host_profile_id'), 'host_profile.host_profile_id'))}</dd>",
                f"          <dt>OS family</dt><dd>{escape(_require_string(host_profile.get('os_family'), 'host_profile.os_family'))}</dd>",
                f"          <dt>Architecture</dt><dd>{escape(_require_string(host_profile.get('architecture'), 'host_profile.architecture'))}</dd>",
            ]
        )
        runtime_family = _optional_string(host_profile.get("runtime_family"), "host_profile.runtime_family")
        if runtime_family is not None:
            parts.append(f"          <dt>Runtime family</dt><dd>{escape(runtime_family)}</dd>")
        features = _string_list(host_profile.get("features"), "host_profile.features")
        if features:
            parts.append(f"          <dt>Features</dt><dd>{escape(', '.join(features))}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )

        primary_object = _optional_mapping(compatibility.get("primary_object"), "compatibility.primary_object")
        if primary_object is not None:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Target</h2>",
                    "        <dl>",
                    f"          <dt>ID</dt><dd>{escape(_require_string(primary_object.get('id'), 'primary_object.id'))}</dd>",
                ]
            )
            kind = _optional_string(primary_object.get("kind"), "primary_object.kind")
            label = _optional_string(primary_object.get("label"), "primary_object.label")
            if kind is not None:
                parts.append(f"          <dt>Kind</dt><dd>{escape(kind)}</dd>")
            if label is not None:
                parts.append(f"          <dt>Label</dt><dd>{escape(label)}</dd>")
            parts.extend(
                [
                    "        </dl>",
                    "      </section>",
                ]
            )

        source = _optional_mapping(compatibility.get("source"), "compatibility.source")
        if source is not None:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Source</h2>",
                    "        <dl>",
                    f"          <dt>Family</dt><dd>{escape(_require_string(source.get('family'), 'source.family'))}</dd>",
                ]
            )
            source_label = _optional_string(source.get("label"), "source.label")
            source_locator = _optional_string(source.get("locator"), "source.locator")
            if source_label is not None:
                parts.append(f"          <dt>Label</dt><dd>{escape(source_label)}</dd>")
            if source_locator is not None:
                parts.append(f"          <dt>Origin</dt><dd>{escape(source_locator)}</dd>")
            parts.extend(
                [
                    "        </dl>",
                    "      </section>",
                ]
            )

        reasons = _mapping_list(compatibility.get("reasons"), "compatibility.reasons")
        parts.extend(
            [
                "      <section>",
                "        <h2>Reasons</h2>",
            ]
        )
        if reasons:
            parts.append("        <ul>")
            for reason in reasons:
                parts.append(
                    "          <li>"
                    f"<strong>{escape(_require_string(reason.get('code'), 'reason.code'))}</strong>: "
                    f"{escape(_require_string(reason.get('message'), 'reason.message'))}</li>"
                )
            parts.append("        </ul>")
        else:
            parts.append("        <p>No bounded reasons are available for this verdict.</p>")
        parts.append("      </section>")

        evidence_verdict = _optional_mapping(
            compatibility.get("compatibility_evidence_verdict"),
            "compatibility.compatibility_evidence_verdict",
        )
        compatibility_evidence = _mapping_list(
            compatibility.get("compatibility_evidence"),
            "compatibility.compatibility_evidence",
            allow_none=True,
        )
        parts.extend(
            [
                "      <section>",
                "        <h2>Compatibility Evidence</h2>",
            ]
        )
        if evidence_verdict is not None:
            verdict = _require_string(evidence_verdict.get("verdict"), "compatibility_evidence_verdict.verdict")
            parts.append(f"        <p>Verdict: {escape(verdict)}</p>")
            limitations = _string_list(
                evidence_verdict.get("limitations"),
                "compatibility_evidence_verdict.limitations",
            )
            if limitations:
                parts.append(f"        <p>Limitations: {escape(', '.join(limitations))}</p>")
        if compatibility_evidence:
            parts.append("        <ul>")
            for item in compatibility_evidence:
                parts.append(f"          <li>{escape(_compact_compatibility_evidence(item))}</li>")
            parts.append("        </ul>")
        else:
            parts.append("        <p>No source-backed compatibility evidence is attached to this target.</p>")
        parts.append("      </section>")

        next_steps = _string_list(compatibility.get("next_steps"), "compatibility.next_steps")
        if next_steps:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Next Steps</h2>",
                    "        <ul>",
                ]
            )
            for step in next_steps:
                parts.append(f"          <li>{escape(step)}</li>")
            parts.extend(
                [
                    "        </ul>",
                    "      </section>",
                ]
            )

        notices = _mapping_list(compatibility.get("notices"), "compatibility.notices", allow_none=True)
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


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    return _require_mapping(value, field_name)


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


def _compact_compatibility_evidence(value: Mapping[str, Any]) -> str:
    platform = value.get("platform")
    platform_name = "(unknown platform)"
    if isinstance(platform, Mapping):
        platform_name = str(platform.get("name") or platform.get("marketing_alias") or platform_name)
    confidence = _optional_string(value.get("confidence"), "compatibility_evidence.confidence") or "unknown"
    return (
        f"{platform_name}: "
        f"{_require_string(value.get('claim_type'), 'compatibility_evidence.claim_type')} via "
        f"{_require_string(value.get('evidence_kind'), 'compatibility_evidence.evidence_kind')} "
        f"({confidence})"
    )

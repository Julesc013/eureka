from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_subject_states_html(
    subject_states: Mapping[str, Any] | None,
    *,
    subject_key: str,
    message: str | None = None,
) -> str:
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Subject States</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Subject States</h1>",
        "      <p>Compatibility-first bounded state listing for one bootstrap subject key.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/compare\">Compare two targets</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>List Subject States</h2>",
        "        <form method=\"get\" action=\"/subject\">",
        "          <label for=\"key\">Subject key</label>",
        f"          <input id=\"key\" name=\"key\" type=\"text\" value=\"{escape(subject_key, quote=True)}\">",
        "          <button type=\"submit\">List states</button>",
        "        </form>",
        "      </section>",
    ]

    if message is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Subject State</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    elif subject_states is not None:
        status = _require_string(subject_states.get("status"), "subject_states.status")
        notices = _mapping_list(subject_states.get("notices"), "subject_states.notices", allow_none=True)
        subject = _optional_mapping(subject_states.get("subject"), "subject_states.subject")
        states = _mapping_list(subject_states.get("states"), "subject_states.states")

        parts.extend(
            [
                "      <section>",
                "        <h2>State Listing</h2>",
                "        <dl>",
                f"          <dt>Status</dt><dd>{escape(status)}</dd>",
                f"          <dt>Requested subject key</dt><dd>{escape(_require_string(subject_states.get('requested_subject_key'), 'subject_states.requested_subject_key'))}</dd>",
            ]
        )
        if subject is not None:
            parts.append(
                f"          <dt>State count</dt><dd>{escape(str(_require_int(subject.get('state_count'), 'subject.state_count')))}</dd>"
            )
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )

        if subject is not None:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Subject</h2>",
                    "        <dl>",
                    f"          <dt>Key</dt><dd>{escape(_require_string(subject.get('subject_key'), 'subject.subject_key'))}</dd>",
                    f"          <dt>Label</dt><dd>{escape(_require_string(subject.get('subject_label'), 'subject.subject_label'))}</dd>",
                ]
            )
            source_family_hint = _optional_string(subject.get("source_family_hint"), "subject.source_family_hint")
            if source_family_hint is not None:
                parts.append(f"          <dt>Source family hint</dt><dd>{escape(source_family_hint)}</dd>")
            parts.extend(
                [
                    "        </dl>",
                    "      </section>",
                ]
            )

        parts.extend(
            [
                "      <section>",
                "        <h2>Ordered States</h2>",
            ]
        )
        if states:
            parts.append("        <ol>")
            for index, state in enumerate(states):
                target_ref = _require_string(state.get("target_ref"), f"states[{index}].target_ref")
                resolved_resource_id = _require_string(
                    state.get("resolved_resource_id"),
                    f"states[{index}].resolved_resource_id",
                )
                object_summary = _require_mapping(state.get("object"), f"states[{index}].object")
                object_label = _optional_string(object_summary.get("label"), f"states[{index}].object.label") or _require_string(
                    object_summary.get("id"),
                    f"states[{index}].object.id",
                )
                resolve_link = "/?target_ref=" + quote(target_ref, safe="")
                parts.extend(
                    [
                        "          <li>",
                        f"            <p><a href=\"{escape(resolve_link, quote=True)}\">{escape(object_label)}</a> <span>({escape(target_ref)})</span></p>",
                        "            <dl>",
                        f"              <dt>Resolved resource ID</dt><dd>{escape(resolved_resource_id)}</dd>",
                    ]
                )
                version_or_state = _optional_string(state.get("version_or_state"), f"states[{index}].version_or_state")
                normalized_version_or_state = _optional_string(
                    state.get("normalized_version_or_state"),
                    f"states[{index}].normalized_version_or_state",
                )
                if version_or_state is not None:
                    parts.append(f"              <dt>Version or state</dt><dd>{escape(version_or_state)}</dd>")
                if normalized_version_or_state is not None:
                    parts.append(
                        f"              <dt>Normalized version/state</dt><dd>{escape(normalized_version_or_state)}</dd>"
                    )
                source = _optional_mapping(state.get("source"), f"states[{index}].source")
                if source is not None:
                    parts.append(
                        f"              <dt>Source family</dt><dd>{escape(_require_string(source.get('family'), f'states[{index}].source.family'))}</dd>"
                    )
                    source_label = _optional_string(source.get("label"), f"states[{index}].source.label")
                    source_locator = _optional_string(source.get("locator"), f"states[{index}].source.locator")
                    if source_label is not None:
                        parts.append(f"              <dt>Source label</dt><dd>{escape(source_label)}</dd>")
                    if source_locator is not None:
                        parts.append(f"              <dt>Source origin</dt><dd>{escape(source_locator)}</dd>")
                parts.extend(
                    [
                        "            </dl>",
                    ]
                )
                evidence = _mapping_list(state.get("evidence"), f"states[{index}].evidence", allow_none=True)
                if evidence:
                    parts.extend(
                        [
                            "            <ul>",
                        ]
                    )
                    for entry in evidence:
                        parts.append(f"              <li>{escape(_compact_evidence_text(entry))}</li>")
                    parts.append("            </ul>")
                parts.append("          </li>")
            parts.append("        </ol>")
        else:
            parts.append("        <p>No bounded states are available for this subject.</p>")
        parts.append("      </section>")

        if notices:
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Notices</h2>",
                    "        <ul>",
                ]
            )
            for notice in notices:
                code = _require_string(notice.get("code"), "notice.code")
                severity = _require_string(notice.get("severity"), "notice.severity")
                message_text = _optional_string(notice.get("message"), "notice.message")
                item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
                if message_text is not None:
                    item += f": {escape(message_text)}"
                item += "</li>"
                parts.append(item)
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
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        result.append(item)
    return result


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


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value


def _compact_evidence_text(entry: Mapping[str, Any]) -> str:
    claim_kind = _require_string(entry.get("claim_kind"), "evidence.claim_kind")
    asserted_by = _optional_string(entry.get("asserted_by_label"), "evidence.asserted_by_label") or _require_string(
        entry.get("asserted_by_family"),
        "evidence.asserted_by_family",
    )
    return f"{claim_kind} via {asserted_by}"

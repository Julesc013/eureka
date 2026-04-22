from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_absence_report_html(
    absence_report: Mapping[str, Any] | None,
    *,
    request_kind: str,
    requested_value: str,
    message: str | None = None,
) -> str:
    if request_kind not in {"resolve", "search"}:
        raise ValueError("request_kind must be 'resolve' or 'search'.")
    input_name = "target_ref" if request_kind == "resolve" else "q"
    action = "/absence/resolve" if request_kind == "resolve" else "/absence/search"
    title = "Resolve Miss Explanation" if request_kind == "resolve" else "Search Miss Explanation"

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        f"    <title>Eureka {escape(title)}</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        f"      <h1>Eureka {escape(title)}</h1>",
        "      <p>Compatibility-first bounded absence reasoning over the current local corpus.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/compare\">Compare two targets</a>",
        "        <a href=\"/subject\">List subject states</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        f"        <h2>{escape(title)}</h2>",
        f"        <form method=\"get\" action=\"{escape(action, quote=True)}\">",
        f"          <label for=\"{escape(input_name, quote=True)}\">Requested value</label>",
        f"          <input id=\"{escape(input_name, quote=True)}\" name=\"{escape(input_name, quote=True)}\" type=\"text\" value=\"{escape(requested_value, quote=True)}\">",
        "          <button type=\"submit\">Explain miss</button>",
        "        </form>",
        "      </section>",
    ]

    if message is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Absence report</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    elif absence_report is not None:
        checked_source_families = _string_list(
            absence_report.get("checked_source_families"),
            "absence_report.checked_source_families",
        )
        near_matches = _mapping_list(absence_report.get("near_matches"), "absence_report.near_matches")
        next_steps = _string_list(absence_report.get("next_steps"), "absence_report.next_steps")
        notices = _mapping_list(absence_report.get("notices"), "absence_report.notices")

        parts.extend(
            [
                "      <section>",
                "        <h2>Absence report</h2>",
                "        <dl>",
                f"          <dt>Requested value</dt><dd>{escape(_require_string(absence_report.get('requested_value'), 'absence_report.requested_value'))}</dd>",
                f"          <dt>Status</dt><dd>{escape(_require_string(absence_report.get('status'), 'absence_report.status'))}</dd>",
                f"          <dt>Likely reason</dt><dd>{escape(_require_string(absence_report.get('likely_reason_code'), 'absence_report.likely_reason_code'))}</dd>",
                f"          <dt>Reason message</dt><dd>{escape(_require_string(absence_report.get('reason_message'), 'absence_report.reason_message'))}</dd>",
                f"          <dt>Checked source families</dt><dd>{escape(', '.join(checked_source_families) or '(none)')}</dd>",
                f"          <dt>Checked record count</dt><dd>{escape(str(_require_int(absence_report.get('checked_record_count'), 'absence_report.checked_record_count')))}</dd>",
                f"          <dt>Checked subject count</dt><dd>{escape(str(_require_int(absence_report.get('checked_subject_count'), 'absence_report.checked_subject_count')))}</dd>",
                "        </dl>",
                "      </section>",
                "      <section>",
                "        <h2>Near matches</h2>",
            ]
        )

        if near_matches:
            parts.append("        <ul>")
            for index, near_match in enumerate(near_matches):
                target_ref = _require_string(near_match.get("target_ref"), f"near_matches[{index}].target_ref")
                object_summary = _require_mapping(near_match.get("object"), f"near_matches[{index}].object")
                object_label = _optional_string(
                    object_summary.get("label"),
                    f"near_matches[{index}].object.label",
                ) or _require_string(object_summary.get("id"), f"near_matches[{index}].object.id")
                resolve_link = "/?target_ref=" + quote(target_ref, safe="")
                parts.extend(
                    [
                        "          <li>",
                        f"            <p><a href=\"{escape(resolve_link, quote=True)}\">{escape(object_label)}</a> <span>({escape(target_ref)})</span></p>",
                        "            <dl>",
                        f"              <dt>Match kind</dt><dd>{escape(_require_string(near_match.get('match_kind'), f'near_matches[{index}].match_kind'))}</dd>",
                        f"              <dt>Resolved resource ID</dt><dd>{escape(_require_string(near_match.get('resolved_resource_id'), f'near_matches[{index}].resolved_resource_id'))}</dd>",
                    ]
                )
                subject_key = _optional_string(near_match.get("subject_key"), f"near_matches[{index}].subject_key")
                if subject_key is not None:
                    parts.append(f"              <dt>Subject key</dt><dd>{escape(subject_key)}</dd>")
                version_or_state = _optional_string(
                    near_match.get("version_or_state"),
                    f"near_matches[{index}].version_or_state",
                )
                if version_or_state is not None:
                    parts.append(f"              <dt>Version or state</dt><dd>{escape(version_or_state)}</dd>")
                source = _optional_mapping(near_match.get("source"), f"near_matches[{index}].source")
                if source is not None:
                    parts.append(
                        f"              <dt>Source family</dt><dd>{escape(_require_string(source.get('family'), f'near_matches[{index}].source.family'))}</dd>"
                    )
                    source_label = _optional_string(source.get("label"), f"near_matches[{index}].source.label")
                    source_locator = _optional_string(
                        source.get("locator"),
                        f"near_matches[{index}].source.locator",
                    )
                    if source_label is not None:
                        parts.append(f"              <dt>Source label</dt><dd>{escape(source_label)}</dd>")
                    if source_locator is not None:
                        parts.append(f"              <dt>Source origin</dt><dd>{escape(source_locator)}</dd>")
                parts.append("            </dl>")
                evidence = _mapping_list(
                    near_match.get("evidence"),
                    f"near_matches[{index}].evidence",
                    allow_none=True,
                )
                if evidence:
                    parts.append("            <ul>")
                    for entry in evidence:
                        parts.append(f"              <li>{escape(_compact_evidence_text(entry))}</li>")
                    parts.append("            </ul>")
                parts.append("          </li>")
            parts.append("        </ul>")
        else:
            parts.append("        <p>No bounded near matches are currently available.</p>")
        parts.append("      </section>")

        parts.extend(
            [
                "      <section>",
                "        <h2>Next steps</h2>",
            ]
        )
        if next_steps:
            parts.append("        <ul>")
            for step in next_steps:
                parts.append(f"          <li>{escape(step)}</li>")
            parts.append("        </ul>")
        else:
            parts.append("        <p>No bounded next steps are currently suggested.</p>")
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
            parts.extend(["        </ul>", "      </section>"])

    parts.extend(["    </main>", "  </body>", "</html>", ""])
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


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_string(item, f"{field_name}[{index}]"))
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

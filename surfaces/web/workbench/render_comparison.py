from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_comparison_html(
    comparison: Mapping[str, Any] | None,
    *,
    left_target_ref: str,
    right_target_ref: str,
    message: str | None = None,
) -> str:
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Comparison</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Comparison</h1>",
        "      <p>Compatibility-first side-by-side comparison of two bounded resolved targets.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/subject\">List subject states</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Compare Two Targets</h2>",
        "        <form method=\"get\" action=\"/compare\">",
        "          <label for=\"left\">Left target reference</label>",
        f"          <input id=\"left\" name=\"left\" type=\"text\" value=\"{escape(left_target_ref, quote=True)}\">",
        "          <label for=\"right\">Right target reference</label>",
        f"          <input id=\"right\" name=\"right\" type=\"text\" value=\"{escape(right_target_ref, quote=True)}\">",
        "          <button type=\"submit\">Compare</button>",
        "        </form>",
        "      </section>",
    ]

    if message:
        parts.extend(
            [
                "      <section>",
                "        <h2>Comparison State</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    elif comparison is not None:
        status = _require_string(comparison.get("status"), "comparison.status")
        notices = _notice_list(comparison.get("notices"), "comparison.notices")
        agreements = _mapping_list(comparison.get("agreements"), "comparison.agreements")
        disagreements = _mapping_list(comparison.get("disagreements"), "comparison.disagreements")
        parts.extend(
            [
                "      <section>",
                "        <h2>Comparison State</h2>",
                "        <dl>",
                f"          <dt>Status</dt><dd>{escape(status)}</dd>",
                f"          <dt>Agreement count</dt><dd>{len(agreements)}</dd>",
                f"          <dt>Disagreement count</dt><dd>{len(disagreements)}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )

        parts.extend(_render_side("Left Side", comparison.get("left"), "comparison.left"))
        parts.extend(_render_side("Right Side", comparison.get("right"), "comparison.right"))

        parts.extend(
            [
                "      <section>",
                "        <h2>Agreements</h2>",
            ]
        )
        if agreements:
            parts.append("        <ul>")
            for agreement in agreements:
                parts.append(
                    "          <li>"
                    f"{escape(_require_string(agreement.get('category'), 'agreement.category'))}: "
                    f"{escape(_require_string(agreement.get('value'), 'agreement.value'))}"
                    "</li>"
                )
            parts.append("        </ul>")
        else:
            parts.append("        <p>No explicit agreements were recorded for this comparison.</p>")
        parts.append("      </section>")

        parts.extend(
            [
                "      <section>",
                "        <h2>Disagreements</h2>",
            ]
        )
        if disagreements:
            parts.append("        <ul>")
            for disagreement in disagreements:
                parts.append(
                    "          <li>"
                    f"{escape(_require_string(disagreement.get('category'), 'disagreement.category'))}: "
                    f"{escape(_require_string(disagreement.get('left_value'), 'disagreement.left_value'))} != "
                    f"{escape(_require_string(disagreement.get('right_value'), 'disagreement.right_value'))}"
                    "</li>"
                )
            parts.append("        </ul>")
        else:
            parts.append("        <p>No explicit disagreements were recorded for this comparison.</p>")
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


def _render_side(title: str, value: Any, field_name: str) -> list[str]:
    side = _require_mapping(value, field_name)
    notices = _notice_list(side.get("notices"), f"{field_name}.notices")
    evidence = _mapping_list(side.get("evidence"), f"{field_name}.evidence", allow_none=True)
    object_summary = _optional_mapping(side.get("object"), f"{field_name}.object")
    source = _optional_mapping(side.get("source"), f"{field_name}.source")
    parts = [
        "      <section>",
        f"        <h2>{escape(title)}</h2>",
        "        <dl>",
        f"          <dt>Target ref</dt><dd>{escape(_require_string(side.get('target_ref'), f'{field_name}.target_ref'))}</dd>",
        f"          <dt>Status</dt><dd>{escape(_require_string(side.get('status'), f'{field_name}.status'))}</dd>",
    ]
    resolved_resource_id = _optional_string(side.get("resolved_resource_id"), f"{field_name}.resolved_resource_id")
    if resolved_resource_id is not None:
        parts.append(f"          <dt>Resolved resource ID</dt><dd>{escape(resolved_resource_id)}</dd>")
    version_or_state = _optional_string(side.get("version_or_state"), f"{field_name}.version_or_state")
    if version_or_state is not None:
        parts.append(f"          <dt>Version or state</dt><dd>{escape(version_or_state)}</dd>")
    if object_summary is not None:
        parts.append(f"          <dt>Object ID</dt><dd>{escape(_require_string(object_summary.get('id'), f'{field_name}.object.id'))}</dd>")
        object_kind = _optional_string(object_summary.get("kind"), f"{field_name}.object.kind")
        object_label = _optional_string(object_summary.get("label"), f"{field_name}.object.label")
        if object_kind is not None:
            parts.append(f"          <dt>Object kind</dt><dd>{escape(object_kind)}</dd>")
        if object_label is not None:
            parts.append(f"          <dt>Object label</dt><dd>{escape(object_label)}</dd>")
    if source is not None:
        parts.append(f"          <dt>Source family</dt><dd>{escape(_require_string(source.get('family'), f'{field_name}.source.family'))}</dd>")
        source_label = _optional_string(source.get("label"), f"{field_name}.source.label")
        source_locator = _optional_string(source.get("locator"), f"{field_name}.source.locator")
        if source_label is not None:
            parts.append(f"          <dt>Source label</dt><dd>{escape(source_label)}</dd>")
        if source_locator is not None:
            parts.append(f"          <dt>Source origin</dt><dd>{escape(source_locator)}</dd>")
    parts.extend(
        [
            "        </dl>",
        ]
    )
    if evidence:
        parts.extend(
            [
                "        <h3>Evidence</h3>",
                "        <ul>",
            ]
        )
        for entry in evidence:
            parts.append(f"          <li>{escape(_evidence_text(entry))}</li>")
        parts.append("        </ul>")
    if notices:
        parts.extend(
            [
                "        <h3>Side Notices</h3>",
                "        <ul>",
            ]
        )
        for notice in notices:
            code = _require_string(notice.get("code"), "notice.code")
            severity = _require_string(notice.get("severity"), "notice.severity")
            message = _optional_string(notice.get("message"), "notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if message is not None:
                item += f": {escape(message)}"
            item += "</li>"
            parts.append(item)
        parts.append("        </ul>")
    parts.append("      </section>")
    return parts


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


def _notice_list(value: Any, field_name: str) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    return _mapping_list(value, field_name)


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


def _evidence_text(entry: Mapping[str, Any]) -> str:
    claim_kind = _require_string(entry.get("claim_kind"), "evidence.claim_kind")
    claim_value = _require_string(entry.get("claim_value"), "evidence.claim_value")
    asserted_by = _optional_string(entry.get("asserted_by_label"), "evidence.asserted_by_label") or _require_string(
        entry.get("asserted_by_family"),
        "evidence.asserted_by_family",
    )
    evidence_kind = _require_string(entry.get("evidence_kind"), "evidence.evidence_kind")
    evidence_locator = _require_string(entry.get("evidence_locator"), "evidence.evidence_locator")
    text = f"{claim_kind} = {claim_value} ({asserted_by}, {evidence_kind}, {evidence_locator})"
    asserted_at = _optional_string(entry.get("asserted_at"), "evidence.asserted_at")
    if asserted_at is not None:
        text += f" @ {asserted_at}"
    return text

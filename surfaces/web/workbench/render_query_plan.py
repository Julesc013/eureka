from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_query_plan_html(query_plan: Mapping[str, Any]) -> str:
    status = _require_string(query_plan.get("status"), "query_plan.status")
    plan = _optional_mapping(query_plan.get("query_plan"), "query_plan.query_plan")
    notices = _optional_notice_list(query_plan.get("notices"), "query_plan.notices")
    raw_query = ""
    if plan is not None:
        raw_query = _require_string(plan.get("raw_query"), "query_plan.query_plan.raw_query")
    else:
        raw_query = _optional_string(query_plan.get("raw_query"), "query_plan.raw_query") or ""

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Query Plan</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Query Plan</h1>",
        "      <p>Deterministic Query Planner v0 over the current bootstrap resolver lane.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/query-plan\">Plan a query</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Plan Query</h2>",
        "        <form method=\"get\" action=\"/query-plan\">",
        "          <label for=\"q\">Raw query</label>",
        f"          <input id=\"q\" name=\"q\" type=\"text\" value=\"{escape(raw_query, quote=True)}\">",
        "          <button type=\"submit\">Plan</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Planner State</h2>",
        "        <dl>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        "        </dl>",
        "      </section>",
    ]

    if plan is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Resolution Task</h2>",
                "        <dl>",
                f"          <dt>Raw query</dt><dd>{escape(plan['raw_query'])}</dd>",
                f"          <dt>Task kind</dt><dd>{escape(plan['task_kind'])}</dd>",
                f"          <dt>Object type</dt><dd>{escape(plan['object_type'])}</dd>",
                f"          <dt>Planner confidence</dt><dd>{escape(plan['planner_confidence'])}</dd>",
                f"          <dt>Constraints</dt><dd>{escape(_mapping_text(plan['constraints']))}</dd>",
                f"          <dt>Prefer</dt><dd>{escape(_list_text(plan['prefer']))}</dd>",
                f"          <dt>Exclude</dt><dd>{escape(_list_text(plan['exclude']))}</dd>",
                f"          <dt>Action hints</dt><dd>{escape(_list_text(plan['action_hints']))}</dd>",
                f"          <dt>Source hints</dt><dd>{escape(_list_text(plan['source_hints']))}</dd>",
                f"          <dt>Planner notes</dt><dd>{escape(_list_text(plan['planner_notes']))}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )

    if notices:
        parts.extend(
            [
                "      <section>",
                "        <h2>Notices</h2>",
                "        <ul>",
            ]
        )
        for notice in notices:
            message = notice.get("message", "")
            parts.append(
                "          <li>"
                f"{escape(notice['severity'])} {escape(notice['code'])}: {escape(message)}"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])

    parts.extend(
        [
            "    </main>",
            "  </body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _mapping_text(value: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key, item in value.items():
        if isinstance(item, Mapping):
            nested = ", ".join(f"{nested_key}={nested_value}" for nested_key, nested_value in item.items())
            parts.append(f"{key}({nested})")
        else:
            parts.append(f"{key}={item}")
    return "; ".join(parts) if parts else "(none)"


def _list_text(value: list[str]) -> str:
    return ", ".join(value) if value else "(none)"


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


def _optional_notice_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    notices: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        notices.append(
            {
                "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
                "severity": _require_string(item.get("severity"), f"{field_name}[{index}].severity"),
                "message": _optional_string(item.get("message"), f"{field_name}[{index}].message") or "",
            }
        )
    return notices


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)

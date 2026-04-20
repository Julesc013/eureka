from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_resolution_workspace_html(workbench_session: Mapping[str, Any]) -> str:
    active_job = _require_mapping(workbench_session.get("active_job"), "workbench_session.active_job")
    target_ref = _require_string(active_job.get("target_ref"), "workbench_session.active_job.target_ref")
    status = _require_string(active_job.get("status"), "workbench_session.active_job.status")
    job_id = _require_string(active_job.get("job_id"), "workbench_session.active_job.job_id")

    selected_object = _optional_mapping(workbench_session.get("selected_object"), "workbench_session.selected_object")
    notices = _notice_list(workbench_session.get("notices"))

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Compatibility Workbench</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Compatibility Workbench</h1>",
        "      <p>Compatibility-first resolution workspace rendered from shared gateway and session contracts.</p>",
        "      <nav>",
        "        <a href=\"/search\">Search the synthetic corpus</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Resolve a Target</h2>",
        "        <form method=\"get\" action=\"/\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <button type=\"submit\">Resolve</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Search the Corpus</h2>",
        "        <form method=\"get\" action=\"/search\">",
        "          <label for=\"q\">Bounded query</label>",
        "          <input id=\"q\" name=\"q\" type=\"text\" value=\"\">",
        "          <button type=\"submit\">Search</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Job State</h2>",
        "        <dl>",
        f"          <dt>Target ref</dt><dd>{escape(target_ref)}</dd>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Job ID</dt><dd>{escape(job_id)}</dd>",
        "        </dl>",
        "      </section>",
    ]

    if selected_object is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Object</h2>",
                "        <dl>",
                f"          <dt>ID</dt><dd>{escape(_require_string(selected_object.get('id'), 'selected_object.id'))}</dd>",
            ]
        )
        object_kind = _optional_string(selected_object.get("kind"), "selected_object.kind")
        if object_kind is not None:
            parts.append(f"          <dt>Kind</dt><dd>{escape(object_kind)}</dd>")
        object_label = _optional_string(selected_object.get("label"), "selected_object.label")
        if object_label is not None:
            parts.append(f"          <dt>Label</dt><dd>{escape(object_label)}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )
    else:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Object</h2>",
                "        <p>No selected object summary is available for this job.</p>",
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
            code = _require_string(notice.get("code"), "notice.code")
            severity = _require_string(notice.get("severity"), "notice.severity")
            message = _optional_string(notice.get("message"), "notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if message is not None:
                item += f": {escape(message)}"
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


def _notice_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("workbench_session.notices must be a list when provided.")
    notices: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"workbench_session.notices[{index}] must be an object.")
        notices.append(item)
    return notices


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

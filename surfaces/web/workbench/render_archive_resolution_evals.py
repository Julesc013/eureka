from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_archive_resolution_evals_html(
    view_model: Mapping[str, Any],
    *,
    requested_task_id: str = "",
    requested_index_path: str = "",
    allow_index_path: bool = True,
    message: str | None = None,
) -> str:
    suite = _optional_mapping(view_model.get("eval_suite"), "view_model.eval_suite")
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Archive Resolution Evals</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Archive Resolution Evals</h1>",
        "      <p>Executable v0 regression harness for hard archive-resolution fixtures.</p>",
        "      <nav>",
        "        <a href=\"/query-plan\">Compile a query plan</a>",
        "        <a href=\"/index/build\">Build local index</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Run</h2>",
        "        <form method=\"get\" action=\"/evals/archive-resolution\">",
        "          <label for=\"task-id\">Task id</label>",
        f"          <input id=\"task-id\" name=\"task_id\" type=\"text\" value=\"{escape(requested_task_id, quote=True)}\">",
    ]
    if allow_index_path:
        parts.extend(
            [
                "          <label for=\"index-path\">Index path</label>",
                f"          <input id=\"index-path\" name=\"index_path\" type=\"text\" value=\"{escape(requested_index_path, quote=True)}\">",
            ]
        )
    else:
        parts.append("          <p>Public-alpha mode uses the server-owned transient index path only.</p>")
    parts.extend(
        [
            "          <button type=\"submit\">Run evals</button>",
            "        </form>",
            "      </section>",
        ]
    )
    if message:
        parts.extend(
            [
                "      <section>",
                "        <h2>Message</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    if suite is None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Suite</h2>",
                "        <p>No eval suite result is available.</p>",
                "      </section>",
            ]
        )
    else:
        parts.extend(_render_suite(suite))
    parts.extend(
        [
            "    </main>",
            "  </body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _render_suite(suite: Mapping[str, Any]) -> list[str]:
    status_counts = _mapping_text(_require_mapping(suite.get("status_counts"), "suite.status_counts"))
    parts = [
        "      <section>",
        "        <h2>Suite Summary</h2>",
        "        <dl>",
        f"          <dt>Task count</dt><dd>{_require_int(suite.get('total_task_count'), 'suite.total_task_count')}</dd>",
        f"          <dt>Status counts</dt><dd>{escape(status_counts)}</dd>",
        f"          <dt>Created by</dt><dd>{escape(_require_string(suite.get('created_by_slice'), 'suite.created_by_slice'))}</dd>",
        "        </dl>",
        "      </section>",
    ]
    tasks = _require_list(suite.get("tasks"), "suite.tasks")
    if tasks:
        parts.extend(
            [
                "      <section>",
                "        <h2>Tasks</h2>",
                "        <table>",
                "          <thead>",
                "            <tr><th>Task</th><th>Status</th><th>Planner</th><th>Search</th><th>Results</th></tr>",
                "          </thead>",
                "          <tbody>",
            ]
        )
        for raw_task in tasks:
            task = _require_mapping(raw_task, "suite.tasks[]")
            parts.append(
                "            <tr>"
                f"<td>{escape(_require_string(task.get('task_id'), 'task.task_id'))}</td>"
                f"<td>{escape(_require_string(task.get('overall_status'), 'task.overall_status'))}</td>"
                f"<td>{escape(_require_string(task.get('planner_status'), 'task.planner_status'))}</td>"
                f"<td>{escape(_require_string(task.get('search_mode'), 'task.search_mode'))}</td>"
                f"<td>{_require_int(task.get('search_observed_result_count'), 'task.search_observed_result_count')}</td>"
                "</tr>"
            )
        parts.extend(["          </tbody>", "        </table>", "      </section>"])

    gap_items = _capability_gap_items(tasks)
    if gap_items:
        parts.extend(
            [
                "      <section>",
                "        <h2>Capability Gaps</h2>",
                "        <ul>",
            ]
        )
        for task_id, message in gap_items:
            parts.append(f"          <li><strong>{escape(task_id)}</strong>: {escape(message)}</li>")
        parts.extend(["        </ul>", "      </section>"])

    notices = _require_list(suite.get("notices"), "suite.notices")
    if notices:
        parts.extend(["      <section>", "        <h2>Notices</h2>", "        <ul>"])
        for raw_notice in notices:
            notice = _require_mapping(raw_notice, "suite.notices[]")
            parts.append(
                "          <li>"
                f"{escape(_require_string(notice.get('severity'), 'notice.severity'))} "
                f"{escape(_require_string(notice.get('code'), 'notice.code'))}: "
                f"{escape(str(notice.get('message') or ''))}"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])
    return parts


def _capability_gap_items(tasks: list[Any]) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for raw_task in tasks:
        task = _require_mapping(raw_task, "suite.tasks[]")
        gaps = _require_list(task.get("capability_gaps"), "task.capability_gaps")
        if not gaps:
            continue
        first_gap = _require_mapping(gaps[0], "task.capability_gaps[0]")
        items.append(
            (
                _require_string(task.get("task_id"), "task.task_id"),
                _require_string(first_gap.get("message"), "gap.message"),
            )
        )
    return items


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    return _require_mapping(value, field_name)


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value


def _mapping_text(value: Mapping[str, Any]) -> str:
    if not value:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in sorted(value.items()))

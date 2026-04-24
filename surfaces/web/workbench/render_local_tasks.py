from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_local_tasks_html(
    local_tasks: Mapping[str, Any],
    *,
    task_store_root: str | None = None,
    requested_index_path: str = "",
    requested_query: str = "",
    message: str | None = None,
) -> str:
    status = _require_string(local_tasks.get("status"), "local_tasks.status")
    task_count = _require_int(local_tasks.get("task_count"), "local_tasks.task_count")
    selected_task_id = _optional_string(local_tasks.get("selected_task_id"), "local_tasks.selected_task_id")
    tasks = _task_list(local_tasks.get("tasks"))
    notices = _optional_notice_list(local_tasks.get("notices"), "local_tasks.notices")
    quoted_task_store_root = escape(task_store_root or "", quote=True)

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Local Tasks</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Local Tasks</h1>",
        "      <p>Compatibility-first, synchronous local bootstrap task records for bounded backend operations.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/tasks\">List local tasks</a>",
        "        <a href=\"/runs\">List resolution runs</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Task Store</h2>",
        "        <p>Local Worker and Task Model v0 uses a caller-supplied local task_store_root for bootstrap/demo persistence only.</p>",
        "      </section>",
        "      <section>",
        "        <h2>Run Source Registry Validation</h2>",
        "        <form method=\"get\" action=\"/task/run/validate-source-registry\">",
        "          <label for=\"task_store_root_validate_sources\">Task store root</label>",
        f"          <input id=\"task_store_root_validate_sources\" name=\"task_store_root\" type=\"text\" value=\"{quoted_task_store_root}\">",
        "          <button type=\"submit\">Run task</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Run Local Index Build</h2>",
        "        <form method=\"get\" action=\"/task/run/build-local-index\">",
        "          <label for=\"task_store_root_build_index\">Task store root</label>",
        f"          <input id=\"task_store_root_build_index\" name=\"task_store_root\" type=\"text\" value=\"{quoted_task_store_root}\">",
        "          <label for=\"index_path_build\">Index path</label>",
        f"          <input id=\"index_path_build\" name=\"index_path\" type=\"text\" value=\"{escape(requested_index_path, quote=True)}\">",
        "          <button type=\"submit\">Run task</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Run Local Index Query</h2>",
        "        <form method=\"get\" action=\"/task/run/query-local-index\">",
        "          <label for=\"task_store_root_query_index\">Task store root</label>",
        f"          <input id=\"task_store_root_query_index\" name=\"task_store_root\" type=\"text\" value=\"{quoted_task_store_root}\">",
        "          <label for=\"index_path_query\">Index path</label>",
        f"          <input id=\"index_path_query\" name=\"index_path\" type=\"text\" value=\"{escape(requested_index_path, quote=True)}\">",
        "          <label for=\"index_query\">Query</label>",
        f"          <input id=\"index_query\" name=\"q\" type=\"text\" value=\"{escape(requested_query, quote=True)}\">",
        "          <button type=\"submit\">Run task</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Run Archive-Resolution Eval Validation</h2>",
        "        <form method=\"get\" action=\"/task/run/validate-archive-resolution-evals\">",
        "          <label for=\"task_store_root_validate_evals\">Task store root</label>",
        f"          <input id=\"task_store_root_validate_evals\" name=\"task_store_root\" type=\"text\" value=\"{quoted_task_store_root}\">",
        "          <button type=\"submit\">Run task</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Task State</h2>",
        "        <dl>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Task count</dt><dd>{task_count}</dd>",
        "        </dl>",
        "      </section>",
    ]

    if message:
        parts.extend(
            [
                "      <section>",
                "        <h2>Message</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )

    if tasks:
        parts.extend(["      <section>", "        <h2>Tasks</h2>", "        <ul>"])
        for task in tasks:
            link = _task_link(task["task_id"], task_store_root)
            parts.append(
                "          <li>"
                f"<a href=\"{escape(link, quote=True)}\">{escape(task['task_id'])}</a> "
                f"<span>[{escape(task['task_kind'])}]</span> "
                f"<span>{escape(task['status'])}</span> "
                f"<span>{escape(_task_summary_text(task))}</span>"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])

    selected_task = _selected_task(tasks, selected_task_id)
    if selected_task is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Task</h2>",
                "        <dl>",
                f"          <dt>Task ID</dt><dd>{escape(selected_task['task_id'])}</dd>",
                f"          <dt>Task kind</dt><dd>{escape(selected_task['task_kind'])}</dd>",
                f"          <dt>Status</dt><dd>{escape(selected_task['status'])}</dd>",
                f"          <dt>Created</dt><dd>{escape(selected_task['created_at'])}</dd>",
                f"          <dt>Started</dt><dd>{escape(selected_task.get('started_at', '(none)'))}</dd>",
                f"          <dt>Completed</dt><dd>{escape(selected_task.get('completed_at', '(none)'))}</dd>",
                f"          <dt>Requested inputs</dt><dd>{escape(_mapping_text(selected_task['requested_inputs']))}</dd>",
                f"          <dt>Created by slice</dt><dd>{escape(selected_task['created_by_slice'])}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )
        result_summary = selected_task.get("result_summary")
        if isinstance(result_summary, Mapping):
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Result Summary</h2>",
                    f"        <p>{escape(_mapping_text(result_summary))}</p>",
                    "      </section>",
                ]
            )
        error_summary = selected_task.get("error_summary")
        if isinstance(error_summary, Mapping):
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Error Summary</h2>",
                    f"        <p>{escape(_mapping_text(error_summary))}</p>",
                    "      </section>",
                ]
            )
        output_references = selected_task.get("output_references")
        if isinstance(output_references, Mapping):
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Output References</h2>",
                    f"        <p>{escape(_mapping_text(output_references))}</p>",
                    "      </section>",
                ]
            )

    if notices:
        parts.extend(["      <section>", "        <h2>Notices</h2>", "        <ul>"])
        for notice in notices:
            parts.append(
                "          <li>"
                f"{escape(notice['severity'])} {escape(notice['code'])}: "
                f"{escape(notice.get('message', ''))}"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])

    parts.extend(["    </main>", "  </body>", "</html>", ""])
    return "\n".join(parts)


def _task_link(task_id: str, task_store_root: str | None) -> str:
    link = "/task?id=" + quote(task_id, safe="")
    if task_store_root:
        link += "&task_store_root=" + quote(task_store_root, safe="")
    return link


def _task_summary_text(task: Mapping[str, Any]) -> str:
    result_summary = task.get("result_summary")
    if isinstance(result_summary, Mapping):
        result_count = result_summary.get("result_count")
        if isinstance(result_count, int):
            return f"{result_count} result(s)"
        return _mapping_text(result_summary)
    error_summary = task.get("error_summary")
    if isinstance(error_summary, Mapping):
        return _mapping_text(error_summary)
    return "no result summary"


def _selected_task(tasks: list[dict[str, Any]], selected_task_id: str | None) -> dict[str, Any] | None:
    if selected_task_id is None:
        return None
    for task in tasks:
        if task["task_id"] == selected_task_id:
            return task
    return None


def _task_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("local_tasks.tasks must be a list.")
    tasks: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"local_tasks.tasks[{index}] must be an object.")
        task = {
            "task_id": _require_string(item.get("task_id"), f"local_tasks.tasks[{index}].task_id"),
            "task_kind": _require_string(item.get("task_kind"), f"local_tasks.tasks[{index}].task_kind"),
            "status": _require_string(item.get("status"), f"local_tasks.tasks[{index}].status"),
            "requested_inputs": _require_mapping(
                item.get("requested_inputs"),
                f"local_tasks.tasks[{index}].requested_inputs",
            ),
            "created_at": _require_string(item.get("created_at"), f"local_tasks.tasks[{index}].created_at"),
            "created_by_slice": _require_string(
                item.get("created_by_slice"),
                f"local_tasks.tasks[{index}].created_by_slice",
            ),
        }
        for optional_name in ("started_at", "completed_at"):
            optional_value = item.get(optional_name)
            if optional_value is not None:
                task[optional_name] = _require_string(
                    optional_value,
                    f"local_tasks.tasks[{index}].{optional_name}",
                )
        for optional_name in ("result_summary", "error_summary", "output_references"):
            optional_value = item.get(optional_name)
            if optional_value is not None:
                task[optional_name] = _require_mapping(
                    optional_value,
                    f"local_tasks.tasks[{index}].{optional_name}",
                )
        notices = item.get("notices")
        if notices is not None:
            task["notices"] = _optional_notice_list(
                notices,
                f"local_tasks.tasks[{index}].notices",
            )
        tasks.append(task)
    return tasks


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


def _mapping_text(value: Mapping[str, Any]) -> str:
    if not value:
        return "(none)"
    parts: list[str] = []
    for key, item in value.items():
        if isinstance(item, Mapping):
            nested = ", ".join(f"{nested_key}={nested_value}" for nested_key, nested_value in item.items())
            parts.append(f"{key}({nested})")
        elif isinstance(item, list):
            parts.append(f"{key}=[{', '.join(str(member) for member in item)}]")
        else:
            parts.append(f"{key}={item}")
    return "; ".join(parts)


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

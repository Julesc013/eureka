from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_resolution_runs_html(
    resolution_runs: Mapping[str, Any],
    *,
    run_store_root: str | None = None,
    requested_target_ref: str = "",
    requested_query: str = "",
    message: str | None = None,
) -> str:
    status = _require_string(resolution_runs.get("status"), "resolution_runs.status")
    run_count = _require_int(resolution_runs.get("run_count"), "resolution_runs.run_count")
    selected_run_id = _optional_string(
        resolution_runs.get("selected_run_id"),
        "resolution_runs.selected_run_id",
    )
    runs = _run_list(resolution_runs.get("runs"))
    notices = _optional_notice_list(resolution_runs.get("notices"), "resolution_runs.notices")
    quoted_run_store_root = escape(run_store_root or "", quote=True)

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Resolution Runs</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Resolution Runs</h1>",
        "      <p>Compatibility-first, synchronous local investigation records for the current bootstrap resolver lane.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/runs\">List runs</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Run Store</h2>",
        "        <p>Resolution Run Model v0 uses a caller-supplied local run_store_root for bootstrap/demo persistence only.</p>",
        "      </section>",
        "      <section>",
        "        <h2>Start Exact Resolution Run</h2>",
        "        <form method=\"get\" action=\"/run/resolve\">",
        "          <label for=\"run_store_root_resolve\">Run store root</label>",
        f"          <input id=\"run_store_root_resolve\" name=\"run_store_root\" type=\"text\" value=\"{quoted_run_store_root}\">",
        "          <label for=\"target_ref\">Target ref</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(requested_target_ref, quote=True)}\">",
        "          <button type=\"submit\">Start run</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Start Deterministic Search Run</h2>",
        "        <form method=\"get\" action=\"/run/search\">",
        "          <label for=\"run_store_root_search\">Run store root</label>",
        f"          <input id=\"run_store_root_search\" name=\"run_store_root\" type=\"text\" value=\"{quoted_run_store_root}\">",
        "          <label for=\"q\">Query</label>",
        f"          <input id=\"q\" name=\"q\" type=\"text\" value=\"{escape(requested_query, quote=True)}\">",
        "          <button type=\"submit\">Start run</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Run State</h2>",
        "        <dl>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Run count</dt><dd>{run_count}</dd>",
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

    if runs:
        parts.extend(
            [
                "      <section>",
                "        <h2>Runs</h2>",
                "        <ul>",
            ]
        )
        for run in runs:
            link = _run_link(run["run_id"], run_store_root)
            summary_text = _run_summary_text(run)
            parts.append(
                "          <li>"
                f"<a href=\"{escape(link, quote=True)}\">{escape(run['run_id'])}</a> "
                f"<span>[{escape(run['run_kind'])}]</span> "
                f"<span>{escape(run['status'])}</span> "
                f"<span>{escape(summary_text)}</span>"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])

    selected_run = _selected_run(runs, selected_run_id)
    if selected_run is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Run</h2>",
                "        <dl>",
                f"          <dt>Run ID</dt><dd>{escape(selected_run['run_id'])}</dd>",
                f"          <dt>Run kind</dt><dd>{escape(selected_run['run_kind'])}</dd>",
                f"          <dt>Requested value</dt><dd>{escape(selected_run['requested_value'])}</dd>",
                f"          <dt>Status</dt><dd>{escape(selected_run['status'])}</dd>",
                f"          <dt>Started</dt><dd>{escape(selected_run['started_at'])}</dd>",
                f"          <dt>Completed</dt><dd>{escape(selected_run['completed_at'])}</dd>",
                f"          <dt>Checked source IDs</dt><dd>{escape(', '.join(selected_run['checked_source_ids']) or '(none)')}</dd>",
                f"          <dt>Checked source families</dt><dd>{escape(', '.join(selected_run['checked_source_families']) or '(none)')}</dd>",
                f"          <dt>Checked sources</dt><dd>{escape(_checked_sources_text(selected_run['checked_sources']))}</dd>",
                f"          <dt>Created by slice</dt><dd>{escape(selected_run['created_by_slice'])}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )
        result_summary = selected_run.get("result_summary")
        if isinstance(result_summary, Mapping):
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Result Summary</h2>",
                    "        <dl>",
                    f"          <dt>Result kind</dt><dd>{escape(str(result_summary.get('result_kind', '(unknown)')))}</dd>",
                    f"          <dt>Result count</dt><dd>{escape(str(result_summary.get('result_count', 0)))}</dd>",
                    "        </dl>",
                    "        <ul>",
                ]
            )
            items = result_summary.get("items")
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, Mapping):
                        continue
                    object_summary = item.get("object", {})
                    label = "(unknown)"
                    if isinstance(object_summary, Mapping):
                        label = str(object_summary.get("label") or object_summary.get("id") or "(unknown)")
                    parts.append(
                        "          <li>"
                        f"{escape(label)} "
                        f"<span>{escape(str(item.get('target_ref', '(unknown)')))}</span>"
                        "</li>"
                    )
            parts.extend(["        </ul>", "      </section>"])
        absence_report = selected_run.get("absence_report")
        if isinstance(absence_report, Mapping):
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Absence Report</h2>",
                    "        <dl>",
                    f"          <dt>Request kind</dt><dd>{escape(str(absence_report.get('request_kind', '(unknown)')))}</dd>",
                    f"          <dt>Likely reason</dt><dd>{escape(str(absence_report.get('likely_reason_code', '(unknown)')))}</dd>",
                    f"          <dt>Reason message</dt><dd>{escape(str(absence_report.get('reason_message', '(unknown)')))}</dd>",
                    f"          <dt>Checked source families</dt><dd>{escape(', '.join(_string_list(absence_report.get('checked_source_families'))))}</dd>",
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
            message_text = notice.get("message", "")
            parts.append(
                "          <li>"
                f"{escape(notice['severity'])} {escape(notice['code'])}: {escape(message_text)}"
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


def _run_link(run_id: str, run_store_root: str | None) -> str:
    link = "/run?id=" + quote(run_id, safe="")
    if run_store_root:
        link += "&run_store_root=" + quote(run_store_root, safe="")
    return link


def _run_summary_text(run: Mapping[str, Any]) -> str:
    result_summary = run.get("result_summary")
    if isinstance(result_summary, Mapping):
        return f"{result_summary.get('result_count', 0)} result(s)"
    absence_report = run.get("absence_report")
    if isinstance(absence_report, Mapping):
        return str(absence_report.get("likely_reason_code", "absence_recorded"))
    return "no result summary"


def _selected_run(runs: list[dict[str, Any]], selected_run_id: str | None) -> dict[str, Any] | None:
    if selected_run_id is None:
        return None
    for run in runs:
        if run["run_id"] == selected_run_id:
            return run
    return None


def _run_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("resolution_runs.runs must be a list.")
    runs: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"resolution_runs.runs[{index}] must be an object.")
        runs.append(_run_entry(item, f"resolution_runs.runs[{index}]"))
    return runs


def _run_entry(value: Mapping[str, Any], field_name: str) -> dict[str, Any]:
    run = {
        "run_id": _require_string(value.get("run_id"), f"{field_name}.run_id"),
        "run_kind": _require_string(value.get("run_kind"), f"{field_name}.run_kind"),
        "requested_value": _require_string(value.get("requested_value"), f"{field_name}.requested_value"),
        "status": _require_string(value.get("status"), f"{field_name}.status"),
        "started_at": _require_string(value.get("started_at"), f"{field_name}.started_at"),
        "completed_at": _require_string(value.get("completed_at"), f"{field_name}.completed_at"),
        "checked_source_ids": _string_list(value.get("checked_source_ids")),
        "checked_source_families": _string_list(value.get("checked_source_families")),
        "checked_sources": _checked_sources(value.get("checked_sources"), f"{field_name}.checked_sources"),
        "created_by_slice": _require_string(value.get("created_by_slice"), f"{field_name}.created_by_slice"),
    }
    result_summary = value.get("result_summary")
    if result_summary is not None:
        run["result_summary"] = _require_mapping(result_summary, f"{field_name}.result_summary")
    absence_report = value.get("absence_report")
    if absence_report is not None:
        run["absence_report"] = _require_mapping(absence_report, f"{field_name}.absence_report")
    notices = value.get("notices")
    if notices is not None:
        run["notices"] = _optional_notice_list(notices, f"{field_name}.notices")
    return run


def _checked_sources(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    sources: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        sources.append(
            {
                "source_id": _require_string(item.get("source_id"), f"{field_name}[{index}].source_id"),
                "name": _require_string(item.get("name"), f"{field_name}[{index}].name"),
                "source_family": _require_string(
                    item.get("source_family"),
                    f"{field_name}[{index}].source_family",
                ),
                "status": _require_string(item.get("status"), f"{field_name}[{index}].status"),
                "trust_lane": _require_string(
                    item.get("trust_lane"),
                    f"{field_name}[{index}].trust_lane",
                ),
            }
        )
    return sources


def _checked_sources_text(value: list[dict[str, str]]) -> str:
    if not value:
        return "(none)"
    return ", ".join(f"{entry['name']} [{entry['status']}]" for entry in value)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("expected a list of strings.")
    values: list[str] = []
    for index, item in enumerate(value):
        values.append(_require_string(item, f"string_list[{index}]"))
    return values


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

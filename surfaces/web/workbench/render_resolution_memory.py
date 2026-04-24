from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_resolution_memory_html(
    resolution_memory: Mapping[str, Any],
    *,
    memory_store_root: str | None = None,
    run_store_root: str | None = None,
    requested_run_id: str = "",
    message: str | None = None,
) -> str:
    status = _require_string(resolution_memory.get("status"), "resolution_memory.status")
    memory_count = _require_int(resolution_memory.get("memory_count"), "resolution_memory.memory_count")
    selected_memory_id = _optional_string(
        resolution_memory.get("selected_memory_id"),
        "resolution_memory.selected_memory_id",
    )
    memories = _memory_list(resolution_memory.get("memories"))
    notices = _optional_notice_list(resolution_memory.get("notices"), "resolution_memory.notices")
    quoted_memory_store_root = escape(memory_store_root or "", quote=True)
    quoted_run_store_root = escape(run_store_root or "", quote=True)

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Resolution Memory</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Resolution Memory</h1>",
        "      <p>Compatibility-first, explicit local memory records derived from existing persisted runs.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/runs\">List runs</a>",
        "        <a href=\"/memories\">List memories</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Memory Store</h2>",
        "        <p>Resolution Memory v0 uses a caller-supplied local memory_store_root for bootstrap/demo persistence only.</p>",
        "      </section>",
        "      <section>",
        "        <h2>Create Memory from Run</h2>",
        "        <form method=\"get\" action=\"/memory/create\">",
        "          <label for=\"memory_store_root_create\">Memory store root</label>",
        f"          <input id=\"memory_store_root_create\" name=\"memory_store_root\" type=\"text\" value=\"{quoted_memory_store_root}\">",
        "          <label for=\"run_store_root_create\">Run store root</label>",
        f"          <input id=\"run_store_root_create\" name=\"run_store_root\" type=\"text\" value=\"{quoted_run_store_root}\">",
        "          <label for=\"run_id\">Run ID</label>",
        f"          <input id=\"run_id\" name=\"run_id\" type=\"text\" value=\"{escape(requested_run_id, quote=True)}\">",
        "          <button type=\"submit\">Create memory</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Memory State</h2>",
        "        <dl>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Memory count</dt><dd>{memory_count}</dd>",
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

    if memories:
        parts.extend(["      <section>", "        <h2>Memories</h2>", "        <ul>"])
        for memory in memories:
            link = _memory_link(memory["memory_id"], memory_store_root)
            parts.append(
                "          <li>"
                f"<a href=\"{escape(link, quote=True)}\">{escape(memory['memory_id'])}</a> "
                f"<span>[{escape(memory['memory_kind'])}]</span> "
                f"<span>{escape(memory['source_run_id'])}</span>"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])

    selected_memory = _selected_memory(memories, selected_memory_id)
    if selected_memory is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Memory</h2>",
                "        <dl>",
                f"          <dt>Memory ID</dt><dd>{escape(selected_memory['memory_id'])}</dd>",
                f"          <dt>Memory kind</dt><dd>{escape(selected_memory['memory_kind'])}</dd>",
                f"          <dt>Source run ID</dt><dd>{escape(selected_memory['source_run_id'])}</dd>",
                f"          <dt>Created</dt><dd>{escape(selected_memory['created_at'])}</dd>",
                f"          <dt>Raw query</dt><dd>{escape(selected_memory.get('raw_query', '(none)'))}</dd>",
                f"          <dt>Task kind</dt><dd>{escape(selected_memory.get('task_kind', '(none)'))}</dd>",
                f"          <dt>Requested value</dt><dd>{escape(selected_memory.get('requested_value', '(none)'))}</dd>",
                f"          <dt>Checked source IDs</dt><dd>{escape(', '.join(selected_memory['checked_source_ids']) or '(none)')}</dd>",
                f"          <dt>Useful source IDs</dt><dd>{escape(', '.join(selected_memory['useful_source_ids']) or '(none)')}</dd>",
                f"          <dt>Primary resolved resource ID</dt><dd>{escape(selected_memory.get('primary_resolved_resource_id', '(none)'))}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )
        result_summaries = selected_memory.get("result_summaries")
        if isinstance(result_summaries, list) and result_summaries:
            parts.extend(["      <section>", "        <h2>Result Summaries</h2>", "        <ul>"])
            for item in result_summaries:
                if not isinstance(item, Mapping):
                    continue
                object_summary = item.get("object", {})
                label = "(unknown)"
                if isinstance(object_summary, Mapping):
                    label = str(object_summary.get("label") or object_summary.get("id") or "(unknown)")
                parts.append(
                    "          <li>"
                    f"{escape(label)} <span>{escape(str(item.get('target_ref', '(unknown)')))}</span>"
                    "</li>"
                )
            parts.extend(["        </ul>", "      </section>"])
        absence_report = selected_memory.get("absence_report")
        if isinstance(absence_report, Mapping):
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Absence Report</h2>",
                    "        <dl>",
                    f"          <dt>Request kind</dt><dd>{escape(str(absence_report.get('request_kind', '(unknown)')))}</dd>",
                    f"          <dt>Likely reason</dt><dd>{escape(str(absence_report.get('likely_reason_code', '(unknown)')))}</dd>",
                    f"          <dt>Reason message</dt><dd>{escape(str(absence_report.get('reason_message', '(unknown)')))}</dd>",
                    "        </dl>",
                    "      </section>",
                ]
            )
        evidence_summary = selected_memory.get("evidence_summary")
        if isinstance(evidence_summary, list) and evidence_summary:
            parts.extend(["      <section>", "        <h2>Evidence Summary</h2>", "        <ul>"])
            for item in evidence_summary:
                if not isinstance(item, Mapping):
                    continue
                parts.append(
                    "          <li>"
                    f"{escape(str(item.get('claim_kind', '(unknown)')))}="
                    f"{escape(str(item.get('claim_value', '(unknown)')))}"
                    "</li>"
                )
            parts.extend(["        </ul>", "      </section>"])
        invalidation_hints = selected_memory.get("invalidation_hints")
        if isinstance(invalidation_hints, Mapping):
            parts.extend(
                [
                    "      <section>",
                    "        <h2>Invalidation Hints</h2>",
                    f"        <p>{escape(_mapping_text(invalidation_hints))}</p>",
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


def _memory_link(memory_id: str, memory_store_root: str | None) -> str:
    link = "/memory?id=" + quote(memory_id, safe="")
    if memory_store_root:
        link += "&memory_store_root=" + quote(memory_store_root, safe="")
    return link


def _selected_memory(memories: list[dict[str, Any]], selected_memory_id: str | None) -> dict[str, Any] | None:
    if selected_memory_id is None:
        return None
    for memory in memories:
        if memory["memory_id"] == selected_memory_id:
            return memory
    return None


def _memory_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("resolution_memory.memories must be a list.")
    memories: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"resolution_memory.memories[{index}] must be an object.")
        memory = {
            "memory_id": _require_string(item.get("memory_id"), f"resolution_memory.memories[{index}].memory_id"),
            "memory_kind": _require_string(item.get("memory_kind"), f"resolution_memory.memories[{index}].memory_kind"),
            "source_run_id": _require_string(item.get("source_run_id"), f"resolution_memory.memories[{index}].source_run_id"),
            "created_at": _require_string(item.get("created_at"), f"resolution_memory.memories[{index}].created_at"),
            "checked_source_ids": _string_list(item.get("checked_source_ids")),
            "useful_source_ids": _string_list(item.get("useful_source_ids")),
        }
        for optional_name in (
            "raw_query",
            "task_kind",
            "requested_value",
            "primary_resolved_resource_id",
        ):
            optional_value = item.get(optional_name)
            if optional_value is not None:
                memory[optional_name] = _require_string(
                    optional_value,
                    f"resolution_memory.memories[{index}].{optional_name}",
                )
        for optional_name in (
            "checked_sources",
            "result_summaries",
            "evidence_summary",
            "absence_report",
            "invalidation_hints",
        ):
            optional_value = item.get(optional_name)
            if optional_value is not None:
                memory[optional_name] = optional_value
        memories.append(memory)
    return memories


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


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value

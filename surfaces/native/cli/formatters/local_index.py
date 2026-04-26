from __future__ import annotations

from typing import Any, Mapping


def format_local_index(local_index: Mapping[str, Any]) -> str:
    lines = [
        "Local index",
        f"status: {local_index.get('status', '(unknown)')}",
    ]
    index_metadata = local_index.get("index")
    if isinstance(index_metadata, Mapping):
        lines.extend(
            [
                "",
                "Index",
                f"path_kind: {index_metadata.get('index_path_kind', '(unknown)')}",
                f"path: {index_metadata.get('index_path', '(not reported)')}",
                f"fts_mode: {index_metadata.get('fts_mode', '(unknown)')}",
                f"record_count: {index_metadata.get('record_count', 0)}",
                f"record_kind_counts: {_mapping_text(index_metadata.get('record_kind_counts'))}",
            ]
        )
    query = local_index.get("query")
    if isinstance(query, str):
        lines.append(f"query: {query}")
    if isinstance(local_index.get("result_count"), int):
        lines.append(f"result_count: {local_index['result_count']}")

    results = local_index.get("results")
    if isinstance(results, list) and results:
        lines.extend(["", "Results"])
        for result in results:
            if not isinstance(result, Mapping):
                continue
            lines.append(
                f"- {result.get('record_kind', '(unknown)')}: {result.get('label', '(unknown)')}"
            )
            for field_name in (
                "target_ref",
                "resolved_resource_id",
                "source_id",
                "source_family",
                "representation_id",
                "member_path",
                "parent_target_ref",
                "parent_representation_id",
                "member_kind",
                "media_type",
                "content_hash",
                "summary",
            ):
                value = result.get(field_name)
                if isinstance(value, str) and value:
                    lines.append(f"  {field_name}: {value}")
            size_bytes = result.get("size_bytes")
            if isinstance(size_bytes, int):
                lines.append(f"  size_bytes: {size_bytes}")
            action_hints = result.get("action_hints")
            if isinstance(action_hints, list) and action_hints:
                lines.append(f"  action_hints: {', '.join(str(item) for item in action_hints)}")
    notices = local_index.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        for notice in notices:
            if not isinstance(notice, Mapping):
                continue
            line = f"- {notice.get('severity', '(unknown)')} {notice.get('code', '(unknown)')}"
            message = notice.get("message")
            if isinstance(message, str) and message:
                line += f": {message}"
            lines.append(line)
    return "\n".join(lines) + "\n"


def _mapping_text(value: Any) -> str:
    if not isinstance(value, Mapping) or not value:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in value.items())

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
            compatibility_summary = result.get("compatibility_summary")
            if isinstance(compatibility_summary, str) and compatibility_summary:
                lines.append(f"  compatibility: {compatibility_summary}")
            compatibility_evidence = result.get("compatibility_evidence")
            if isinstance(compatibility_evidence, list) and compatibility_evidence:
                lines.append(f"  compatibility_evidence: {_compact_compatibility_evidence(compatibility_evidence[0])}")
            primary_lane = result.get("primary_lane")
            if isinstance(primary_lane, str) and primary_lane:
                lines.append(f"  lane: {primary_lane}")
            user_cost_score = result.get("user_cost_score")
            if isinstance(user_cost_score, int):
                lines.append(f"  user_cost: {user_cost_score}")
            user_cost_reasons = result.get("user_cost_reasons")
            if isinstance(user_cost_reasons, list) and user_cost_reasons:
                lines.append(f"  why: {', '.join(str(item) for item in user_cost_reasons)}")
            usefulness_summary = result.get("usefulness_summary")
            if isinstance(usefulness_summary, str) and usefulness_summary:
                lines.append(f"  usefulness: {usefulness_summary}")
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


def _compact_compatibility_evidence(value: Any) -> str:
    if not isinstance(value, Mapping):
        return "(unknown)"
    platform = value.get("platform")
    platform_name = "(unknown platform)"
    if isinstance(platform, Mapping):
        platform_name = str(platform.get("name") or platform.get("marketing_alias") or platform_name)
    return (
        f"{platform_name} {value.get('claim_type', '(unknown claim)')} "
        f"via {value.get('evidence_kind', '(unknown evidence)')}"
    )

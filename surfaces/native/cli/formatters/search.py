from __future__ import annotations

from typing import Any, Mapping


def format_search_results(search_results: Mapping[str, Any]) -> str:
    lines = [
        "Search",
        f"query: {search_results.get('query', '')}",
        f"result_count: {search_results.get('result_count', 0)}",
    ]
    results = search_results.get("results", [])
    if isinstance(results, list) and results:
        lines.extend(["", "Results"])
        for index, result in enumerate(results, start=1):
            object_summary = result.get("object", {})
            label = object_summary.get("label") or object_summary.get("id") or "(unknown)"
            lines.append(f"{index}. {label}")
            lines.append(f"   target_ref: {result.get('target_ref', '(unknown)')}")
            lines.append(f"   object_id: {object_summary.get('id', '(unknown)')}")
            if object_summary.get("kind"):
                lines.append(f"   object_kind: {object_summary['kind']}")
            for field_name in (
                "record_kind",
                "member_path",
                "member_kind",
                "parent_target_ref",
                "parent_representation_id",
                "media_type",
                "content_hash",
            ):
                value = object_summary.get(field_name)
                if isinstance(value, str) and value:
                    lines.append(f"   {field_name}: {value}")
            size_bytes = object_summary.get("size_bytes")
            if isinstance(size_bytes, int):
                lines.append(f"   size_bytes: {size_bytes}")
            action_hints = object_summary.get("action_hints")
            if isinstance(action_hints, list) and action_hints:
                lines.append(f"   action_hints: {', '.join(str(item) for item in action_hints)}")
            primary_lane = result.get("primary_lane") or object_summary.get("primary_lane")
            if isinstance(primary_lane, str) and primary_lane:
                lines.append(f"   lane: {primary_lane}")
            user_cost_score = result.get("user_cost_score")
            if not isinstance(user_cost_score, int):
                user_cost_score = object_summary.get("user_cost_score")
            if isinstance(user_cost_score, int):
                lines.append(f"   user_cost: {user_cost_score}")
            user_cost_reasons = result.get("user_cost_reasons") or object_summary.get("user_cost_reasons")
            if isinstance(user_cost_reasons, list) and user_cost_reasons:
                lines.append(f"   why: {', '.join(str(item) for item in user_cost_reasons)}")
            usefulness_summary = result.get("usefulness_summary") or object_summary.get("usefulness_summary")
            if isinstance(usefulness_summary, str) and usefulness_summary:
                lines.append(f"   usefulness: {usefulness_summary}")
            source = result.get("source")
            if isinstance(source, Mapping):
                source_label = source.get("label") or source.get("family")
                if source_label:
                    lines.append(f"   source: {source_label}")
            evidence = result.get("evidence")
            if isinstance(evidence, list) and evidence:
                lines.append(f"   evidence: {_compact_evidence_entry(evidence[0])}")
            resolved_resource_id = result.get("resolved_resource_id")
            if isinstance(resolved_resource_id, str) and resolved_resource_id:
                lines.append(f"   resolved_resource_id: {resolved_resource_id}")
    else:
        absence = search_results.get("absence")
        if isinstance(absence, Mapping):
            lines.extend(
                [
                    "",
                    "No results",
                    f"code: {absence.get('code', '(unknown)')}",
                    f"message: {absence.get('message', '(unknown)')}",
                ]
            )

    return "\n".join(lines) + "\n"


def _compact_evidence_entry(entry: Any) -> str:
    if not isinstance(entry, Mapping):
        return "(unknown)"
    claim_kind = entry.get("claim_kind", "(unknown)")
    asserted_by = entry.get("asserted_by_label") or entry.get("asserted_by_family") or "(unknown)"
    return f"{claim_kind} via {asserted_by}"

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

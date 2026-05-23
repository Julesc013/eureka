"""Reviewed-index-only search summaries for local Search Hunt sessions."""

from typing import Any

from .records import normalize_query, utc_now
from .validation import validate_query_text


def build_reviewed_index_search_summary(runtime: Any, query: str, limit: int = 20) -> dict[str, Any]:
    text = validate_query_text(query)
    results = runtime.public_index.search(text, limit=limit)
    result_payloads = [item.to_dict() if hasattr(item, "to_dict") else dict(item) for item in results]
    index_summary = runtime.public_index.summarize().to_dict()
    return {
        "schema_version": "search_hunt_reviewed_index_search_summary.v0",
        "query": text,
        "normalized_query": normalize_query(text),
        "created_at": utc_now(),
        "layer": "reviewed_public_index",
        "reviewed_index_only": True,
        "current_index_only": True,
        "result_count": len(result_payloads),
        "limit": int(limit),
        "results": result_payloads,
        "index_summary": index_summary,
        "limitations": [
            "local reviewed public index only",
            "no live source inspection",
            "no background work scheduled",
        ],
        "warnings": [],
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
    }

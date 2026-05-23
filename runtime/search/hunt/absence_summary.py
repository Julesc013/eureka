"""Local absence summaries for Search Hunt sessions."""

from typing import Any

from .records import SearchHuntUncheckedLayer, normalize_query, utc_now
from .validation import validate_query_text


def build_local_absence_summary(runtime: Any, query: str) -> dict[str, Any]:
    text = validate_query_text(query)
    absence = runtime.public_index.absence_report(text).to_dict()
    return {
        "schema_version": "search_hunt_local_absence_summary.v0",
        "query": text,
        "normalized_query": normalize_query(text),
        "created_at": utc_now(),
        "layer": "local_absence_report",
        "local_current_index_absence_only": True,
        "absence": absence,
        "unchecked_layers": [item.value for item in SearchHuntUncheckedLayer],
        "limitations": [
            "absence is limited to the current local reviewed index",
            "unchecked layers were not inspected",
            "source probes, extraction, broader connectors, synthetic query generation, and AI escalation are deferred",
        ],
        "warnings": [],
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
    }

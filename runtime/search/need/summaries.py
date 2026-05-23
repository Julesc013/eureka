"""SearchNeed summary helpers."""

from typing import Any

from .records import SearchNeed


def build_search_need_summary(need: SearchNeed) -> dict[str, Any]:
    return {
        "schema_version": "search_need_summary.v0",
        "id": need.id,
        "hunt_id": need.hunt_id,
        "exhaustion_report_id": need.exhaustion_report_id,
        "query": need.query,
        "normalized_query": need.normalized_query,
        "need_title": need.need_title,
        "need_kind": need.need_kind.value,
        "desired_outcome": need.desired_outcome.value,
        "state": need.state.value,
        "priority": need.priority,
        "local_result_state": need.local_result_state,
        "recommended_future_work_count": len(need.recommended_future_work),
        "workunit_creation_enabled": False,
        "source_probe_execution_enabled": False,
        "model_provider_enabled": False,
    }

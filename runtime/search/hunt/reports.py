"""Report serialization helpers for Search Hunt records."""

from typing import Any, Mapping

from .records import SearchHuntExhaustionReport


def exhaustion_report_payload(report: SearchHuntExhaustionReport | Mapping[str, Any] | None) -> dict[str, Any]:
    if report is None:
        return {}
    if isinstance(report, SearchHuntExhaustionReport):
        return report.to_dict()
    return dict(report)


def exhaustion_response_payload(
    hunt_id: str,
    report: SearchHuntExhaustionReport | Mapping[str, Any] | None,
    *,
    status: str = "pass",
) -> dict[str, Any]:
    return {
        "schema_version": "search_hunt_exhaustion_response.v0",
        "status": status,
        "hunt_id": hunt_id,
        "exhaustion_report": exhaustion_report_payload(report),
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }

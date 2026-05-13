"""Read-only routes over the local appliance runtime."""

from typing import Any

from .request_context import LocalRequestContext
from .responses import DEFAULT_LIMITATIONS, LocalServiceResponse, error_response, json_response, text_response
from .validation import first_param, parse_limit


def route_request(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    method = request_context.method
    path = request_context.path
    if method != "GET":
        return error_response(405, "method_not_allowed", "only GET is enabled for the read-only local service")
    if path == "/":
        return _root_response()
    if path in {"/status", "/api/v1/status"}:
        return _status_response(runtime)
    if path in {"/health", "/api/v1/health"}:
        return _health_response(runtime)
    if path == "/api/v1/search":
        return _search_response(runtime, request_context)
    if path.startswith("/api/v1/object/"):
        return _object_response(runtime, path.removeprefix("/api/v1/object/"))
    if path.startswith("/api/v1/source/"):
        return _source_response(runtime, path.removeprefix("/api/v1/source/"), request_context)
    if path == "/api/v1/absence":
        return _absence_response(runtime, request_context)
    return error_response(404, "route_not_found", "local service route was not found", {"path": path})


def _root_response() -> LocalServiceResponse:
    return text_response(
        200,
        "Eureka Local Appliance Service\nRead-only localhost JSON API.\n",
        {"Content-Type": "text/plain; charset=utf-8"},
    )


def _status_response(runtime: Any) -> LocalServiceResponse:
    runtime_status = runtime.status().to_dict()
    summary = runtime.public_index.summarize().to_dict()
    payload = {
        "schema_version": "local_http_status_response.v0",
        "status": runtime_status.get("status", "pass"),
        "service": {
            "read_only": True,
            "localhost_only": True,
            "write_routes_enabled": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "source_probe_execution_enabled": False,
            "workunit_execution_enabled": False,
            "review_decision_mutation_enabled": False,
            "index_rebuild_enabled": False,
        },
        "runtime": runtime_status,
        "public_index": summary,
        "warnings": list(runtime_status.get("warnings", [])),
        "limitations": list(DEFAULT_LIMITATIONS),
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    return json_response(200, payload)


def _health_response(runtime: Any) -> LocalServiceResponse:
    status = runtime.status().to_dict()
    payload = {
        "schema_version": "local_http_health_response.v0",
        "status": "pass" if status.get("status") == "pass" else "fail",
        "read_only": True,
        "localhost_only": True,
        "lan_enabled": False,
        "deployment_performed": False,
        "warnings": list(status.get("warnings", [])),
        "limitations": list(DEFAULT_LIMITATIONS),
    }
    return json_response(200 if payload["status"] == "pass" else 503, payload)


def _search_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    limit = parse_limit(first_param(request_context.params, "limit", ""))
    results = [item.to_dict() for item in runtime.public_index.search(query, limit=limit)]
    payload = {
        "schema_version": "local_http_search_response.v0",
        "status": "pass",
        "query": query,
        "limit": limit,
        "result_count": len(results),
        "results": results,
        "reviewed_public_index_only": True,
        "warnings": [] if query else ["empty query returns no results"],
        "limitations": list(DEFAULT_LIMITATIONS),
    }
    return json_response(200, payload)


def _object_response(runtime: Any, record_id: str) -> LocalServiceResponse:
    if not record_id:
        return error_response(400, "missing_record_id", "record_id is required")
    record = runtime.public_index.get_record(record_id)
    if record is None:
        return error_response(404, "record_not_found", "record was not found in the reviewed public index", {"record_id": record_id})
    payload = {
        "schema_version": "local_http_object_response.v0",
        "status": "pass",
        "record_id": record_id,
        "record": record.to_dict(),
        "warnings": list(record.warnings),
        "limitations": list(DEFAULT_LIMITATIONS) + list(record.limitations),
    }
    return json_response(200, payload)


def _source_response(runtime: Any, source_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    if not source_id:
        return error_response(400, "missing_source_id", "source_id is required")
    limit = parse_limit(first_param(request_context.params, "limit", ""))
    records = [item.to_dict() for item in runtime.public_index.list_records(source_id=source_id, limit=limit)]
    payload = {
        "schema_version": "local_http_source_response.v0",
        "status": "pass",
        "source_id": source_id,
        "limit": limit,
        "result_count": len(records),
        "records": records,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS)
        + ["empty result does not prove the source lacks matching records"],
    }
    return json_response(200, payload)


def _absence_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    report = runtime.public_index.absence_report(query).to_dict()
    payload = {
        "schema_version": "local_http_absence_response.v0",
        "status": "pass",
        "absence": report,
        "warnings": list(report.get("warnings", [])),
        "limitations": list(DEFAULT_LIMITATIONS) + list(report.get("limitations", [])),
    }
    return json_response(200, payload)

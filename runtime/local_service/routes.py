"""Routes over the local appliance runtime."""

from typing import Any

from .request_context import LocalRequestContext
from .responses import DEFAULT_LIMITATIONS, LocalServiceResponse, error_response, html_response, json_response
from .validation import first_param, parse_limit


def route_request(
    runtime: Any,
    request_context: LocalRequestContext,
    operator_auth_state: Any = None,
) -> LocalServiceResponse:
    method = request_context.method
    path = request_context.path
    if method != "GET":
        return _mutation_response(runtime, request_context, operator_auth_state)
    if path == "/":
        return _home_response(runtime)
    if path == "/status":
        if _wants_json(request_context):
            return _status_response(runtime)
        return _status_html_response(runtime)
    if path == "/api/v1/status":
        return _status_response(runtime)
    if path in {"/health", "/api/v1/health"}:
        return _health_response(runtime)
    if path == "/search":
        if _wants_json(request_context):
            return _search_response(runtime, request_context)
        return _search_html_response(runtime, request_context)
    if path == "/api/v1/search":
        return _search_response(runtime, request_context)
    if path.startswith("/object/"):
        record_id = path.removeprefix("/object/")
        if _wants_json(request_context):
            return _object_response(runtime, record_id)
        return _object_html_response(runtime, record_id)
    if path.startswith("/api/v1/object/"):
        return _object_response(runtime, path.removeprefix("/api/v1/object/"))
    if path.startswith("/source/"):
        source_id = path.removeprefix("/source/")
        if _wants_json(request_context):
            return _source_response(runtime, source_id, request_context)
        return _source_html_response(runtime, source_id, request_context)
    if path.startswith("/api/v1/source/"):
        return _source_response(runtime, path.removeprefix("/api/v1/source/"), request_context)
    if path == "/absence":
        if _wants_json(request_context):
            return _absence_response(runtime, request_context)
        return _absence_html_response(runtime, request_context)
    if path == "/api/v1/absence":
        return _absence_response(runtime, request_context)
    if path == "/review":
        if _wants_json(request_context):
            return _review_list_response(runtime, request_context)
        return _review_list_html_response(runtime, request_context)
    if path == "/api/v1/review":
        return _review_list_response(runtime, request_context)
    if path.startswith("/review/"):
        review_item_id = path.removeprefix("/review/")
        if _wants_json(request_context):
            return _review_item_response(runtime, review_item_id)
        return _review_item_html_response(runtime, review_item_id)
    if path.startswith("/api/v1/review/"):
        return _review_item_response(runtime, path.removeprefix("/api/v1/review/"))
    if path == "/rebuild":
        if _wants_json(request_context):
            return _rebuild_status_response(runtime)
        return _rebuild_html_response(runtime)
    if path == "/api/v1/rebuild/status":
        return _rebuild_status_response(runtime)
    return error_response(404, "route_not_found", "local service route was not found", {"path": path})


def _home_response(runtime: Any) -> LocalServiceResponse:
    workbench = _workbench()
    status = _status_payload(runtime)
    html = workbench.render_home_page(workbench.build_home_page_view(status))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, {"schema_version": "local_http_html_response.v0", "status": "pass"})


def _status_response(runtime: Any) -> LocalServiceResponse:
    return json_response(200, _status_payload(runtime))


def _status_payload(runtime: Any) -> dict[str, Any]:
    runtime_status = runtime.status().to_dict()
    summary = runtime.public_index.summarize().to_dict()
    return {
        "schema_version": "local_http_status_response.v0",
        "status": runtime_status.get("status", "pass"),
        "service": {
            "read_only": bool(runtime.read_only),
            "localhost_only": True,
            "write_routes_enabled": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "source_probe_execution_enabled": False,
            "workunit_execution_enabled": False,
            "review_decision_mutation_enabled": False,
            "index_rebuild_enabled": False,
            "operator_gated_review_decisions_enabled": True,
            "operator_gated_rebuild_enabled": True,
        },
        "runtime": runtime_status,
        "public_index": summary,
        "warnings": list(runtime_status.get("warnings", [])),
        "limitations": list(DEFAULT_LIMITATIONS),
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _status_html_response(runtime: Any) -> LocalServiceResponse:
    workbench = _workbench()
    payload = _status_payload(runtime)
    html = workbench.render_status_page(workbench.build_status_page_view(payload))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, payload)


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
    results = [_search_result_payload(runtime, item.to_dict()) for item in runtime.public_index.search(query, limit=limit)]
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


def _search_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _search_response(runtime, request_context)
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    html = workbench.render_search_page(workbench.build_search_page_view(query, response.payload))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, response.payload)


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


def _object_html_response(runtime: Any, record_id: str) -> LocalServiceResponse:
    workbench = _workbench()
    if not record_id:
        return error_response(400, "missing_record_id", "record_id is required")
    record = runtime.public_index.get_record(record_id)
    html = workbench.render_object_page(workbench.build_object_page_view(record_id, record.to_dict() if record else None))
    workbench.validate_local_workbench_page(html)
    return html_response(200 if record else 404, html, {"schema_version": "local_http_object_html_response.v0", "status": "pass" if record else "fail"})


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


def _source_html_response(runtime: Any, source_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _source_response(runtime, source_id, request_context)
    html = workbench.render_source_page(workbench.build_source_page_view(source_id, response.payload))
    workbench.validate_local_workbench_page(html)
    return html_response(response.status_code, html, response.payload)


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


def _absence_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _absence_response(runtime, request_context)
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    html = workbench.render_absence_page(workbench.build_absence_page_view(query, response.payload))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, response.payload)


def _review_list_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    status = first_param(request_context.params, "status", "")
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    payload = _review_service().list_review_items(runtime, status=status or None, limit=limit)
    payload.update(
        {
            "review_ui_enabled": True,
            "operator_token_required_for_mutations": True,
            "lan_enabled": False,
            "deployment_performed": False,
        }
    )
    return json_response(200, payload)


def _review_list_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _review_list_response(runtime, request_context)
    html = workbench.render_review_queue_page(workbench.build_review_queue_page_view(response.payload))
    workbench.validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(200, html, response.payload)


def _review_item_response(runtime: Any, review_item_id: str) -> LocalServiceResponse:
    if not review_item_id:
        return error_response(400, "missing_review_item_id", "review item id is required")
    payload = _review_service().get_review_item(runtime, review_item_id)
    return json_response(200 if payload.get("found") else 404, payload)


def _review_item_html_response(runtime: Any, review_item_id: str) -> LocalServiceResponse:
    workbench = _workbench()
    response = _review_item_response(runtime, review_item_id)
    html = workbench.render_review_item_page(workbench.build_review_item_page_view(review_item_id, response.payload))
    workbench.validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(response.status_code, html, response.payload)


def _rebuild_status_response(runtime: Any) -> LocalServiceResponse:
    summary = runtime.public_index.summarize().to_dict()
    payload = {
        "schema_version": "local_review_rebuild_status_response.v0",
        "status": "pass",
        "public_index": summary,
        "operator_token_required_for_mutations": True,
        "input_stores_mutated": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["rebuild writes only to the local reviewed public index store"],
    }
    return json_response(200, payload)


def _rebuild_html_response(runtime: Any) -> LocalServiceResponse:
    workbench = _workbench()
    response = _rebuild_status_response(runtime)
    html = workbench.render_rebuild_page(workbench.build_rebuild_page_view(response.payload))
    workbench.validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(200, html, response.payload)


def _mutation_response(runtime: Any, request_context: LocalRequestContext, operator_auth_state: Any) -> LocalServiceResponse:
    if request_context.method != "POST":
        return error_response(405, "method_not_allowed", "method is not enabled for local service route")
    try:
        _require_operator_token(request_context, runtime.config, operator_auth_state)
    except _operator_auth_error() as exc:
        return error_response(401, "operator_token_required", str(exc))
    path = request_context.path
    if path.startswith("/review/") and path.endswith("/decision"):
        review_item_id = path.removeprefix("/review/").removesuffix("/decision").strip("/")
        return _record_decision_response(runtime, request_context, review_item_id)
    if path == "/rebuild":
        return _apply_rebuild_response(runtime, request_context)
    return error_response(404, "route_not_found", "operator mutation route was not found", {"path": path})


def _record_decision_response(runtime: Any, request_context: LocalRequestContext, review_item_id: str) -> LocalServiceResponse:
    params = request_context.body_params
    decision = first_param(params, "decision", "")
    reason = first_param(params, "reason", "")
    operator_label = first_param(params, "operator_label", "local_operator")
    confirmed = first_param(params, "local_only_confirmed", "").lower() in {"1", "true", "yes", "on"}
    try:
        payload = _review_service().record_review_decision(runtime, review_item_id, decision, reason, operator_label, confirmed)
    except Exception as exc:
        return error_response(400, "review_decision_rejected", str(exc), {"review_item_id": review_item_id})
    return json_response(200, payload)


def _apply_rebuild_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    params = request_context.body_params
    operator_label = first_param(params, "operator_label", "local_operator")
    dry_run = first_param(params, "dry_run", "").lower() in {"1", "true", "yes", "on"}
    try:
        payload = _review_service().rebuild_reviewed_index(runtime, operator_label=operator_label, dry_run=dry_run)
    except Exception as exc:
        return error_response(400, "reviewed_index_rebuild_rejected", str(exc))
    return json_response(200, payload)


def _wants_json(request_context: LocalRequestContext) -> bool:
    return first_param(request_context.params, "format", "").lower() == "json"


def _search_result_payload(runtime: Any, result: dict[str, Any]) -> dict[str, Any]:
    record = runtime.public_index.get_record(str(result.get("record_id", "")))
    if record is None:
        return result
    payload = record.to_dict()
    payload.update(
        {
            "score": result.get("score"),
            "matched_terms": result.get("matched_terms", []),
        }
    )
    return payload


def _workbench() -> Any:
    return __import__("runtime.local_workbench", fromlist=["build_home_page_view"])


def _review_service() -> Any:
    return __import__("runtime.local_review", fromlist=["list_review_items"])


def _operator_auth() -> Any:
    return __import__("runtime.local_operator", fromlist=["require_operator_token"])


def _operator_auth_error() -> Any:
    return getattr(_operator_auth(), "LocalOperatorAuthError")


def _require_operator_token(request_context: LocalRequestContext, config: Any, operator_auth_state: Any) -> Any:
    return _operator_auth().require_operator_token(request_context, config, operator_auth_state)

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
    if not _route_allowed_for_scope(method, path, request_context.client_scope):
        return error_response(
            403,
            "lan_route_forbidden",
            "route is not available for this client scope",
            {"path": path, "method": method, "client_scope": request_context.client_scope},
        )
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
    if path == "/hunts":
        if _wants_json(request_context):
            return _hunt_list_response(runtime, request_context)
        return _hunt_list_html_response(runtime, request_context)
    if path == "/api/v1/hunts":
        return _hunt_list_response(runtime, request_context)
    parsed_hunt_route = _parse_hunt_route(path)
    if parsed_hunt_route and parsed_hunt_route[1] == "exhaustion":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_exhaustion_response(runtime, hunt_id)
        if _wants_json(request_context):
            return _hunt_exhaustion_response(runtime, hunt_id)
        return _hunt_exhaustion_html_response(runtime, hunt_id)
    if parsed_hunt_route and parsed_hunt_route[1] == "commands":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_commands_response(runtime, hunt_id)
        if _wants_json(request_context):
            return _hunt_commands_response(runtime, hunt_id)
        return _hunt_commands_html_response(runtime, hunt_id)
    if parsed_hunt_route and parsed_hunt_route[1] == "steering":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_steering_response(runtime, hunt_id)
        if _wants_json(request_context):
            return _hunt_steering_response(runtime, hunt_id)
        return _hunt_steering_html_response(runtime, hunt_id)
    if path.startswith("/hunt/"):
        hunt_id = path.removeprefix("/hunt/")
        if _wants_json(request_context):
            return _hunt_detail_response(runtime, hunt_id)
        return _hunt_detail_html_response(runtime, hunt_id)
    if path.startswith("/api/v1/hunt/"):
        return _hunt_detail_response(runtime, path.removeprefix("/api/v1/hunt/"))
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
    lan_enabled = bool(getattr(runtime, "lan_enabled", False))
    lan_read_only = bool(getattr(runtime, "lan_read_only", True))
    warnings = list(runtime_status.get("warnings", []))
    if lan_enabled:
        warnings.extend(_lan_warnings())
    return {
        "schema_version": "local_http_status_response.v0",
        "status": runtime_status.get("status", "pass"),
        "service": {
            "read_only": bool(runtime.read_only),
            "localhost_only": not lan_enabled,
            "write_routes_enabled": False,
            "lan_enabled": lan_enabled,
            "bind_lan": bool(getattr(runtime, "bind_lan", False)),
            "lan_read_only": lan_read_only,
            "lan_mutations_enabled": False,
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
        "warnings": warnings,
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
    lan_enabled = bool(getattr(runtime, "lan_enabled", False))
    payload = {
        "schema_version": "local_http_health_response.v0",
        "status": "pass" if status.get("status") == "pass" else "fail",
        "read_only": True,
        "localhost_only": not lan_enabled,
        "lan_enabled": lan_enabled,
        "lan_read_only": bool(getattr(runtime, "lan_read_only", True)),
        "deployment_performed": False,
        "warnings": list(status.get("warnings", [])) + (_lan_warnings() if lan_enabled else []),
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


def _hunt_list_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    sessions = [item.to_dict() for item in runtime.search_hunt.list_sessions(limit=limit)]
    payload = {
        "schema_version": "search_hunt_ui_hunts_response.v0",
        "status": "pass",
        "hunt_count": len(sessions),
        "hunts": sessions,
        "unavailable_actions": _search_hunt_unavailable_actions_payload(),
        "read_only": True,
        "hunt_creation_enabled": False,
        "hunt_transition_enabled": False,
        "workunit_creation_enabled": False,
        "source_probe_execution_enabled": False,
        "model_provider_enabled": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS)
        + [
            "Search Hunt Sessions are local investigation state only",
            "read-only UI does not add hunts or change hunt state",
        ],
    }
    return json_response(200, payload)


def _hunt_list_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _hunt_list_response(runtime, request_context)
    html = workbench.render_search_hunt_list_page(workbench.build_search_hunt_list_page_view(response.payload["hunts"], response.payload))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, response.payload)


def _hunt_detail_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return json_response(
            404,
            {
                "schema_version": "search_hunt_ui_hunt_response.v0",
                "status": "not_found",
                "hunt_id": hunt_id,
                "hunt": None,
                "warnings": [],
                "limitations": list(DEFAULT_LIMITATIONS) + ["missing hunts are not created implicitly"],
            },
        )
    transitions = [item.to_dict() for item in runtime.search_hunt.list_transitions(hunt_id, limit=100)]
    summaries = [item.to_dict() for item in runtime.search_hunt.list_summaries(hunt_id, limit=100)]
    commands = [item.to_dict() for item in runtime.search_hunt.list_commands(hunt_id, limit=100)]
    steering = [item.to_dict() for item in runtime.search_hunt.list_steering_preferences(hunt_id, active_only=False)]
    exhaustion = runtime.search_hunt.get_latest_exhaustion_report(hunt_id)
    payload = {
        "schema_version": "search_hunt_ui_hunt_response.v0",
        "status": "pass",
        "hunt_id": hunt_id,
        "hunt": session.to_dict(),
        "transitions": transitions,
        "summaries": summaries,
        "commands": commands,
        "steering_preferences": steering,
        "exhaustion_report": exhaustion.to_dict() if exhaustion else None,
        "unavailable_actions": _search_hunt_unavailable_actions_payload(),
        "read_only": True,
        "hunt_creation_enabled": False,
        "hunt_transition_enabled": True,
        "command_controls_enabled": not bool(getattr(runtime, "read_only", True)),
        "steering_controls_enabled": not bool(getattr(runtime, "read_only", True)),
        "exhaustion_report_generation_enabled": not bool(getattr(runtime, "read_only", True)),
        "operator_token_required_for_mutations": True,
        "localhost_only_mutations": True,
        "lan_command_mutations_enabled": False,
        "workunit_creation_enabled": False,
        "source_probe_execution_enabled": False,
        "model_provider_enabled": False,
        "review_mutation_enabled": False,
        "public_index_mutation_enabled": False,
        "master_index_mutation_enabled": False,
        "warnings": list(session.warnings),
        "limitations": list(DEFAULT_LIMITATIONS)
        + list(session.limitations)
        + [
            "Search Hunt Sessions are local investigation state only",
            "local absence is current-index absence only",
        ],
    }
    return json_response(200, payload)


def _hunt_detail_html_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    workbench = _workbench()
    response = _hunt_detail_response(runtime, hunt_id)
    if response.status_code == 404:
        html = workbench.render_search_hunt_not_found_page(workbench.build_search_hunt_not_found_page_view(hunt_id))
        workbench.validate_local_workbench_page(html)
        return html_response(404, html, response.payload)
    if response.status_code != 200:
        return response
    html = workbench.render_search_hunt_detail_page(
        workbench.build_search_hunt_detail_page_view(
            response.payload["hunt"],
            response.payload["transitions"],
            response.payload,
        )
    )
    workbench.validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(response.status_code, html, response.payload)


def _hunt_commands_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    commands = [item.to_dict() for item in runtime.search_hunt.list_commands(hunt_id, limit=100)]
    payload = {
        "schema_version": "search_hunt_command_history_response.v0",
        "status": "pass",
        "hunt_id": hunt_id,
        "command_count": len(commands),
        "commands": commands,
        "read_only": True,
        "workunit_creation_enabled": False,
        "source_probe_execution_enabled": False,
        "model_provider_enabled": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["command history is local operator state only"],
    }
    return json_response(200, payload)


def _hunt_commands_html_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    return _hunt_detail_html_response(runtime, hunt_id)


def _hunt_steering_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    preferences = [item.to_dict() for item in runtime.search_hunt.list_steering_preferences(hunt_id, active_only=False)]
    payload = {
        "schema_version": "search_hunt_steering_response.v0",
        "status": "pass",
        "hunt_id": hunt_id,
        "steering_count": len(preferences),
        "steering_preferences": preferences,
        "read_only": True,
        "workunit_creation_enabled": False,
        "source_probe_execution_enabled": False,
        "model_provider_enabled": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["steering preferences record operator intent only"],
    }
    return json_response(200, payload)


def _hunt_steering_html_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    return _hunt_detail_html_response(runtime, hunt_id)


def _hunt_exhaustion_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    report = runtime.search_hunt.get_latest_exhaustion_report(hunt_id)
    payload = _hunt_exhaustion_payload(hunt_id, report.to_dict() if report else None)
    if report is None:
        payload["status"] = "not_found"
        payload["warnings"] = ["no exhaustion report has been generated for this hunt"]
    return json_response(200, payload)


def _hunt_exhaustion_html_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    return _hunt_detail_html_response(runtime, hunt_id)


def _review_list_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    status = first_param(request_context.params, "status", "")
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    payload = _review_service().list_review_items(runtime, status=status or None, limit=limit)
    payload.update(
        {
            "review_ui_enabled": True,
            "operator_token_required_for_mutations": True,
            "lan_enabled": bool(getattr(runtime, "lan_enabled", False)),
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
        "lan_enabled": bool(getattr(runtime, "lan_enabled", False)),
        "lan_mutations_enabled": False,
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
    if request_context.client_scope != "loopback":
        return error_response(
            403,
            "lan_mutation_forbidden",
            "mutation routes are localhost-only",
            {"path": request_context.path, "client_scope": request_context.client_scope},
        )
    if request_context.method != "POST":
        return error_response(405, "method_not_allowed", "method is not enabled for local service route")
    try:
        _require_operator_token(request_context, runtime.config, operator_auth_state)
    except _operator_auth_error() as exc:
        return error_response(401, "operator_token_required", str(exc))
    path = request_context.path
    hunt_mutation = _parse_hunt_mutation_path(path)
    if hunt_mutation:
        if hunt_mutation[1] == "exhaustion":
            return _apply_hunt_exhaustion_response(runtime, request_context, hunt_mutation[0])
        return _apply_hunt_command_response(runtime, request_context, hunt_mutation[0], hunt_mutation[1])
    if path.startswith("/review/") and path.endswith("/decision"):
        review_item_id = path.removeprefix("/review/").removesuffix("/decision").strip("/")
        return _record_decision_response(runtime, request_context, review_item_id)
    if path == "/rebuild":
        return _apply_rebuild_response(runtime, request_context)
    return error_response(404, "route_not_found", "operator mutation route was not found", {"path": path})


def _apply_hunt_command_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str, action: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    params = request_context.body_params
    operator_label = first_param(params, "operator_label", "local_operator")
    reason = first_param(params, "reason", "")
    value = first_param(params, "value", "")
    try:
        if action == "steer":
            steering_type = first_param(params, "type", first_param(params, "steering_type", ""))
            remove_id = first_param(params, "steering_id", "")
            if remove_id:
                preference = runtime.search_hunt.remove_steering_preference(hunt_id, remove_id, reason=reason, operator_label=operator_label)
                payload = _hunt_command_payload("search_hunt_steering_removed", hunt_id, {"steering_preference": preference.to_dict()})
            else:
                preference = runtime.search_hunt.add_steering_preference(hunt_id, steering_type, value=value, reason=reason, operator_label=operator_label)
                payload = _hunt_command_payload("search_hunt_steering_recorded", hunt_id, {"steering_preference": preference.to_dict()})
        else:
            result = runtime.search_hunt.apply_command(hunt_id, _command_type_for_route(action), value=value, reason=reason, operator_label=operator_label)
            payload = _hunt_command_payload("search_hunt_command_applied", hunt_id, result.to_dict())
    except Exception as exc:
        return error_response(400, "hunt_command_rejected", str(exc), {"hunt_id": hunt_id, "action": action})
    return json_response(200, payload)


def _apply_hunt_exhaustion_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    try:
        report = _search_hunt().build_hunt_exhaustion_report(runtime, hunt_id, operator_label=operator_label)
        attached = runtime.search_hunt.attach_exhaustion_report(hunt_id, report)
    except Exception as exc:
        return error_response(400, "hunt_exhaustion_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _hunt_exhaustion_payload(hunt_id, attached.to_dict())
    payload.update(
        {
            "action": "search_hunt_exhaustion_report_generated",
            "operator_token_required": True,
            "localhost_only_generation": True,
            "lan_generation_enabled": False,
        }
    )
    return json_response(200, payload)


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


def _route_allowed_for_scope(method: str, path: str, client_scope: object) -> bool:
    if _is_hunt_operator_mutation_path(method, path):
        return str(getattr(client_scope, "value", client_scope) or "").lower() == "loopback"
    return _network().is_route_allowed_for_scope(method, path, client_scope)


def _is_hunt_operator_mutation_path(method: str, path: str) -> bool:
    return str(method or "").upper() == "POST" and _parse_hunt_mutation_path(path) is not None


def _parse_hunt_route(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    if len(parts) == 3 and parts[0] == "hunt" and parts[2] in {"commands", "steering", "exhaustion"}:
        return parts[1], parts[2]
    if len(parts) == 5 and parts[:3] == ["api", "v1", "hunt"] and parts[4] in {"commands", "steering", "exhaustion"}:
        return parts[3], parts[4]
    return None


def _parse_hunt_mutation_path(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    actions = {"pause", "resume", "cancel", "block", "wait-for-user", "wait-for-policy", "steer", "exhaustion"}
    if len(parts) == 3 and parts[0] == "hunt" and parts[2] in actions:
        return parts[1], parts[2]
    if len(parts) == 5 and parts[:3] == ["api", "v1", "hunt"] and parts[4] == "exhaustion":
        return parts[3], parts[4]
    return None


def _command_type_for_route(action: str) -> str:
    return {
        "pause": "pause",
        "resume": "resume",
        "cancel": "cancel",
        "block": "block",
        "wait-for-user": "wait_for_user",
        "wait-for-policy": "wait_for_policy",
    }[action]


def _hunt_command_payload(action: str, hunt_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "search_hunt_command_route_result.v0",
        "status": "pass",
        "action": action,
        "hunt_id": hunt_id,
        "operator_token_required": True,
        "localhost_only_mutations": True,
        "lan_command_mutations_enabled": False,
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
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["command routes mutate Search Hunt state only"],
    }
    result.update(payload)
    return result


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


def _search_hunt_unavailable_actions_payload() -> list[dict[str, str]]:
    return [
        {
            "action": "pause/resume/steer",
            "status": "deferred",
            "reason": "Command controls are added in a later Search Hunt command phase.",
        },
        {
            "action": "exhaustion report",
            "status": "available",
            "reason": "Reports explain local checked layers and deferred work without executing it.",
        },
        {
            "action": "SearchNeed pipeline",
            "status": "deferred",
            "reason": "Need persistence is a later pipeline step.",
        },
        {
            "action": "WorkUnit pipeline",
            "status": "deferred",
            "reason": "WorkUnit creation from hunts is not enabled.",
        },
        {
            "action": "background runner",
            "status": "deferred",
            "reason": "Background hunt execution is not enabled.",
        },
        {
            "action": "source probes",
            "status": "disabled",
            "reason": "Source-probe execution remains behind a future source gate.",
        },
        {
            "action": "extraction",
            "status": "deferred",
            "reason": "Extraction remains outside this UI state layer.",
        },
        {
            "action": "AI escalation",
            "status": "disabled",
            "reason": "Model/provider calls are disabled.",
        },
        {
            "action": "sync",
            "status": "disabled",
            "reason": "Sync requires a future reviewed policy gate.",
        },
    ]


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


def _lan_warnings() -> list[str]:
    module = _network()
    return [module.build_lan_warning(), module.build_firewall_warning()]


def _network() -> Any:
    return __import__("runtime.local_network", fromlist=["is_route_allowed_for_scope", "build_lan_warning"])


def _search_hunt() -> Any:
    return __import__("runtime.search_hunt", fromlist=["build_hunt_exhaustion_report"])


def _hunt_exhaustion_payload(hunt_id: str, report: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "schema_version": "search_hunt_exhaustion_response.v0",
        "status": "pass",
        "hunt_id": hunt_id,
        "exhaustion_report": report,
        "read_only": True,
        "operator_token_required_for_generation": True,
        "localhost_only_generation": True,
        "lan_generation_enabled": False,
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
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS)
        + [
            "exhaustion reports are local current-index explanations only",
            "exhaustion reports do not create background work",
        ],
    }

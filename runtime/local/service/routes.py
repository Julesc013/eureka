"""Routes over the local appliance runtime."""

from html import escape
import json
from typing import Any, Mapping
from urllib.parse import quote

from runtime.search.live_service import LiveSearchService
from runtime.search.live_web import provider_status

from .request_context import LocalRequestContext
from .responses import DEFAULT_LIMITATIONS, LocalServiceResponse, error_response, html_response, json_response, redirect_response
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
        if _live_search_enabled(runtime):
            return _live_search_home_html_response(runtime, request_context)
        return redirect_response("/explore")
    if path == "/status":
        if _wants_json(request_context):
            return _status_response(runtime)
        return _status_html_response(runtime)
    if path == "/api/v1/status":
        return _status_response(runtime)
    if path in {"/health", "/api/v1/health"}:
        return _health_response(runtime)
    if path == "/explore":
        if _wants_json(request_context):
            return _explore_workspace_response(runtime, request_context)
        return _explore_workspace_html_response(runtime, request_context)
    if path == "/api/v1/explore":
        return _explore_workspace_response(runtime, request_context)
    if path == "/explore/runs":
        if _wants_json(request_context):
            return _explore_runs_response(runtime, request_context)
        return _explore_runs_html_response(runtime, request_context)
    if path == "/api/v1/explore/runs":
        return _explore_runs_response(runtime, request_context)
    if path == "/explore/compare":
        if _wants_json(request_context):
            return _explore_compare_response(runtime, request_context)
        return _explore_compare_html_response(runtime, request_context)
    if path == "/api/v1/explore/compare":
        return _explore_compare_response(runtime, request_context)
    explore_run_route = _parse_explore_run_route(path)
    if explore_run_route:
        if path.startswith("/api/v1/") or _wants_json(request_context):
            return _explore_run_response(runtime, request_context, explore_run_route)
        return _explore_run_html_response(runtime, request_context, explore_run_route)
    if path == "/search":
        if _live_search_enabled(runtime):
            if _wants_json(request_context):
                return _live_search_response(runtime, request_context)
            return _live_search_html_response(runtime, request_context)
        if _wants_json(request_context):
            return _search_response(runtime, request_context)
        return _search_html_response(runtime, request_context)
    if path == "/api/search":
        if _live_search_enabled(runtime):
            return _live_search_response(runtime, request_context)
        return _search_response(runtime, request_context)
    if path == "/api/v1/search":
        if _live_search_enabled(runtime):
            return _live_search_response(runtime, request_context)
        return _search_response(runtime, request_context)
    if path == "/hunt":
        if _live_search_enabled(runtime):
            if _wants_json(request_context):
                return _live_hunt_response(runtime, request_context)
            return _live_hunt_html_response(runtime, request_context)
    if path == "/api/hunt":
        if _live_search_enabled(runtime):
            return _live_hunt_response(runtime, request_context)
    if path == "/runs":
        if _wants_json(request_context):
            return _workbench_live_run_list_or_create_response(request_context)
        return _workbench_live_run_list_or_create_html_response(request_context)
    if path == "/api/v1/resolution-runs":
        return _workbench_live_run_list_or_create_response(request_context)
    parsed_run_route = _parse_workbench_live_run_route(path)
    if parsed_run_route:
        run_id, endpoint = parsed_run_route
        if endpoint == "events":
            return _workbench_live_run_events_response(run_id, request_context)
        if endpoint == "lanes":
            return _workbench_live_run_lanes_response(run_id, request_context)
        if endpoint == "workunits":
            return _workbench_live_run_workunits_response(run_id, request_context)
        if endpoint == "commands":
            return _workbench_live_run_commands_response(run_id, request_context)
        if path.startswith("/api/v1/") or _wants_json(request_context):
            return _workbench_live_run_detail_response(run_id, request_context)
        return _workbench_live_run_detail_html_response(run_id, request_context)
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
    if parsed_hunt_route and parsed_hunt_route[1] == "replay":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_replay_response(runtime, hunt_id)
        if _wants_json(request_context):
            return _hunt_replay_response(runtime, hunt_id)
        return _hunt_detail_html_response(runtime, hunt_id)
    if parsed_hunt_route and parsed_hunt_route[1] == "runner":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_runner_response(runtime, hunt_id)
        if _wants_json(request_context):
            return _hunt_runner_response(runtime, hunt_id)
        return _hunt_detail_html_response(runtime, hunt_id)
    if parsed_hunt_route and parsed_hunt_route[1] == "agent-tasks":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_agent_tasks_response(runtime, hunt_id, request_context)
        if _wants_json(request_context):
            return _hunt_agent_tasks_response(runtime, hunt_id, request_context)
        return _hunt_detail_html_response(runtime, hunt_id)
    if parsed_hunt_route and parsed_hunt_route[1] == "ai-escalation":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_ai_escalation_response(runtime, hunt_id)
        if _wants_json(request_context):
            return _hunt_ai_escalation_response(runtime, hunt_id)
        return _hunt_detail_html_response(runtime, hunt_id)
    if parsed_hunt_route and parsed_hunt_route[1] == "workunits":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_workunits_response(runtime, hunt_id, request_context)
        if _wants_json(request_context):
            return _hunt_workunits_response(runtime, hunt_id, request_context)
        return _hunt_detail_html_response(runtime, hunt_id)
    if parsed_hunt_route and parsed_hunt_route[1] == "needs":
        hunt_id = parsed_hunt_route[0]
        if path.startswith("/api/v1/"):
            return _hunt_needs_response(runtime, hunt_id, request_context)
        if _wants_json(request_context):
            return _hunt_needs_response(runtime, hunt_id, request_context)
        return _hunt_detail_html_response(runtime, hunt_id)
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
    if path == "/needs":
        if _wants_json(request_context):
            return _need_list_response(runtime, request_context)
        return _need_list_html_response(runtime, request_context)
    if path == "/api/v1/needs":
        return _need_list_response(runtime, request_context)
    parsed_need_route = _parse_need_route(path)
    if parsed_need_route and parsed_need_route[1] == "agent-tasks":
        need_id = parsed_need_route[0]
        if path.startswith("/api/v1/"):
            return _need_agent_tasks_response(runtime, need_id, request_context)
        if _wants_json(request_context):
            return _need_agent_tasks_response(runtime, need_id, request_context)
        return _need_detail_html_response(runtime, need_id)
    if parsed_need_route and parsed_need_route[1] == "ai-escalation":
        need_id = parsed_need_route[0]
        if path.startswith("/api/v1/"):
            return _need_ai_escalation_response(runtime, need_id)
        if _wants_json(request_context):
            return _need_ai_escalation_response(runtime, need_id)
        return _need_detail_html_response(runtime, need_id)
    if parsed_need_route and parsed_need_route[1] == "workunits":
        need_id = parsed_need_route[0]
        if path.startswith("/api/v1/"):
            return _need_workunits_response(runtime, need_id, request_context)
        if _wants_json(request_context):
            return _need_workunits_response(runtime, need_id, request_context)
        return _need_detail_html_response(runtime, need_id)
    if path == "/api/v1/agent-research/report-schema":
        return _agent_research_report_schema_response(runtime)
    if path.startswith("/need/"):
        need_id = path.removeprefix("/need/")
        if _wants_json(request_context):
            return _need_detail_response(runtime, need_id)
        return _need_detail_html_response(runtime, need_id)
    if path.startswith("/api/v1/need/"):
        return _need_detail_response(runtime, path.removeprefix("/api/v1/need/"))
    if path == "/review":
        if _wants_json(request_context):
            return _review_list_response(runtime, request_context)
        return _review_list_html_response(runtime, request_context)
    if path == "/api/v1/review":
        return _review_list_response(runtime, request_context)
    if path == "/promotion":
        if _wants_json(request_context):
            return _workbench_review_promote_response(request_context, endpoint="promotion")
        return _workbench_review_promote_html_response(request_context, endpoint="promotion")
    if path == "/api/v1/promotion-preview":
        return _workbench_review_promote_response(request_context, endpoint="promotion_preview")
    if path == "/api/v1/reviewed-index/refresh-preview":
        return _workbench_review_promote_response(request_context, endpoint="reviewed_index_refresh_preview")
    if path == "/apply":
        if _wants_json(request_context):
            return _local_apply_preview_response(request_context, endpoint="apply")
        return _local_apply_html_response(request_context)
    if path == "/api/v1/local-apply/preview":
        return _local_apply_preview_response(request_context, endpoint="local_apply_preview")
    if path == "/api/v1/local-apply/audit":
        return _local_apply_audit_response(request_context)
    if path == "/index/rebuild-preview":
        if _wants_json(request_context):
            return _workbench_review_promote_response(request_context, endpoint="reviewed_index_refresh_preview")
        return _workbench_review_promote_html_response(request_context, endpoint="reviewed_index_refresh_preview")
    if path.startswith("/promotion/"):
        if _wants_json(request_context):
            return _workbench_review_promote_response(request_context, endpoint="promotion_detail")
        return _workbench_review_promote_html_response(request_context, endpoint="promotion_detail")
    if path.startswith("/api/v1/promotion-preview/"):
        return _workbench_review_promote_response(request_context, endpoint="promotion_detail")
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
            "live_search_enabled": _live_search_enabled(runtime),
            "live_provider_configured": bool(provider_status(str(getattr(runtime, "live_search_provider", "brave"))).get("configured")),
        },
        "runtime": runtime_status,
        "public_index": summary,
        "warnings": warnings,
        "limitations": _service_limitations(runtime),
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
        "limitations": _service_limitations(runtime),
    }
    return json_response(200 if payload["status"] == "pass" else 503, payload)


def _explore_workspace_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=20)
    include_synthetic_default = bool(getattr(runtime, "e2e_explore_include_synthetic", False))
    include_synthetic_param = first_param(
        request_context.params,
        "include_synthetic",
        first_param(request_context.params, "include-synthetic", "true" if include_synthetic_default else ""),
    )
    payload = _explore().build_explore_workspace(
        query,
        options=_explore().options_from_runtime(runtime),
        limit=limit,
        include_synthetic=_truthy(include_synthetic_param),
    )
    return json_response(200, payload)


def _explore_workspace_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    response = _explore_workspace_response(runtime, request_context)
    html = _explore_html().render_explore_workspace_html(response.payload)
    _workbench().validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(200, html, response.payload)


def _explore_runs_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=50)
    payload = _explore().list_run_bundles(_explore().options_from_runtime(runtime).runs_root, limit=limit)
    return json_response(200, payload)


def _explore_runs_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    response = _explore_runs_response(runtime, request_context)
    html = _explore_html().render_explore_runs_html(response.payload)
    _workbench().validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(200, html, response.payload)


def _explore_run_response(runtime: Any, request_context: LocalRequestContext, run_id: str) -> LocalServiceResponse:
    try:
        payload = _explore().load_run_detail(run_id, _explore().options_from_runtime(runtime).runs_root)
    except FileNotFoundError:
        return error_response(404, "explore_run_not_found", "E2E explore run bundle was not found", {"run_id": run_id})
    except Exception as exc:
        return error_response(400, "explore_run_invalid", str(exc), {"run_id": run_id})
    return json_response(200, payload)


def _explore_run_html_response(runtime: Any, request_context: LocalRequestContext, run_id: str) -> LocalServiceResponse:
    response = _explore_run_response(runtime, request_context, run_id)
    if response.status_code != 200:
        error = dict(response.payload.get("error") or {})
        html = _explore_html().render_explore_error_html(
            "Hunt Could Not Open",
            str(error.get("message") or "The local Hunt record was not found."),
        )
        _workbench().validate_local_workbench_page(html, allow_operator_mutation_forms=True)
        return html_response(response.status_code, html, {"schema_version": "local_http_explore_error_response.v0", "status": "fail"})
    html = _explore_html().render_explore_run_html(response.payload)
    _workbench().validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(200, html, response.payload)


def _explore_compare_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    left = first_param(request_context.params, "left", "")
    right = first_param(request_context.params, "right", "")
    if not left or not right:
        return json_response(200, _explore().empty_compare_payload(left, right))
    try:
        payload = _explore().compare_runs(left, right, runs_root=_explore().options_from_runtime(runtime).runs_root)
    except FileNotFoundError as exc:
        return error_response(404, "explore_run_not_found", str(exc), {"left": left, "right": right})
    except Exception as exc:
        return error_response(400, "explore_compare_invalid", str(exc), {"left": left, "right": right})
    return json_response(200, payload)


def _explore_compare_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    response = _explore_compare_response(runtime, request_context)
    if response.status_code != 200:
        return response
    html = _explore_html().render_explore_compare_html(response.payload)
    _workbench().validate_local_workbench_page(html)
    return html_response(200, html, response.payload)


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


def _live_search_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    return json_response(200, _live_search_payload(runtime, request_context))


def _live_search_home_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    return _live_search_html_response(runtime, request_context)


def _live_search_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    payload = _live_search_payload(runtime, request_context)
    return html_response(200, _render_live_search_html(payload), payload)


def _live_hunt_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    return json_response(200, _live_hunt_payload(runtime, request_context))


def _live_hunt_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    payload = _live_hunt_payload(runtime, request_context)
    return html_response(200, _render_live_search_html(payload, hunt=True), payload)


def _search_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _search_response(runtime, request_context)
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    live_run = None
    if query.strip():
        live_run = _workbench_live_run().create_workbench_resolution_run(
            query,
            _projection_profile(request_context),
            include_ia_hunt_dry_run=True,
        )
    html = workbench.render_search_page(workbench.build_search_page_view(query, response.payload, live_run=live_run))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, response.payload)


def _live_search_payload(runtime: Any, request_context: LocalRequestContext) -> dict[str, Any]:
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", "")).strip()
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=10)
    provider_name = str(getattr(runtime, "live_search_provider", "brave") or "brave")
    local = _live_local_preview_results(runtime, query, limit=limit)
    payload = LiveSearchService(provider_name=provider_name).search(
        query,
        mode="blended",
        local_results=local,
        page=0,
        count=limit,
        freshness=first_param(request_context.params, "freshness", ""),
        country=first_param(request_context.params, "country", ""),
        language=first_param(request_context.params, "language", ""),
        safe_search=first_param(request_context.params, "safe_search", "moderate"),
        timeout_seconds=10,
    )
    payload["limitations"] = _service_limitations(runtime) + ["live provider results are transient discovery leads"]
    return payload


def _live_hunt_payload(runtime: Any, request_context: LocalRequestContext) -> dict[str, Any]:
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", "")).strip()
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=10)
    max_queries = parse_limit(first_param(request_context.params, "max_queries", ""), default=5)
    provider_name = str(getattr(runtime, "live_search_provider", "brave") or "brave")
    hunt = LiveSearchService(provider_name=provider_name).start_hunt(
        query,
        run_id="http-live-hunt-preview",
        max_queries=max_queries,
        max_fetches=0,
        count=limit,
        timeout_seconds=10,
    )
    payload = dict(hunt.response)
    payload["schema_version"] = "eureka.live_hunt_response.v0"
    payload["limitations"] = _service_limitations(runtime) + ["live Hunt currently expands provider queries only"]
    return payload


def _live_local_preview_results(runtime: Any, query: str, *, limit: int) -> dict[str, Any]:
    path = getattr(runtime, "e2e_explore_preview_index_path", None)
    if not query or path is None:
        return {"status": "not_requested", "result_count": 0, "results": [], "warnings": []}
    try:
        payload = _preview_index().search_preview_index(path, query, limit=limit, include_synthetic=False)
    except Exception:
        return {"status": "absent_or_unavailable", "result_count": 0, "results": [], "warnings": ["Local Preview Index is unavailable."]}
    cards = []
    for item in payload.get("results") or []:
        if not isinstance(item, dict):
            continue
        cards.append(
            {
                "state": "INDEXED - UNREVIEWED",
                "title": str(item.get("title") or item.get("normalized_title") or item.get("candidate_id") or "Indexed discovery"),
                "url": str(item.get("url") or ""),
                "snippet": str(item.get("summary") or item.get("non_verified_reason") or "Local Preview Index record."),
                "provider": str(item.get("source_family") or "local_preview_index"),
                "retrieved_at": str(item.get("created_at") or ""),
                "query": query,
                "source": "local_preview_index",
                "retention_policy": {"persist_urls": True, "persist_snippets": True, "persist_rank": False, "terms_basis": "local_preview_index"},
            }
        )
    return {"status": "pass", "result_count": len(cards), "results": cards, "warnings": []}


def _render_live_search_html(payload: Mapping[str, Any], *, hunt: bool = False) -> str:
    query = str(payload.get("query") or "")
    title = "Eureka"
    cards = payload.get("results") or []
    if not cards and query:
        error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
        if not error and payload.get("errors"):
            errors = payload.get("errors") if isinstance(payload.get("errors"), list) else []
            error = errors[0] if errors and isinstance(errors[0], Mapping) else {}
        message = str(error.get("message") if isinstance(error, Mapping) else "") or "No results yet."
        result_html = f'<p class="empty">{escape(message)}</p>'
    elif not cards:
        result_html = '<p class="empty">Search the web and your Eureka index.</p>'
    else:
        result_html = "\n".join(_render_live_card(item) for item in cards if isinstance(item, Mapping))
    escaped_query = escape(query, quote=True)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{title}</title>",
            "<style>body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;color:#182229;background:#f7f8f8}main{max-width:980px;margin:auto;padding:28px 18px}.search{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:8px;margin:16px 0 22px}.search input{font:inherit;padding:11px;border:1px solid #aeb8bf;border-radius:6px;background:white}.search button,.search a{font:inherit;padding:11px 14px;border-radius:6px;border:1px solid #2d5d78;background:#2d5d78;color:white;text-decoration:none}.search a{background:#fff;color:#2d5d78}.card{background:#fff;border:1px solid #d8dee2;border-radius:8px;padding:14px;margin:10px 0}.state{font-size:12px;font-weight:700;color:#4b5b64}.url{color:#0b5cad;overflow-wrap:anywhere}.meta,.empty{color:#52616b}.snippet{margin:8px 0}</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>Eureka</h1>",
            '<form class="search" action="/hunt" method="get">' if hunt else '<form class="search" action="/search" method="get">',
            f'<input name="q" value="{escaped_query}" placeholder="Search the web and your Eureka index..." autofocus>',
            '<button type="submit">Search</button>' if not hunt else '<button type="submit">Hunt deeper</button>',
            f'<a href="/hunt?q={quote(query)}">Hunt deeper</a>' if not hunt else f'<a href="/search?q={quote(query)}">Search</a>',
            "</form>",
            result_html,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _render_live_card(item: Mapping[str, Any]) -> str:
    title = escape(str(item.get("title") or "Live result"))
    url = escape(str(item.get("url") or ""))
    snippet = escape(str(item.get("snippet") or ""))
    state = escape(str(item.get("state") or "LIVE - UNREVIEWED"))
    provider = escape(str(item.get("provider") or ""))
    retrieved_at = escape(str(item.get("retrieved_at") or ""))
    return "\n".join(
        [
            '<article class="card">',
            f'<div class="state">{state}</div>',
            f"<h2>{title}</h2>",
            f'<div class="url">{url}</div>' if url else "",
            f'<p class="snippet">{snippet}</p>' if snippet else "",
            f'<p class="meta">Provider: {provider or "local"} | Retrieved: {retrieved_at or "n/a"}</p>',
            "</article>",
        ]
    )


def _workbench_live_run_list_or_create_response(request_context: LocalRequestContext) -> LocalServiceResponse:
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    live_run = _workbench_live_run()
    if query.strip():
        packet = live_run.create_workbench_resolution_run(
            query,
            _projection_profile(request_context),
            include_ia_hunt_dry_run=_include_ia_hunt_dry_run(request_context),
        )
        return json_response(200, live_run.build_api_response(packet, "create_run"))
    return json_response(200, live_run.list_workbench_resolution_runs(_projection_profile(request_context)))


def _workbench_live_run_list_or_create_html_response(request_context: LocalRequestContext) -> LocalServiceResponse:
    query = first_param(request_context.params, "q", first_param(request_context.params, "query", ""))
    live_run = _workbench_live_run()
    workbench = _workbench()
    if query.strip():
        packet = live_run.create_workbench_resolution_run(
            query,
            _projection_profile(request_context),
            include_ia_hunt_dry_run=_include_ia_hunt_dry_run(request_context),
        )
        html = workbench.render_workbench_live_run_page(workbench.build_workbench_live_run_page_view(packet))
        workbench.validate_local_workbench_page(html)
        return html_response(200, html, live_run.build_api_response(packet, "create_run"))
    payload = live_run.list_workbench_resolution_runs(_projection_profile(request_context))
    html = workbench.render_workbench_live_run_list_page(workbench.build_workbench_live_run_list_page_view(payload))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, payload)


def _workbench_live_run_detail_response(run_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    try:
        packet = _workbench_live_run().get_workbench_resolution_run(run_id, _projection_profile(request_context))
    except KeyError:
        return error_response(404, "resolution_run_not_found", "resolution run was not found", {"run_id": run_id})
    return json_response(200, _workbench_live_run().build_api_response(packet, "run"))


def _workbench_live_run_detail_html_response(run_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _workbench_live_run_detail_response(run_id, request_context)
    if response.status_code != 200:
        return response
    packet = response.payload["data"]
    html = workbench.render_workbench_live_run_page(workbench.build_workbench_live_run_page_view(packet))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, response.payload)


def _workbench_live_run_events_response(run_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    try:
        payload = _workbench_live_run().get_workbench_run_events(run_id, _projection_profile(request_context))
    except KeyError:
        return error_response(404, "resolution_run_not_found", "resolution run was not found", {"run_id": run_id})
    return json_response(200, payload)


def _workbench_live_run_lanes_response(run_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    try:
        payload = _workbench_live_run().get_workbench_run_lanes(run_id, _projection_profile(request_context))
    except KeyError:
        return error_response(404, "resolution_run_not_found", "resolution run was not found", {"run_id": run_id})
    return json_response(200, payload)


def _workbench_live_run_workunits_response(run_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    try:
        payload = _workbench_live_run().get_workbench_run_workunits(run_id, _projection_profile(request_context))
    except KeyError:
        return error_response(404, "resolution_run_not_found", "resolution run was not found", {"run_id": run_id})
    return json_response(200, payload)


def _workbench_live_run_commands_response(run_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    command_type = first_param(request_context.params, "command", "run_live_source")
    try:
        payload = _workbench_live_run().build_command_response(
            run_id,
            command_type,
            _projection_profile(request_context),
            operator_token=first_param(request_context.params, "operator_token", first_param(request_context.params, "operator-token", "")),
            allow_live=_truthy(first_param(request_context.params, "allow_live", first_param(request_context.params, "allow-live", ""))),
            mock_live=_truthy(first_param(request_context.params, "mock_live", first_param(request_context.params, "mock-live", ""))),
            max_requests=parse_limit(first_param(request_context.params, "max_requests", first_param(request_context.params, "max-requests", "")), default=2),
            rows=parse_limit(first_param(request_context.params, "rows", ""), default=5),
            timeout_seconds=parse_limit(
                first_param(request_context.params, "timeout_seconds", first_param(request_context.params, "timeout-seconds", "")),
                default=15,
            ),
        )
    except KeyError:
        return error_response(404, "resolution_run_not_found", "resolution run was not found", {"run_id": run_id})
    return json_response(200 if payload.get("allowed") else 403, payload)


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
    linked_needs = [item.to_dict() for item in runtime.search_need.list_needs_for_hunt(hunt_id, limit=100)]
    linked_workunits = _search_need_runtime().list_workunits_for_hunt(runtime, hunt_id, limit=100)
    runner_summary = _search_hunt().summarize_background_hunt(runtime, hunt_id)
    agent_tasks = [item.to_dict() for item in runtime.agent_research.list_tasks(hunt_id=hunt_id, limit=100)]
    ai_escalation = _ai_escalation_summary(runtime, hunt_id=hunt_id)
    replay_summary = _hunt_replay_summary(runtime, hunt_id)
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
        "search_needs": linked_needs,
        "workunits": linked_workunits,
        "background_runner": runner_summary,
        "agent_research_tasks": agent_tasks,
        "ai_escalation": ai_escalation,
        "hunt_replay": replay_summary,
        "unavailable_actions": _search_hunt_unavailable_actions_payload(),
        "read_only": True,
        "hunt_creation_enabled": False,
        "hunt_transition_enabled": True,
        "command_controls_enabled": not bool(getattr(runtime, "read_only", True)),
        "steering_controls_enabled": not bool(getattr(runtime, "read_only", True)),
        "exhaustion_report_generation_enabled": not bool(getattr(runtime, "read_only", True)),
        "search_need_creation_enabled": not bool(getattr(runtime, "read_only", True)),
        "operator_token_required_for_mutations": True,
        "localhost_only_mutations": True,
        "lan_command_mutations_enabled": False,
        "workunit_creation_enabled": True,
        "workunit_execution_enabled": False,
        "background_hunt_runner_enabled": True,
        "hunt_replay_enabled": True,
        "replay_controls_enabled": not bool(getattr(runtime, "read_only", True)),
        "agent_research_task_draft_enabled": not bool(getattr(runtime, "read_only", True)),
        "agent_research_provider_enabled": False,
        "agent_research_execution_enabled": False,
        "ai_escalation_preflight_enabled": not bool(getattr(runtime, "read_only", True)),
        "ai_escalation_provider_enabled": False,
        "ai_escalation_execution_enabled": False,
        "workunit_execution_enabled_for_safe_workers": True,
        "runner_controls_enabled": not bool(getattr(runtime, "read_only", True)),
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
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


def _hunt_needs_response(runtime: Any, hunt_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    needs = [item.to_dict() for item in runtime.search_need.list_needs_for_hunt(hunt_id, limit=limit)]
    payload = {
        "schema_version": "search_need_hunt_needs_response.v0",
        "status": "pass",
        "hunt_id": hunt_id,
        "need_count": len(needs),
        "needs": needs,
        "read_only": True,
        "workunit_creation_enabled": False,
        "source_probe_execution_enabled": False,
        "model_provider_enabled": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["SearchNeeds are local demand state only"],
    }
    return json_response(200, payload)


def _hunt_workunits_response(runtime: Any, hunt_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    workunits = _search_need_runtime().list_workunits_for_hunt(runtime, hunt_id, limit=limit)
    payload = {
        "schema_version": "hunt_workunits_response.v0",
        "status": "pass",
        "hunt_id": hunt_id,
        "workunit_count": len(workunits),
        "workunits": workunits,
        "read_only": True,
        "workunit_execution_enabled": False,
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
        "model_provider_enabled": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["WorkUnits are local queue records and are not executed by this route"],
    }
    return json_response(200, payload)


def _hunt_runner_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    summary = _search_hunt().summarize_background_hunt(runtime, hunt_id)
    payload = _background_hunt_runner_payload(
        "background_hunt_runner_status",
        {
            "hunt_id": hunt_id,
            "runner": summary,
            "plan": summary.get("plan"),
            "latest_run": summary.get("latest_run"),
            "runs": summary.get("runs", []),
            "read_only": True,
            "workunit_execution_enabled_for_safe_workers": True,
            "runner_execution_performed": False,
        },
    )
    return json_response(200, payload)


def _hunt_replay_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    payload = _hunt_replay_payload(
        "hunt_replay_status",
        {
            "hunt_id": hunt_id,
            "replay": _hunt_replay_summary(runtime, hunt_id),
            "read_only": True,
            "replay_run_performed": False,
        },
    )
    return json_response(200, payload)


def _hunt_agent_tasks_response(runtime: Any, hunt_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    tasks = [item.to_dict() for item in runtime.agent_research.list_tasks(hunt_id=hunt_id, limit=limit)]
    payload = _agent_research_payload(
        "agent_research_tasks_for_hunt",
        {
            "hunt_id": hunt_id,
            "task_count": len(tasks),
            "agent_research_tasks": tasks,
            "read_only": True,
            "draft_creation_enabled": not bool(getattr(runtime, "read_only", True)),
            "task_execution_enabled": False,
        },
    )
    return json_response(200, payload)


def _hunt_ai_escalation_response(runtime: Any, hunt_id: str) -> LocalServiceResponse:
    if not hunt_id:
        return error_response(400, "missing_hunt_id", "hunt id is required")
    session = runtime.search_hunt.get_session(hunt_id)
    if session is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    payload = _ai_escalation_payload(
        "ai_escalation_for_hunt",
        {
            "hunt_id": hunt_id,
            "ai_escalation": _ai_escalation_summary(runtime, hunt_id=hunt_id),
            "read_only": True,
        },
    )
    return json_response(200, payload)


def _need_list_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    state = first_param(request_context.params, "state", "")
    kind = first_param(request_context.params, "kind", "")
    needs = [
        item.to_dict()
        for item in runtime.search_need.list_needs(state=state or None, kind=kind or None, limit=limit)
    ]
    payload = {
        "schema_version": "search_need_list_response.v0",
        "status": "pass",
        "need_count": len(needs),
        "needs": needs,
        "search_need_creation_enabled": True,
        "workunit_creation_enabled": True,
        "workunit_execution_enabled": False,
        "source_probe_execution_enabled": False,
        "model_provider_enabled": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["SearchNeeds are local demand state only"],
    }
    return json_response(200, payload)


def _need_list_html_response(runtime: Any, request_context: LocalRequestContext) -> LocalServiceResponse:
    workbench = _workbench()
    response = _need_list_response(runtime, request_context)
    html = workbench.render_search_need_list_page(workbench.build_search_need_list_page_view(response.payload["needs"], response.payload))
    workbench.validate_local_workbench_page(html)
    return html_response(200, html, response.payload)


def _need_detail_response(runtime: Any, need_id: str) -> LocalServiceResponse:
    if not need_id:
        return error_response(400, "missing_need_id", "SearchNeed id is required")
    need = runtime.search_need.get_need(need_id)
    if need is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    transitions = [item.to_dict() for item in runtime.search_need.list_transitions(need_id, limit=100)]
    workunit_module = _search_need_runtime()
    plan = workunit_module.build_workunit_plan_for_need(runtime, need_id)
    workunits = workunit_module.list_workunits_for_need(runtime, need_id, limit=100)
    agent_tasks = [item.to_dict() for item in runtime.agent_research.list_tasks(need_id=need_id, limit=100)]
    ai_escalation = _ai_escalation_summary(runtime, hunt_id=need.hunt_id, need_id=need_id)
    payload = {
        "schema_version": "search_need_detail_response.v0",
        "status": "pass",
        "need_id": need_id,
        "need": need.to_dict(),
        "transitions": transitions,
        "workunit_plan": plan.to_dict(),
        "workunits": workunits,
        "agent_research_tasks": agent_tasks,
        "ai_escalation": ai_escalation,
        "state_transition_enabled": not bool(getattr(runtime, "read_only", True)),
        "workunit_creation_enabled": not bool(getattr(runtime, "read_only", True)),
        "agent_research_task_draft_enabled": not bool(getattr(runtime, "read_only", True)),
        "agent_research_provider_enabled": False,
        "agent_research_execution_enabled": False,
        "ai_escalation_preflight_enabled": not bool(getattr(runtime, "read_only", True)),
        "ai_escalation_provider_enabled": False,
        "ai_escalation_execution_enabled": False,
        "workunit_execution_enabled": False,
        "operator_token_required_for_mutations": True,
        "localhost_only_mutations": True,
        "lan_mutations_enabled": False,
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
        "model_provider_enabled": False,
        "review_mutation_enabled": False,
        "public_index_mutation_enabled": False,
        "master_index_mutation_enabled": False,
        "warnings": list(need.warnings),
        "limitations": list(DEFAULT_LIMITATIONS) + list(need.policy_limitations),
    }
    return json_response(200, payload)


def _need_workunits_response(runtime: Any, need_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    if not need_id:
        return error_response(400, "missing_need_id", "SearchNeed id is required")
    need = runtime.search_need.get_need(need_id)
    if need is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    workunits = _search_need_runtime().list_workunits_for_need(runtime, need_id, limit=limit)
    payload = {
        "schema_version": "search_need_workunits_response.v0",
        "status": "pass",
        "need_id": need_id,
        "workunit_count": len(workunits),
        "workunits": workunits,
        "read_only": True,
        "workunit_execution_enabled": False,
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
        "model_provider_enabled": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["WorkUnits linked to a SearchNeed are local queue records only"],
    }
    return json_response(200, payload)


def _need_agent_tasks_response(runtime: Any, need_id: str, request_context: LocalRequestContext) -> LocalServiceResponse:
    if not need_id:
        return error_response(400, "missing_need_id", "SearchNeed id is required")
    need = runtime.search_need.get_need(need_id)
    if need is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    limit = parse_limit(first_param(request_context.params, "limit", ""), default=100)
    tasks = [item.to_dict() for item in runtime.agent_research.list_tasks(need_id=need_id, limit=limit)]
    payload = _agent_research_payload(
        "agent_research_tasks_for_need",
        {
            "need_id": need_id,
            "hunt_id": need.hunt_id,
            "task_count": len(tasks),
            "agent_research_tasks": tasks,
            "read_only": True,
            "draft_creation_enabled": not bool(getattr(runtime, "read_only", True)),
            "task_execution_enabled": False,
        },
    )
    return json_response(200, payload)


def _need_ai_escalation_response(runtime: Any, need_id: str) -> LocalServiceResponse:
    if not need_id:
        return error_response(400, "missing_need_id", "SearchNeed id is required")
    need = runtime.search_need.get_need(need_id)
    if need is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    payload = _ai_escalation_payload(
        "ai_escalation_for_need",
        {
            "need_id": need_id,
            "hunt_id": need.hunt_id,
            "ai_escalation": _ai_escalation_summary(runtime, hunt_id=need.hunt_id, need_id=need_id),
            "read_only": True,
        },
    )
    return json_response(200, payload)


def _agent_research_report_schema_response(runtime: Any) -> LocalServiceResponse:
    schema = _agent_research().build_agent_research_report_schema().to_dict()
    payload = _agent_research_payload(
        "agent_research_report_schema",
        {
            "report_schema": schema,
            "read_only": True,
            "report_output_candidate_only": True,
            "review_required": True,
        },
    )
    return json_response(200, payload)


def _need_detail_html_response(runtime: Any, need_id: str) -> LocalServiceResponse:
    workbench = _workbench()
    response = _need_detail_response(runtime, need_id)
    if response.status_code != 200:
        return response
    html = workbench.render_search_need_detail_page(
        workbench.build_search_need_detail_page_view(
            response.payload["need"],
            response.payload["transitions"],
            response.payload,
        )
    )
    workbench.validate_local_workbench_page(html, allow_operator_mutation_forms=True)
    return html_response(response.status_code, html, response.payload)


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


def _workbench_review_promote_response(request_context: LocalRequestContext, endpoint: str = "promotion") -> LocalServiceResponse:
    payload = _workbench_review_promote().run_review_promote_flow(
        decision=first_param(request_context.params, "decision", "accept_local_reviewed"),
        projection_profile=_projection_profile(request_context),
        dry_run=True,
    )
    payload["endpoint"] = endpoint
    return json_response(200, payload)


def _local_apply_preview_response(request_context: LocalRequestContext, endpoint: str = "local_apply_preview") -> LocalServiceResponse:
    target = first_param(request_context.params, "instance", "")
    payload = _local_apply().build_local_apply_preview(target_instance=target or None)
    payload.update(
        {
            "endpoint": endpoint,
            "operator_projection": True,
            "public_projection_blocked": True,
            "native_read_only_projection_blocked": True,
            "api_apply_enabled": False,
            "cli_apply_gate_required": True,
        }
    )
    return json_response(200, payload)


def _local_apply_plan_response(request_context: LocalRequestContext) -> LocalServiceResponse:
    target = first_param(request_context.body_params, "instance", first_param(request_context.params, "instance", ""))
    preview = _local_apply().build_local_apply_preview(target_instance=target or None)
    plan = _local_apply().build_local_apply_plan(
        preview,
        target or "",
        {
            "apply": False,
            "operator_token_present": bool(first_param(request_context.body_params, "operator_token", "")),
            "confirmation": first_param(request_context.body_params, "confirm", ""),
        },
    )
    return json_response(
        200,
        {
            "schema_version": "local_apply_api_plan_response.v0",
            "status": "pass" if plan.get("status") in {"preview_created", "apply_ready"} else "blocked",
            "preview": preview,
            "plan": plan,
            "apply_performed": False,
            "public_projection_blocked": True,
            "native_read_only_projection_blocked": True,
            "cli_apply_gate_required": True,
        },
    )


def _local_apply_audit_response(request_context: LocalRequestContext) -> LocalServiceResponse:
    return json_response(
        200,
        {
            "schema_version": "local_apply_api_audit_response.v0",
            "status": "pass",
            "audit_endpoint_reserved": True,
            "instance_path_required_for_records": True,
            "raw_token_stored": False,
            "public_projection_blocked": True,
            "native_read_only_projection_blocked": True,
        },
    )


def _local_apply_html_response(request_context: LocalRequestContext) -> LocalServiceResponse:
    payload = _local_apply().build_local_apply_preview(target_instance=first_param(request_context.params, "instance", "") or None)
    html = (
        "<!doctype html><title>Eureka Local Apply</title><main><h1>Local Apply</h1><pre>"
        + _html().escape(json.dumps(payload, indent=2, sort_keys=True))
        + "</pre></main>"
    )
    return html_response(200, html, {"schema_version": "local_apply_html_response.v0", "status": payload.get("status", "preview_created")})


def _workbench_review_promote_html_response(request_context: LocalRequestContext, endpoint: str = "promotion") -> LocalServiceResponse:
    response = _workbench_review_promote_response(request_context, endpoint=endpoint)
    payload = response.payload
    html = "\n".join(
        [
            "<!doctype html><html><head><meta charset=\"utf-8\"><title>Promotion preview</title></head><body>",
            "<h1>Promotion preview</h1>",
            "<p>Promotion preview is operator-gated local review state only.</p>",
            f"<p>Review item: {payload.get('review_item', {}).get('review_item_id', '')}</p>",
            f"<p>Promotion preview: {payload.get('promotion_preview', {}).get('preview_id', '')}</p>",
            "<p><a href=\"/review\">Review queue</a> | <a href=\"/api/v1/promotion-preview\">JSON promotion preview</a></p>",
            "</body></html>",
        ]
    )
    return html_response(200, html, payload)


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
    path = request_context.path
    if not _mutation_route_allows_missing_token(path):
        try:
            _require_operator_token(request_context, runtime.config, operator_auth_state)
        except _operator_auth_error() as exc:
            if path.startswith("/explore/"):
                query = first_param(request_context.body_params, "q", first_param(request_context.body_params, "query", ""))
                html = _explore_html().render_explore_error_html(
                    "Hunt Could Not Start",
                    "The local start token was missing or incorrect.",
                    query=query,
                )
                _workbench().validate_local_workbench_page(html, allow_operator_mutation_forms=True)
                return html_response(401, html, {"schema_version": "local_http_explore_error_response.v0", "status": "fail"})
            return error_response(401, "operator_token_required", str(exc))
    explore_mutation = _parse_explore_mutation_path(path)
    if explore_mutation:
        return _apply_explore_mutation_response(runtime, request_context, explore_mutation[0], explore_mutation[1])
    hunt_mutation = _parse_hunt_mutation_path(path)
    if hunt_mutation:
        if hunt_mutation[1] == "replay-plan":
            return _apply_hunt_replay_plan_response(runtime, request_context, hunt_mutation[0])
        if hunt_mutation[1] == "replay-run":
            return _apply_hunt_replay_run_response(runtime, request_context, hunt_mutation[0])
        if hunt_mutation[1] == "runner-plan":
            return _apply_hunt_runner_plan_response(runtime, request_context, hunt_mutation[0])
        if hunt_mutation[1] == "runner-run-next":
            return _apply_hunt_runner_run_response(runtime, request_context, hunt_mutation[0], mode="run_next")
        if hunt_mutation[1] == "runner-run-batch":
            return _apply_hunt_runner_run_response(runtime, request_context, hunt_mutation[0], mode="run_batch")
        if hunt_mutation[1] == "exhaustion":
            return _apply_hunt_exhaustion_response(runtime, request_context, hunt_mutation[0])
        if hunt_mutation[1] == "search-need":
            return _apply_hunt_search_need_response(runtime, request_context, hunt_mutation[0])
        if hunt_mutation[1] == "agent-task-draft":
            return _apply_hunt_agent_task_draft_response(runtime, request_context, hunt_mutation[0])
        if hunt_mutation[1] == "ai-escalation-preflight":
            return _apply_hunt_ai_escalation_preflight_response(runtime, request_context, hunt_mutation[0])
        return _apply_hunt_command_response(runtime, request_context, hunt_mutation[0], hunt_mutation[1])
    need_mutation = _parse_need_mutation_path(path)
    if need_mutation:
        if need_mutation[1] == "state":
            return _apply_search_need_state_response(runtime, request_context, need_mutation[0])
        if need_mutation[1] == "workunits-plan":
            return _apply_search_need_workunit_plan_response(runtime, request_context, need_mutation[0])
        if need_mutation[1] == "workunits":
            return _apply_search_need_workunit_create_response(runtime, request_context, need_mutation[0])
        if need_mutation[1] == "agent-task-draft":
            return _apply_need_agent_task_draft_response(runtime, request_context, need_mutation[0])
        if need_mutation[1] == "ai-escalation-preflight":
            return _apply_need_ai_escalation_preflight_response(runtime, request_context, need_mutation[0])
    if path.startswith("/api/v1/review/") and path.endswith("/decision"):
        review_item_id = path.removeprefix("/api/v1/review/").removesuffix("/decision").strip("/")
        return _workbench_review_promote_decision_response(request_context, review_item_id)
    if path == "/api/v1/promotion-preview":
        return _workbench_review_promote_decision_response(request_context, first_param(request_context.body_params, "review_item_id", ""))
    if path == "/api/v1/reviewed-index/refresh-preview":
        return _workbench_review_promote_response(request_context, endpoint="reviewed_index_refresh_preview")
    if path in {"/api/v1/local-apply/preview", "/api/v1/local-apply/plan"}:
        return _local_apply_plan_response(request_context)
    if path.startswith("/api/v1/local-apply/") and (path.endswith("/apply") or path.endswith("/rollback")):
        return error_response(
            409,
            "local_apply_cli_required",
            "local apply mutations are reserved for the explicit CLI gate in this build",
            {
                "path": path,
                "operator_token_required": True,
                "exact_apply_confirmation": "APPLY_TO_LOCAL_INSTANCE",
                "exact_rollback_confirmation": "ROLLBACK_LOCAL_INSTANCE",
                "public_projection_blocked": True,
                "native_read_only_projection_blocked": True,
            },
        )
    if path.startswith("/review/") and path.endswith("/decision"):
        review_item_id = path.removeprefix("/review/").removesuffix("/decision").strip("/")
        return _record_decision_response(runtime, request_context, review_item_id)
    if path == "/rebuild":
        return _apply_rebuild_response(runtime, request_context)
    return error_response(404, "route_not_found", "operator mutation route was not found", {"path": path})


def _apply_explore_mutation_response(runtime: Any, request_context: LocalRequestContext, action: str, run_id: str) -> LocalServiceResponse:
    options = _explore().options_from_runtime(runtime)
    if action == "start":
        query = first_param(request_context.body_params, "q", first_param(request_context.body_params, "query", ""))
        fixture = first_param(request_context.body_params, "fixture", options.default_fixture)
        try:
            payload = _explore().start_synthetic_hunt(query, options=options, fixture=fixture)
        except Exception as exc:
            if not _is_api_path(request_context.path):
                html = _explore_html().render_explore_error_html("Hunt Could Not Start", str(exc), query=query)
                _workbench().validate_local_workbench_page(html, allow_operator_mutation_forms=True)
                return html_response(400, html, {"schema_version": "local_http_explore_error_response.v0", "status": "fail"})
            return error_response(400, "explore_start_rejected", str(exc), {"query_present": bool(query.strip())})
        if not _is_api_path(request_context.path):
            return redirect_response("/explore/run/" + quote(str(payload.get("run_id", ""))), status_code=303)
        return json_response(200, payload)
    try:
        payload = _explore().apply_run_control(run_id, action, runs_root=options.runs_root)
    except FileNotFoundError:
        return error_response(404, "explore_run_not_found", "E2E explore run bundle was not found", {"run_id": run_id, "action": action})
    except Exception as exc:
        return error_response(400, "explore_command_rejected", str(exc), {"run_id": run_id, "action": action})
    status_code = 409 if payload.get("status") == "blocked" else 200
    return json_response(status_code, payload)


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


def _apply_hunt_search_need_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    idempotency_key = first_param(request_context.body_params, "idempotency_key", "")
    try:
        need = runtime.search_need.create_need_from_hunt(
            runtime,
            hunt_id,
            operator_label=operator_label,
            idempotency_key=idempotency_key or None,
        )
    except Exception as exc:
        return error_response(400, "search_need_creation_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _search_need_mutation_payload(
        "search_need_created_from_hunt",
        {"hunt_id": hunt_id, "need": need.to_dict()},
    )
    return json_response(200, payload)


def _apply_search_need_state_response(runtime: Any, request_context: LocalRequestContext, need_id: str) -> LocalServiceResponse:
    if runtime.search_need.get_need(need_id) is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    target_state = first_param(request_context.body_params, "state", "")
    reason = first_param(request_context.body_params, "reason", "")
    if not target_state:
        return error_response(400, "missing_search_need_state", "state is required", {"need_id": need_id})
    try:
        need = runtime.search_need.transition_need(need_id, target_state, reason=reason)
    except Exception as exc:
        return error_response(400, "search_need_transition_rejected", str(exc), {"need_id": need_id})
    payload = _search_need_mutation_payload(
        "search_need_state_transitioned",
        {"need_id": need_id, "need": need.to_dict()},
    )
    return json_response(200, payload)


def _apply_search_need_workunit_plan_response(runtime: Any, request_context: LocalRequestContext, need_id: str) -> LocalServiceResponse:
    if runtime.search_need.get_need(need_id) is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    try:
        plan = _search_need_runtime().build_workunit_plan_for_need(runtime, need_id, operator_label=operator_label)
    except Exception as exc:
        return error_response(400, "workunit_plan_rejected", str(exc), {"need_id": need_id})
    payload = _search_need_workunit_payload(
        "search_need_workunit_plan_generated",
        {
            "need_id": need_id,
            "plan": plan.to_dict(),
            "workunit_persistence_performed": False,
            "workunit_creation_performed": False,
        },
    )
    return json_response(200, payload)


def _apply_search_need_workunit_create_response(runtime: Any, request_context: LocalRequestContext, need_id: str) -> LocalServiceResponse:
    if runtime.search_need.get_need(need_id) is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    idempotency_key = first_param(request_context.body_params, "idempotency_key", "")
    try:
        result = _search_need_runtime().create_workunits_from_need(
            runtime,
            need_id,
            operator_label=operator_label,
            idempotency_key=idempotency_key or None,
        )
    except Exception as exc:
        return error_response(400, "workunit_creation_rejected", str(exc), {"need_id": need_id})
    payload = _search_need_workunit_payload(
        "search_need_workunits_created",
        {
            "need_id": need_id,
            "result": result.to_dict(),
            "workunit_count": result.created_count,
            "workunits": list(result.workunits),
            "workunit_creation_performed": True,
        },
    )
    return json_response(200, payload)


def _apply_hunt_agent_task_draft_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    try:
        task = runtime.agent_research.draft_task_from_hunt(
            runtime,
            hunt_id,
            operator_label=first_param(request_context.body_params, "operator_label", "local_operator"),
        )
    except Exception as exc:
        return error_response(400, "agent_research_task_draft_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _agent_research_payload(
        "agent_research_task_drafted_from_hunt",
        {
            "hunt_id": hunt_id,
            "agent_research_task": task.to_dict(),
            "task_execution_performed": False,
        },
    )
    return json_response(200, payload)


def _apply_need_agent_task_draft_response(runtime: Any, request_context: LocalRequestContext, need_id: str) -> LocalServiceResponse:
    if runtime.search_need.get_need(need_id) is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    try:
        task = runtime.agent_research.draft_task_from_need(
            runtime,
            need_id,
            operator_label=first_param(request_context.body_params, "operator_label", "local_operator"),
        )
    except Exception as exc:
        return error_response(400, "agent_research_task_draft_rejected", str(exc), {"need_id": need_id})
    payload = _agent_research_payload(
        "agent_research_task_drafted_from_need",
        {
            "need_id": need_id,
            "hunt_id": task.search_hunt_id,
            "agent_research_task": task.to_dict(),
            "task_execution_performed": False,
        },
    )
    return json_response(200, payload)


def _apply_hunt_ai_escalation_preflight_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    try:
        preflight = _ai_escalation().build_ai_escalation_preflight(runtime, hunt_id=hunt_id, operator_label=operator_label)
        written = runtime.ai_escalation.write_preflight(preflight)
    except Exception as exc:
        return error_response(400, "ai_escalation_preflight_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _ai_escalation_payload(
        "ai_escalation_preflight_from_hunt",
        {
            "hunt_id": hunt_id,
            "preflight": written.to_dict(),
            "ai_escalation": _ai_escalation_summary(runtime, hunt_id=hunt_id),
            "preflight_written": True,
            "provider_call_performed": False,
        },
    )
    return json_response(200, payload)


def _apply_need_ai_escalation_preflight_response(runtime: Any, request_context: LocalRequestContext, need_id: str) -> LocalServiceResponse:
    need = runtime.search_need.get_need(need_id)
    if need is None:
        return error_response(404, "search_need_not_found", "SearchNeed was not found", {"need_id": need_id})
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    try:
        preflight = _ai_escalation().build_ai_escalation_preflight(runtime, need_id=need_id, operator_label=operator_label)
        written = runtime.ai_escalation.write_preflight(preflight)
    except Exception as exc:
        return error_response(400, "ai_escalation_preflight_rejected", str(exc), {"need_id": need_id})
    payload = _ai_escalation_payload(
        "ai_escalation_preflight_from_need",
        {
            "need_id": need_id,
            "hunt_id": need.hunt_id,
            "preflight": written.to_dict(),
            "ai_escalation": _ai_escalation_summary(runtime, hunt_id=need.hunt_id, need_id=need_id),
            "preflight_written": True,
            "provider_call_performed": False,
        },
    )
    return json_response(200, payload)


def _apply_hunt_runner_plan_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    limit = parse_limit(first_param(request_context.body_params, "limit", ""), default=10)
    try:
        plan = _search_hunt().build_background_hunt_plan(runtime, hunt_id, limit=limit)
    except Exception as exc:
        return error_response(400, "background_hunt_plan_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _background_hunt_runner_payload(
        "background_hunt_runner_plan",
        {
            "hunt_id": hunt_id,
            "plan": plan.to_dict(),
            "runner_execution_performed": False,
        },
    )
    return json_response(200, payload)


def _apply_hunt_runner_run_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str, *, mode: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    limit = parse_limit(first_param(request_context.body_params, "limit", ""), default=1)
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    context = {
        "authorized": True,
        "operator_label": operator_label,
        "raw_token_stored": False,
    }
    try:
        if mode == "run_next":
            result = _search_hunt().run_next_hunt_workunit(runtime, hunt_id, operator_context=context)
        else:
            result = _search_hunt().run_background_hunt_batch(runtime, hunt_id, limit=limit, operator_context=context)
    except Exception as exc:
        return error_response(400, "background_hunt_run_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _background_hunt_runner_payload(
        "background_hunt_runner_" + mode,
        {
            "hunt_id": hunt_id,
            "result": result.to_dict(),
            "run": result.run.to_dict(),
            "plan": result.plan.to_dict(),
            "runner_execution_performed": True,
        },
    )
    return json_response(200, payload)


def _apply_hunt_replay_plan_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    try:
        fixture = _search_hunt().build_replay_plan_from_hunt(runtime, hunt_id)
        result = _search_hunt().run_hunt_replay(runtime, fixture, mode="plan_only")
    except Exception as exc:
        return error_response(400, "hunt_replay_plan_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _hunt_replay_payload(
        "hunt_replay_plan",
        {
            "hunt_id": hunt_id,
            "fixture": fixture.to_dict(),
            "plan": result.to_dict(),
            "replay_run_performed": False,
        },
    )
    return json_response(200, payload)


def _apply_hunt_replay_run_response(runtime: Any, request_context: LocalRequestContext, hunt_id: str) -> LocalServiceResponse:
    if runtime.search_hunt.get_session(hunt_id) is None:
        return error_response(404, "hunt_not_found", "Search Hunt session was not found", {"hunt_id": hunt_id})
    operator_label = first_param(request_context.body_params, "operator_label", "local_operator")
    context = {
        "authorized": True,
        "operator_label": operator_label,
        "raw_token_stored": False,
    }
    try:
        fixture = _search_hunt().build_replay_fixture_from_hunt(runtime, hunt_id)
        result = _search_hunt().run_hunt_replay(runtime, fixture, operator_context=context, mode="replay_local")
    except Exception as exc:
        return error_response(400, "hunt_replay_run_rejected", str(exc), {"hunt_id": hunt_id})
    payload = _hunt_replay_payload(
        "hunt_replay_run",
        {
            "hunt_id": hunt_id,
            "fixture": fixture.to_dict(),
            "result": result.to_dict(),
            "record": result.record.to_dict(),
            "replay_run_performed": True,
        },
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


def _workbench_review_promote_decision_response(request_context: LocalRequestContext, review_item_id: str) -> LocalServiceResponse:
    params = request_context.body_params
    payload = _workbench_review_promote().run_review_promote_flow(
        candidate=first_param(params, "candidate_id", "") or None,
        decision=first_param(params, "decision", "accept_local_reviewed"),
        projection_profile=_projection_profile(request_context),
        operator_token=first_param(params, "operator_token", ""),
        dry_run=False,
    )
    payload["requested_review_item_id"] = review_item_id
    return json_response(200 if payload.get("review_decision", {}).get("allowed") else 403, payload)


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


def _live_search_enabled(runtime: Any) -> bool:
    return bool(getattr(runtime, "live_search_enabled", False))


def _service_limitations(runtime: Any) -> list[str]:
    if _live_search_enabled(runtime):
        return [
            "local Preview Index plus opt-in live provider search",
            "loopback-only service",
            "live provider leads are transient unless later fetched and indexed under policy",
        ]
    return list(DEFAULT_LIMITATIONS)


def _is_api_path(path: str) -> bool:
    return str(path or "").startswith("/api/v1/")


def _route_allowed_for_scope(method: str, path: str, client_scope: object) -> bool:
    if _is_operator_mutation_path(method, path):
        return str(getattr(client_scope, "value", client_scope) or "").lower() == "loopback"
    return _network().is_route_allowed_for_scope(method, path, client_scope)


def _is_operator_mutation_path(method: str, path: str) -> bool:
    return str(method or "").upper() == "POST" and (
        _parse_explore_mutation_path(path) is not None
        or _parse_hunt_mutation_path(path) is not None
        or _parse_need_mutation_path(path) is not None
        or (path.startswith("/api/v1/review/") and path.endswith("/decision"))
        or path in {"/api/v1/promotion-preview", "/api/v1/reviewed-index/refresh-preview"}
        or _is_local_apply_api_mutation_path(path)
    )


def _is_local_apply_api_mutation_path(path: str) -> bool:
    value = str(path or "")
    if value in {"/api/v1/local-apply/preview", "/api/v1/local-apply/plan"}:
        return True
    return value.startswith("/api/v1/local-apply/") and (value.endswith("/apply") or value.endswith("/rollback"))


def _parse_explore_run_route(path: str) -> str | None:
    parts = [part for part in str(path or "").split("/") if part]
    if len(parts) == 3 and parts[:2] == ["explore", "run"]:
        return parts[2]
    if len(parts) == 5 and parts[:4] == ["api", "v1", "explore", "run"]:
        return parts[4]
    return None


def _parse_explore_mutation_path(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    actions = {"pause", "resume", "cancel", "step", "advance", "replay"}
    if parts == ["explore", "run", "start"]:
        return "start", ""
    if parts == ["api", "v1", "explore", "run", "start"]:
        return "start", ""
    if len(parts) == 4 and parts[:2] == ["explore", "run"] and parts[3] in actions:
        return parts[3], parts[2]
    if len(parts) == 6 and parts[:4] == ["api", "v1", "explore", "run"] and parts[5] in actions:
        return parts[5], parts[4]
    return None


def _parse_hunt_route(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    if len(parts) == 3 and parts[0] == "hunt" and parts[2] in {"commands", "steering", "exhaustion", "needs", "workunits", "runner", "agent-tasks", "replay", "ai-escalation"}:
        return parts[1], parts[2]
    if len(parts) == 5 and parts[:3] == ["api", "v1", "hunt"] and parts[4] in {"commands", "steering", "exhaustion", "needs", "workunits", "runner", "agent-tasks", "replay", "ai-escalation"}:
        return parts[3], parts[4]
    return None


def _parse_hunt_mutation_path(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    actions = {"pause", "resume", "cancel", "block", "wait-for-user", "wait-for-policy", "steer", "exhaustion", "search-need", "agent-task-draft"}
    if len(parts) == 3 and parts[0] == "hunt" and parts[2] in actions:
        return parts[1], parts[2]
    if len(parts) == 4 and parts[0] == "hunt" and parts[2] == "runner" and parts[3] in {"plan", "run-next", "run-batch"}:
        return parts[1], "runner-" + parts[3]
    if len(parts) == 4 and parts[0] == "hunt" and parts[2] == "replay" and parts[3] in {"plan", "run"}:
        return parts[1], "replay-" + parts[3]
    if len(parts) == 4 and parts[0] == "hunt" and parts[2] == "ai-escalation" and parts[3] == "preflight":
        return parts[1], "ai-escalation-preflight"
    if len(parts) == 5 and parts[:3] == ["api", "v1", "hunt"] and parts[4] in {"exhaustion", "search-need", "agent-task-draft"}:
        return parts[3], parts[4]
    if len(parts) == 6 and parts[:3] == ["api", "v1", "hunt"] and parts[4] == "runner" and parts[5] in {"plan", "run-next", "run-batch"}:
        return parts[3], "runner-" + parts[5]
    if len(parts) == 6 and parts[:3] == ["api", "v1", "hunt"] and parts[4] == "replay" and parts[5] in {"plan", "run"}:
        return parts[3], "replay-" + parts[5]
    if len(parts) == 6 and parts[:3] == ["api", "v1", "hunt"] and parts[4] == "ai-escalation" and parts[5] == "preflight":
        return parts[3], "ai-escalation-preflight"
    return None


def _mutation_route_allows_missing_token(path: str) -> bool:
    parsed = _parse_hunt_mutation_path(path)
    return bool(parsed and parsed[1] in {"runner-plan", "replay-plan"})


def _parse_need_mutation_path(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    if len(parts) == 3 and parts[0] == "need" and parts[2] in {"state", "workunits", "agent-task-draft"}:
        return parts[1], parts[2]
    if len(parts) == 4 and parts[0] == "need" and parts[2] == "ai-escalation" and parts[3] == "preflight":
        return parts[1], "ai-escalation-preflight"
    if len(parts) == 4 and parts[0] == "need" and parts[2:] == ["workunits", "plan"]:
        return parts[1], "workunits-plan"
    if len(parts) == 5 and parts[:3] == ["api", "v1", "need"] and parts[4] in {"state", "workunits", "agent-task-draft"}:
        return parts[3], parts[4]
    if len(parts) == 6 and parts[:3] == ["api", "v1", "need"] and parts[4] == "ai-escalation" and parts[5] == "preflight":
        return parts[3], "ai-escalation-preflight"
    if len(parts) == 6 and parts[:3] == ["api", "v1", "need"] and parts[4:] == ["workunits", "plan"]:
        return parts[3], "workunits-plan"
    return None


def _parse_need_route(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    if len(parts) == 3 and parts[0] == "need" and parts[2] in {"workunits", "agent-tasks", "ai-escalation"}:
        return parts[1], parts[2]
    if len(parts) == 5 and parts[:3] == ["api", "v1", "need"] and parts[4] in {"workunits", "agent-tasks", "ai-escalation"}:
        return parts[3], parts[4]
    return None


def _parse_workbench_live_run_route(path: str) -> tuple[str, str] | None:
    parts = [part for part in str(path or "").split("/") if part]
    if len(parts) == 2 and parts[0] == "runs":
        return parts[1], "detail"
    if len(parts) == 3 and parts[0] == "runs" and parts[2] in {"events", "lanes", "workunits", "commands"}:
        return parts[1], parts[2]
    if len(parts) == 4 and parts[:3] == ["api", "v1", "resolution-runs"]:
        return parts[3], "detail"
    if len(parts) == 5 and parts[:3] == ["api", "v1", "resolution-runs"] and parts[4] in {"events", "lanes", "workunits", "commands"}:
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


def _search_need_mutation_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "search_need_mutation_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required": True,
        "localhost_only_mutations": True,
        "lan_mutations_enabled": False,
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
        "limitations": list(DEFAULT_LIMITATIONS) + ["SearchNeed routes mutate local demand state only"],
    }
    result.update(payload)
    return result


def _search_need_workunit_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "search_need_workunit_route_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required": True,
        "localhost_only_mutations": True,
        "lan_mutations_enabled": False,
        "workunit_execution_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS) + ["WorkUnit routes create local queue records only"],
    }
    result.update(payload)
    return result


def _agent_research_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "agent_research_route_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required_for_drafts": True,
        "localhost_only_mutations": True,
        "lan_mutations_enabled": False,
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "source_probe_enabled": False,
        "output_candidate_only": True,
        "review_required": True,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS)
        + [
            "agent research task records are disabled future escalation contracts",
            "agent research reports would be candidate material only",
            "no provider, browser, source probe, review, or index mutation is performed",
        ],
    }
    result.update(payload)
    return result


def _ai_escalation_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "ai_escalation_route_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required_for_preflight": True,
        "localhost_only_mutations": True,
        "lan_mutations_enabled": False,
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "source_probe_enabled": False,
        "extraction_enabled": False,
        "output_candidate_only": True,
        "review_required": True,
        "execute_route_exists": False,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS)
        + [
            "AI escalation is a disabled future gate",
            "preflight records local readiness only",
            "future output would be candidate material only and review-required",
            "provider, browser, source probe, extraction, review, and index mutation are disabled",
        ],
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
            "status": "available",
            "reason": "Operator-gated command controls update local Search Hunt state only.",
        },
        {
            "action": "exhaustion report",
            "status": "available",
            "reason": "Reports explain local checked layers and deferred work without executing it.",
        },
        {
            "action": "SearchNeed pipeline",
            "status": "available",
            "reason": "SearchNeeds can be created from unresolved hunts without creating work.",
        },
        {
            "action": "WorkUnit pipeline",
            "status": "available",
            "reason": "SearchNeeds can create linked WorkUnits without executing them.",
        },
        {
            "action": "background runner",
            "status": "available",
            "reason": "The runner can process safe deterministic local WorkUnits only.",
        },
        {
            "action": "agent research task drafts",
            "status": "disabled",
            "reason": "Disabled task records are visible, but providers and execution are not enabled.",
        },
        {
            "action": "hunt replay",
            "status": "available",
            "reason": "Replay can plan and rerun deterministic local workflow steps while future actions remain blocked.",
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
    return __import__("surfaces.web.workbench.local_html", fromlist=["build_home_page_view"])


def _workbench_live_run() -> Any:
    return __import__("runtime.local_service.workbench_live_run", fromlist=["create_workbench_resolution_run"])


def _preview_index() -> Any:
    return __import__("runtime.index.preview", fromlist=["search_preview_index"])


def _explore() -> Any:
    return __import__("runtime.local.e2e_hunt_exploration", fromlist=["build_explore_workspace"])


def _explore_html() -> Any:
    return __import__("surfaces.web.workbench.render_e2e_hunt_exploration", fromlist=["render_explore_workspace_html"])


def _workbench_review_promote() -> Any:
    return __import__("runtime.local_service.workbench_review_promote", fromlist=["run_review_promote_flow"])


def _projection_profile(request_context: LocalRequestContext) -> str:
    return first_param(request_context.params, "projection", first_param(request_context.params, "projection_profile", "operator_workbench"))


def _include_ia_hunt_dry_run(request_context: LocalRequestContext) -> bool:
    value = first_param(request_context.params, "include_ia_hunt_dry_run", first_param(request_context.params, "include-ia-hunt-dry-run", "true")).lower()
    return value not in {"0", "false", "no", "off"}


def _truthy(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _review_service() -> Any:
    return __import__("runtime.local_review", fromlist=["list_review_items"])


def _operator_auth() -> Any:
    return __import__("runtime.local_operator", fromlist=["require_operator_token"])


def _operator_auth_error() -> Any:
    return getattr(_operator_auth(), "LocalOperatorAuthError")


def _require_operator_token(request_context: LocalRequestContext, config: Any, operator_auth_state: Any) -> Any:
    return _operator_auth().require_operator_token(request_context, config, operator_auth_state)


def _local_apply() -> Any:
    return __import__("runtime.local.apply", fromlist=["build_local_apply_preview"])


def _html() -> Any:
    return __import__("html", fromlist=["escape"])


def _lan_warnings() -> list[str]:
    module = _network()
    return [module.build_lan_warning(), module.build_firewall_warning()]


def _network() -> Any:
    return __import__("runtime.local_network", fromlist=["is_route_allowed_for_scope", "build_lan_warning"])


def _search_hunt() -> Any:
    return __import__("runtime.search_hunt", fromlist=["build_hunt_exhaustion_report", "build_background_hunt_plan"])


def _search_need_runtime() -> Any:
    return __import__("runtime.search_need", fromlist=["build_workunit_plan_for_need"])


def _agent_research() -> Any:
    return __import__("runtime.agent_research", fromlist=["build_agent_research_report_schema"])


def _ai_escalation() -> Any:
    return __import__("runtime.ai_escalation", fromlist=["build_ai_escalation_preflight"])


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


def _background_hunt_runner_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "background_hunt_runner_response.v0",
        "status": "pass",
        "action": action,
        "operator_token_required_for_execution": True,
        "localhost_only_execution": True,
        "lan_execution_enabled": False,
        "workunit_execution_enabled_for_safe_workers": True,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "review_mutation_performed": False,
        "public_index_mutated_except_allowed_rebuild_worker": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS)
        + [
            "background hunt runner uses deterministic local workers only",
            "policy-blocked WorkUnits remain blocked",
        ],
    }
    result.update(payload)
    return result


def _hunt_replay_summary(runtime: Any, hunt_id: str) -> dict[str, Any]:
    fixture = _search_hunt().build_replay_plan_from_hunt(runtime, hunt_id)
    plan = _search_hunt().run_hunt_replay(runtime, fixture, mode="plan_only")
    records = [item.to_dict() for item in runtime.search_hunt.list_replay_results(hunt_id=hunt_id, limit=20)]
    latest = records[0] if records else None
    return {
        "schema_version": "hunt_replay_summary.v0",
        "hunt_id": hunt_id,
        "fixture": fixture.to_dict(),
        "plan": plan.to_dict(),
        "latest_result": latest,
        "results": records,
        "result_count": len(records),
        "blocked_step_count": len(fixture.blocked_steps),
        "expected_step_count": len(fixture.expected_steps),
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _hunt_replay_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "hunt_replay_response.v0",
        "status": "pass",
        "action": action,
        "operator_token_required_for_run": True,
        "localhost_only_run": True,
        "lan_replay_run_enabled": False,
        "plan_only_enabled": True,
        "replay_local_enabled": True,
        "verify_existing_enabled": True,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": list(DEFAULT_LIMITATIONS)
        + [
            "hunt replay is for local reproducibility and audit only",
            "blocked future actions remain blocked",
            "replay is not truth, evidence acceptance, or broad absence proof",
        ],
    }
    result.update(payload)
    return result


def _ai_escalation_summary(runtime: Any, *, hunt_id: str | None = None, need_id: str | None = None) -> dict[str, Any]:
    eligibility = _ai_escalation().evaluate_ai_escalation_eligibility(runtime, hunt_id=hunt_id, need_id=need_id)
    gates = [item.to_dict() for item in runtime.ai_escalation.list_gates(hunt_id=hunt_id, need_id=need_id, limit=20)]
    latest_preflight = runtime.ai_escalation.get_latest_preflight(hunt_id=hunt_id, need_id=need_id)
    return {
        "schema_version": "ai_escalation_summary.v0",
        "hunt_id": str(hunt_id or eligibility.input_packet.search_hunt_id),
        "need_id": str(need_id or eligibility.input_packet.search_need_id),
        "eligibility": eligibility.to_dict(),
        "gates": gates,
        "gate_count": len(gates),
        "latest_preflight": latest_preflight.to_dict() if latest_preflight else None,
        "provider_enabled": False,
        "execution_enabled": False,
        "candidate_only_output": True,
        "review_required": True,
        "execute_route_exists": False,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
    }

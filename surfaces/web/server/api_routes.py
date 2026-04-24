from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import parse_qs

from runtime.gateway.public_api import (
    AcquisitionFetchRequest,
    AcquisitionPublicApi,
    ActionPlanEvaluationRequest,
    ActionPlanPublicApi,
    AbsencePublicApi,
    ArchiveResolutionEvalRunRequest,
    ArchiveResolutionEvalsPublicApi,
    BOOTSTRAP_HOST_PROFILE_PRESETS,
    BOOTSTRAP_STRATEGY_PROFILES,
    CompareTargetsRequest,
    ComparisonPublicApi,
    CompatibilityEvaluationRequest,
    CompatibilityPublicApi,
    DeterministicSearchRunRequest,
    LocalIndexBuildRequest,
    LocalIndexPublicApi,
    LocalIndexQueryRequest,
    LocalIndexStatusRequest,
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
    PlannedSearchRunRequest,
    DecompositionInspectionRequest,
    DecompositionPublicApi,
    decomposition_envelope_to_view_model,
    ExactResolutionRunRequest,
    MemberAccessPublicApi,
    MemberAccessReadRequest,
    member_access_envelope_to_view_model,
    ExplainResolveMissRequest,
    ExplainSearchMissRequest,
    InspectResolutionBundleRequest,
    RepresentationCatalogRequest,
    RepresentationSelectionEvaluationRequest,
    RepresentationSelectionPublicApi,
    representation_selection_envelope_to_view_model,
    RepresentationsPublicApi,
    ResolutionActionRequest,
    ResolutionBundleInspectionPublicApi,
    ResolutionActionsPublicApi,
    ResolutionJobsPublicApi,
    QueryPlanRequest,
    QueryPlannerPublicApi,
    ResolutionRunReadRequest,
    ResolutionWorkspaceReadError,
    SearchCatalogRequest,
    SearchPublicApi,
    SubjectStatesCatalogRequest,
    SubjectStatesPublicApi,
    StoredArtifactRequest,
    StoredExportsTargetRequest,
    build_demo_resolution_runs_public_api,
    build_demo_resolution_memory_public_api,
    build_demo_local_tasks_public_api,
    build_demo_local_index_public_api,
    build_demo_stored_exports_public_api,
    acquisition_envelope_to_view_model,
    action_plan_envelope_to_view_model,
    absence_envelope_to_view_model,
    archive_resolution_evals_envelope_to_view_model,
    build_resolution_workspace_view_models,
    bundle_inspection_envelope_to_view_model,
    comparison_envelope_to_view_model,
    compatibility_envelope_to_view_model,
    representations_envelope_to_view_model,
    resolution_runs_envelope_to_view_model,
    resolution_memory_envelope_to_view_model,
    search_response_envelope_to_search_results_view_model,
    local_index_envelope_to_view_model,
    LocalTaskReadRequest,
    LocalTaskRunRequest,
    local_tasks_envelope_to_view_model,
    SourceCatalogRequest,
    SourceReadRequest,
    SourceRegistryPublicApi,
    source_registry_envelope_to_view_model,
    query_plan_envelope_to_view_model,
    stored_exports_envelope_to_view_model,
    subject_states_envelope_to_view_model,
)
from surfaces.web.server.api_serialization import (
    SerializedHttpResponse,
    bytes_response,
    error_response,
    json_response,
)
from surfaces.web.server.route_policy import PublicAlphaRoutePolicy
from surfaces.web.server.server_config import WebServerConfig, default_web_server_config


def build_api_index_document(
    server_config: WebServerConfig | None = None,
) -> dict[str, Any]:
    config = server_config or default_web_server_config()
    return {
        "api_kind": "eureka.bootstrap_http_api",
        "api_version": "0.1.0-draft",
        "status": "local_bootstrap",
        "mode": config.mode,
        "safe_mode_enabled": config.safe_mode_enabled,
        "enabled_capabilities": config.to_status_dict()["enabled_capabilities"],
        "disabled_capabilities": config.to_status_dict()["disabled_capabilities"],
        "endpoints": [
            {
                "path": "/api/status",
                "method": "GET",
                "query_parameters": [],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/tasks",
                "method": "GET",
                "query_parameters": ["task_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/task",
                "method": "GET",
                "query_parameters": ["id", "task_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/task/run/validate-source-registry",
                "method": "GET",
                "query_parameters": ["task_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/task/run/build-local-index",
                "method": "GET",
                "query_parameters": ["task_store_root", "index_path"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/task/run/query-local-index",
                "method": "GET",
                "query_parameters": ["task_store_root", "index_path", "q"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/task/run/validate-archive-resolution-evals",
                "method": "GET",
                "query_parameters": ["task_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/evals/archive-resolution",
                "method": "GET",
                "query_parameters": ["task_id", "index_path"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/index/build",
                "method": "GET",
                "query_parameters": ["index_path"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/index/status",
                "method": "GET",
                "query_parameters": ["index_path"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/index/query",
                "method": "GET",
                "query_parameters": ["index_path", "q"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/runs",
                "method": "GET",
                "query_parameters": ["run_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/memories",
                "method": "GET",
                "query_parameters": ["memory_store_root", "kind", "source_run_id", "task_kind", "source_id"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/memory",
                "method": "GET",
                "query_parameters": ["id", "memory_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/memory/create",
                "method": "GET",
                "query_parameters": ["run_store_root", "memory_store_root", "run_id"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/run",
                "method": "GET",
                "query_parameters": ["id", "run_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/run/resolve",
                "method": "GET",
                "query_parameters": ["target_ref", "run_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/run/search",
                "method": "GET",
                "query_parameters": ["q", "run_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/run/planned-search",
                "method": "GET",
                "query_parameters": ["q", "run_store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/query-plan",
                "method": "GET",
                "query_parameters": ["q"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/fetch",
                "method": "GET",
                "query_parameters": ["target_ref", "representation_id"],
                "response_content_types": ["application/octet-stream", "application/json"],
            },
            {
                "path": "/api/decompose",
                "method": "GET",
                "query_parameters": ["target_ref", "representation_id"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/member",
                "method": "GET",
                "query_parameters": ["target_ref", "representation_id", "member_path", "raw"],
                "response_content_types": ["application/octet-stream", "application/json"],
            },
            {
                "path": "/api/action-plan",
                "method": "GET",
                "query_parameters": ["target_ref", "host", "strategy", "store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/resolve",
                "method": "GET",
                "query_parameters": ["target_ref", "host", "strategy", "store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/handoff",
                "method": "GET",
                "query_parameters": ["target_ref", "host", "strategy"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/compare",
                "method": "GET",
                "query_parameters": ["left", "right"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/compatibility",
                "method": "GET",
                "query_parameters": ["target_ref", "host"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/representations",
                "method": "GET",
                "query_parameters": ["target_ref"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/search",
                "method": "GET",
                "query_parameters": ["q"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/sources",
                "method": "GET",
                "query_parameters": ["status", "family", "role", "surface"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/source",
                "method": "GET",
                "query_parameters": ["id"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/absence/resolve",
                "method": "GET",
                "query_parameters": ["target_ref"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/absence/search",
                "method": "GET",
                "query_parameters": ["q"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/states",
                "method": "GET",
                "query_parameters": ["subject"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/export/manifest",
                "method": "GET",
                "query_parameters": ["target_ref"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/export/bundle",
                "method": "GET",
                "query_parameters": ["target_ref"],
                "response_content_types": ["application/zip", "application/json"],
            },
            {
                "path": "/api/inspect/bundle",
                "method": "GET",
                "query_parameters": ["bundle_path"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/store/manifest",
                "method": "GET",
                "query_parameters": ["target_ref", "store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/store/bundle",
                "method": "GET",
                "query_parameters": ["target_ref", "store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/stored",
                "method": "GET",
                "query_parameters": ["target_ref", "store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/stored/artifact",
                "method": "GET",
                "query_parameters": ["artifact_id", "store_root"],
                "response_content_types": ["application/json", "application/zip"],
            },
        ],
        "notes": [
            "This is the first local stdlib HTTP API slice over Eureka's transport-neutral public boundary.",
            "Route names, auth, HTTPS/TLS, deployment, and multi-user semantics remain intentionally unresolved.",
            "store_root and bundle_path remain bootstrap local parameters for deterministic demo-scale flows.",
            "run_store_root remains a bootstrap/demo local parameter for synchronous persisted resolution runs only.",
            "memory_store_root remains a bootstrap/demo local parameter for explicit local resolution memory only.",
            "task_store_root remains a bootstrap/demo local parameter for synchronous persisted local tasks only.",
        ],
        "bootstrap_host_profile_presets": list(BOOTSTRAP_HOST_PROFILE_PRESETS),
        "bootstrap_strategy_profiles": list(BOOTSTRAP_STRATEGY_PROFILES),
    }


def handle_api_request(
    method: str,
    path: str,
    query_string: str,
    *,
    resolution_public_api: ResolutionJobsPublicApi,
    absence_public_api: AbsencePublicApi | None,
    comparison_public_api: ComparisonPublicApi | None,
    compatibility_public_api: CompatibilityPublicApi | None,
    acquisition_public_api: AcquisitionPublicApi | None,
    decomposition_public_api: DecompositionPublicApi | None,
    member_access_public_api: MemberAccessPublicApi | None,
    action_plan_public_api: ActionPlanPublicApi | None,
    archive_resolution_evals_public_api: ArchiveResolutionEvalsPublicApi | None,
    handoff_public_api: RepresentationSelectionPublicApi | None,
    query_planner_public_api: QueryPlannerPublicApi | None,
    subject_states_public_api: SubjectStatesPublicApi | None,
    representations_public_api: RepresentationsPublicApi | None,
    actions_public_api: ResolutionActionsPublicApi | None,
    bundle_inspection_public_api: ResolutionBundleInspectionPublicApi | None,
    local_index_public_api: LocalIndexPublicApi | None,
    search_public_api: SearchPublicApi,
    source_registry_public_api: SourceRegistryPublicApi | None,
    session_id: str,
    server_config: WebServerConfig | None = None,
) -> SerializedHttpResponse | None:
    if not path.startswith("/api"):
        return None
    config = server_config or default_web_server_config()

    if method != "GET":
        return error_response(
            405,
            code="method_not_allowed",
            message="This bootstrap HTTP API accepts GET requests only.",
            extra_fields={"allowed_methods": ["GET"]},
            headers=(("Allow", "GET"),),
        )

    query = parse_qs(query_string, keep_blank_values=False)
    route_decision = PublicAlphaRoutePolicy(config).evaluate_api_request(path, query)
    if not route_decision.allowed:
        return json_response(403, route_decision.to_blocked_payload())

    if path == "/api/status":
        return json_response(200, config.to_status_dict())

    if path in {"/api", "/api/"}:
        return json_response(200, build_api_index_document(config))

    if path == "/api/evals/archive-resolution":
        if archive_resolution_evals_public_api is None:
            return _service_unavailable(
                "archive_resolution_evals_unavailable",
                "This bootstrap HTTP API was not configured with a public archive-resolution eval boundary.",
            )
        request = ArchiveResolutionEvalRunRequest.from_parts(
            task_id=_optional_query_value(query, "task_id"),
            index_path=_optional_query_value(query, "index_path"),
        )
        response = (
            archive_resolution_evals_public_api.run_task(request)
            if request.task_id is not None
            else archive_resolution_evals_public_api.run_suite(request)
        )
        return json_response(
            response.status_code,
            archive_resolution_evals_envelope_to_view_model(response.body),
        )

    if path == "/api/index/build":
        if local_index_public_api is None:
            return _service_unavailable(
                "local_index_unavailable",
                "This bootstrap HTTP API was not configured with a public local-index boundary.",
            )
        index_path = _required_query_value(query, "index_path")
        if index_path is None:
            return _missing_query_value("index_path")
        try:
            response = local_index_public_api.build_index(
                LocalIndexBuildRequest.from_parts(index_path),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_local_index_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            local_index_envelope_to_view_model(response.body),
        )

    if path == "/api/tasks":
        tasks_public_api = _required_tasks_public_api(query)
        if isinstance(tasks_public_api, SerializedHttpResponse):
            return tasks_public_api
        response = tasks_public_api.list_tasks()
        return json_response(
            response.status_code,
            local_tasks_envelope_to_view_model(response.body),
        )

    if path == "/api/memories":
        memory_store_root = _required_query_value(query, "memory_store_root")
        if memory_store_root is None:
            return _missing_query_value("memory_store_root")
        memory_public_api = build_demo_resolution_memory_public_api(
            memory_store_root,
            run_store_root=_optional_query_value(query, "run_store_root"),
        )
        response = memory_public_api.list_memories(
            ResolutionMemoryCatalogRequest.from_parts(
                memory_kind=_optional_query_value(query, "kind"),
                source_run_id=_optional_query_value(query, "source_run_id"),
                task_kind=_optional_query_value(query, "task_kind"),
                checked_source_id=_optional_query_value(query, "source_id"),
            )
        )
        return json_response(
            response.status_code,
            resolution_memory_envelope_to_view_model(response.body),
        )

    if path == "/api/memory":
        memory_id = _required_query_value(query, "id")
        if memory_id is None:
            return _missing_query_value("id")
        memory_store_root = _required_query_value(query, "memory_store_root")
        if memory_store_root is None:
            return _missing_query_value("memory_store_root")
        memory_public_api = build_demo_resolution_memory_public_api(
            memory_store_root,
            run_store_root=_optional_query_value(query, "run_store_root"),
        )
        try:
            response = memory_public_api.get_memory(
                ResolutionMemoryReadRequest.from_parts(memory_id),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_resolution_memory_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            resolution_memory_envelope_to_view_model(response.body),
        )

    if path == "/api/memory/create":
        run_id = _required_query_value(query, "run_id")
        if run_id is None:
            return _missing_query_value("run_id")
        run_store_root = _required_query_value(query, "run_store_root")
        if run_store_root is None:
            return _missing_query_value("run_store_root")
        memory_store_root = _required_query_value(query, "memory_store_root")
        if memory_store_root is None:
            return _missing_query_value("memory_store_root")
        memory_public_api = build_demo_resolution_memory_public_api(
            memory_store_root,
            run_store_root=run_store_root,
        )
        try:
            response = memory_public_api.create_memory_from_run(
                ResolutionMemoryCreateRequest.from_parts(run_id),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_resolution_memory_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            resolution_memory_envelope_to_view_model(response.body),
        )

    if path == "/api/task":
        task_id = _required_query_value(query, "id")
        if task_id is None:
            return _missing_query_value("id")
        tasks_public_api = _required_tasks_public_api(query)
        if isinstance(tasks_public_api, SerializedHttpResponse):
            return tasks_public_api
        try:
            response = tasks_public_api.get_task(LocalTaskReadRequest.from_parts(task_id))
        except ValueError as error:
            return error_response(
                400,
                code="invalid_task_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            local_tasks_envelope_to_view_model(response.body),
        )

    if path == "/api/task/run/validate-source-registry":
        tasks_public_api = _required_tasks_public_api(query)
        if isinstance(tasks_public_api, SerializedHttpResponse):
            return tasks_public_api
        response = tasks_public_api.run_task(
            LocalTaskRunRequest.from_parts("validate-source-registry"),
        )
        return json_response(
            response.status_code,
            local_tasks_envelope_to_view_model(response.body),
        )

    if path == "/api/task/run/build-local-index":
        index_path = _required_query_value(query, "index_path")
        if index_path is None:
            return _missing_query_value("index_path")
        tasks_public_api = _required_tasks_public_api(query)
        if isinstance(tasks_public_api, SerializedHttpResponse):
            return tasks_public_api
        response = tasks_public_api.run_task(
            LocalTaskRunRequest.from_parts(
                "build-local-index",
                {"index_path": index_path},
            )
        )
        return json_response(
            response.status_code,
            local_tasks_envelope_to_view_model(response.body),
        )

    if path == "/api/task/run/query-local-index":
        index_path = _required_query_value(query, "index_path")
        if index_path is None:
            return _missing_query_value("index_path")
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        tasks_public_api = _required_tasks_public_api(query)
        if isinstance(tasks_public_api, SerializedHttpResponse):
            return tasks_public_api
        response = tasks_public_api.run_task(
            LocalTaskRunRequest.from_parts(
                "query-local-index",
                {"index_path": index_path, "query": query_text},
            )
        )
        return json_response(
            response.status_code,
            local_tasks_envelope_to_view_model(response.body),
        )

    if path == "/api/task/run/validate-archive-resolution-evals":
        tasks_public_api = _required_tasks_public_api(query)
        if isinstance(tasks_public_api, SerializedHttpResponse):
            return tasks_public_api
        response = tasks_public_api.run_task(
            LocalTaskRunRequest.from_parts("validate-archive-resolution-evals"),
        )
        return json_response(
            response.status_code,
            local_tasks_envelope_to_view_model(response.body),
        )

    if path == "/api/index/status":
        if local_index_public_api is None:
            return _service_unavailable(
                "local_index_unavailable",
                "This bootstrap HTTP API was not configured with a public local-index boundary.",
            )
        index_path = _required_query_value(query, "index_path")
        if index_path is None:
            return _missing_query_value("index_path")
        try:
            response = local_index_public_api.get_index_status(
                LocalIndexStatusRequest.from_parts(index_path),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_local_index_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            local_index_envelope_to_view_model(response.body),
        )

    if path == "/api/index/query":
        if local_index_public_api is None:
            return _service_unavailable(
                "local_index_unavailable",
                "This bootstrap HTTP API was not configured with a public local-index boundary.",
            )
        index_path = _required_query_value(query, "index_path")
        if index_path is None:
            return _missing_query_value("index_path")
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        try:
            response = local_index_public_api.query_index(
                LocalIndexQueryRequest.from_parts(index_path, query_text),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_local_index_query",
                message=str(error),
            )
        return json_response(
            response.status_code,
            local_index_envelope_to_view_model(response.body),
        )

    if path == "/api/resolve":
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        stored_exports_public_api = _optional_store_public_api(query)
        try:
            workspace = build_resolution_workspace_view_models(
                resolution_public_api,
                target_ref,
                action_plan_public_api=action_plan_public_api,
                handoff_public_api=handoff_public_api,
                actions_public_api=actions_public_api,
                stored_exports_public_api=stored_exports_public_api,
                session_id=session_id,
                host_profile_id=_required_query_value(query, "host"),
                strategy_id=_required_query_value(query, "strategy"),
            )
        except ResolutionWorkspaceReadError as error:
            return error_response(
                404,
                code="resolution_job_not_found",
                message=str(error),
                extra_fields={"target_ref": target_ref},
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_action_plan_context",
                message=str(error),
                extra_fields={"target_ref": target_ref},
            )

        payload: dict[str, Any] = {
            "workbench_session": workspace.workbench_session,
        }
        if workspace.resolution_actions is not None:
            payload["resolution_actions"] = workspace.resolution_actions
        if workspace.action_plan is not None:
            payload["action_plan"] = workspace.action_plan
        if workspace.handoff is not None:
            payload["handoff"] = workspace.handoff
        if workspace.stored_exports is not None:
            payload["stored_exports"] = workspace.stored_exports
        return json_response(200, payload)

    if path == "/api/runs":
        runs_public_api = _required_runs_public_api(query)
        if isinstance(runs_public_api, SerializedHttpResponse):
            return runs_public_api
        response = runs_public_api.list_runs()
        return json_response(
            response.status_code,
            resolution_runs_envelope_to_view_model(response.body),
        )

    if path == "/api/run":
        run_id = _required_query_value(query, "id")
        if run_id is None:
            return _missing_query_value("id")
        runs_public_api = _required_runs_public_api(query)
        if isinstance(runs_public_api, SerializedHttpResponse):
            return runs_public_api
        try:
            response = runs_public_api.get_run(ResolutionRunReadRequest.from_parts(run_id))
        except ValueError as error:
            return error_response(
                400,
                code="invalid_run_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            resolution_runs_envelope_to_view_model(response.body),
        )

    if path == "/api/run/resolve":
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        runs_public_api = _required_runs_public_api(query)
        if isinstance(runs_public_api, SerializedHttpResponse):
            return runs_public_api
        try:
            response = runs_public_api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(target_ref),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_run_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            resolution_runs_envelope_to_view_model(response.body),
        )

    if path == "/api/run/search":
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        runs_public_api = _required_runs_public_api(query)
        if isinstance(runs_public_api, SerializedHttpResponse):
            return runs_public_api
        try:
            response = runs_public_api.start_deterministic_search_run(
                DeterministicSearchRunRequest.from_parts(query_text),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_run_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            resolution_runs_envelope_to_view_model(response.body),
        )

    if path == "/api/run/planned-search":
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        runs_public_api = _required_runs_public_api(query)
        if isinstance(runs_public_api, SerializedHttpResponse):
            return runs_public_api
        try:
            response = runs_public_api.start_planned_search_run(
                PlannedSearchRunRequest.from_parts(query_text),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_run_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            resolution_runs_envelope_to_view_model(response.body),
        )

    if path == "/api/query-plan":
        if query_planner_public_api is None:
            return _service_unavailable(
                "query_planner_unavailable",
                "This bootstrap HTTP API was not configured with a public query-planner boundary.",
            )
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        response = query_planner_public_api.plan_query_text(query_text)
        return json_response(
            response.status_code,
            query_plan_envelope_to_view_model(response.body),
        )

    if path == "/api/action-plan":
        if action_plan_public_api is None:
            return _service_unavailable(
                "action_plan_unavailable",
                "This bootstrap HTTP API was not configured with a public action-plan boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        host_profile_id = _required_query_value(query, "host")
        strategy_id = _required_query_value(query, "strategy")
        try:
            response = action_plan_public_api.plan_actions(
                ActionPlanEvaluationRequest.from_parts(
                    target_ref,
                    host_profile_id,
                    strategy_id,
                    store_actions_enabled=_required_query_value(query, "store_root") is not None,
                )
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_action_plan_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            action_plan_envelope_to_view_model(response.body),
        )

    if path == "/api/fetch":
        if acquisition_public_api is None:
            return _service_unavailable(
                "acquisition_unavailable",
                "This bootstrap HTTP API was not configured with a public acquisition boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        representation_id = _required_query_value(query, "representation_id")
        if representation_id is None:
            return _missing_query_value("representation_id")
        try:
            response = acquisition_public_api.fetch_representation(
                AcquisitionFetchRequest.from_parts(target_ref, representation_id)
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_fetch_request",
                message=str(error),
            )
        if response.status_code == 200 and response.payload is not None and response.content_type is not None:
            return bytes_response(
                response.status_code,
                content_type=response.content_type,
                payload=response.payload,
                filename=response.filename,
            )
        return json_response(
            response.status_code,
            acquisition_envelope_to_view_model(response.body),
        )

    if path == "/api/decompose":
        if decomposition_public_api is None:
            return _service_unavailable(
                "decomposition_unavailable",
                "This bootstrap HTTP API was not configured with a public decomposition boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        representation_id = _required_query_value(query, "representation_id")
        if representation_id is None:
            return _missing_query_value("representation_id")
        try:
            response = decomposition_public_api.decompose_representation(
                DecompositionInspectionRequest.from_parts(target_ref, representation_id)
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_decomposition_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            decomposition_envelope_to_view_model(response.body),
        )

    if path == "/api/member":
        if member_access_public_api is None:
            return _service_unavailable(
                "member_access_unavailable",
                "This bootstrap HTTP API was not configured with a public member-access boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        representation_id = _required_query_value(query, "representation_id")
        if representation_id is None:
            return _missing_query_value("representation_id")
        member_path = _required_query_value(query, "member_path")
        if member_path is None:
            return _missing_query_value("member_path")
        try:
            response = member_access_public_api.read_member(
                MemberAccessReadRequest.from_parts(target_ref, representation_id, member_path)
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_member_access_request",
                message=str(error),
            )
        if (
            response.status_code == 200
            and response.payload is not None
            and response.content_type is not None
            and _required_query_value(query, "raw") is not None
        ):
            return bytes_response(
                response.status_code,
                content_type=response.content_type,
                payload=response.payload,
                filename=response.filename,
            )
        return json_response(
            response.status_code,
            member_access_envelope_to_view_model(response.body),
        )

    if path == "/api/handoff":
        if handoff_public_api is None:
            return _service_unavailable(
                "handoff_unavailable",
                "This bootstrap HTTP API was not configured with a public representation-selection boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        host_profile_id = _required_query_value(query, "host")
        strategy_id = _required_query_value(query, "strategy")
        try:
            response = handoff_public_api.select_representation(
                RepresentationSelectionEvaluationRequest.from_parts(
                    target_ref,
                    host_profile_id,
                    strategy_id,
                )
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_handoff_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            representation_selection_envelope_to_view_model(response.body),
        )

    if path == "/api/compare":
        if comparison_public_api is None:
            return _service_unavailable(
                "comparison_unavailable",
                "This bootstrap HTTP API was not configured with a public comparison boundary.",
            )
        left_target_ref = _required_query_value(query, "left")
        if left_target_ref is None:
            return _missing_query_value("left")
        right_target_ref = _required_query_value(query, "right")
        if right_target_ref is None:
            return _missing_query_value("right")
        response = comparison_public_api.compare_targets(
            CompareTargetsRequest.from_parts(left_target_ref, right_target_ref),
        )
        return json_response(
            response.status_code,
            comparison_envelope_to_view_model(response.body),
        )

    if path == "/api/compatibility":
        if compatibility_public_api is None:
            return _service_unavailable(
                "compatibility_unavailable",
                "This bootstrap HTTP API was not configured with a public compatibility boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        host_profile_id = _required_query_value(query, "host")
        if host_profile_id is None:
            return _missing_query_value("host")
        try:
            response = compatibility_public_api.evaluate_compatibility(
                CompatibilityEvaluationRequest.from_parts(target_ref, host_profile_id),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_host_profile",
                message=str(error),
            )
        return json_response(
            response.status_code,
            compatibility_envelope_to_view_model(response.body),
        )

    if path == "/api/states":
        if subject_states_public_api is None:
            return _service_unavailable(
                "subject_states_unavailable",
                "This bootstrap HTTP API was not configured with a public subject/state boundary.",
            )
        subject_key = _required_query_value(query, "subject")
        if subject_key is None:
            return _missing_query_value("subject")
        response = subject_states_public_api.list_subject_states(
            SubjectStatesCatalogRequest.from_parts(subject_key),
        )
        return json_response(
            response.status_code,
            subject_states_envelope_to_view_model(response.body),
        )

    if path == "/api/representations":
        if representations_public_api is None:
            return _service_unavailable(
                "representations_unavailable",
                "This bootstrap HTTP API was not configured with a public representations boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        response = representations_public_api.list_representations(
            RepresentationCatalogRequest.from_parts(target_ref),
        )
        return json_response(
            response.status_code,
            representations_envelope_to_view_model(response.body),
        )

    if path == "/api/search":
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        response = search_public_api.search_records(SearchCatalogRequest.from_parts(query_text))
        return json_response(
            response.status_code,
            search_response_envelope_to_search_results_view_model(response.body),
        )

    if path == "/api/sources":
        if source_registry_public_api is None:
            return _service_unavailable(
                "source_registry_unavailable",
                "This bootstrap HTTP API was not configured with a public source-registry boundary.",
            )
        response = source_registry_public_api.list_sources(
            SourceCatalogRequest.from_parts(
                status=_required_query_value(query, "status"),
                source_family=_required_query_value(query, "family"),
                role=_required_query_value(query, "role"),
                surface=_required_query_value(query, "surface"),
            )
        )
        return json_response(
            response.status_code,
            source_registry_envelope_to_view_model(response.body),
        )

    if path == "/api/source":
        if source_registry_public_api is None:
            return _service_unavailable(
                "source_registry_unavailable",
                "This bootstrap HTTP API was not configured with a public source-registry boundary.",
            )
        source_id = _required_query_value(query, "id")
        if source_id is None:
            return _missing_query_value("id")
        try:
            response = source_registry_public_api.get_source(
                SourceReadRequest.from_parts(source_id),
            )
        except ValueError as error:
            return error_response(
                400,
                code="invalid_source_request",
                message=str(error),
            )
        return json_response(
            response.status_code,
            source_registry_envelope_to_view_model(response.body),
        )

    if path == "/api/absence/resolve":
        if absence_public_api is None:
            return _service_unavailable(
                "absence_unavailable",
                "This bootstrap HTTP API was not configured with a public absence boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        response = absence_public_api.explain_resolution_miss(
            ExplainResolveMissRequest.from_parts(target_ref),
        )
        return json_response(
            response.status_code,
            absence_envelope_to_view_model(response.body),
        )

    if path == "/api/absence/search":
        if absence_public_api is None:
            return _service_unavailable(
                "absence_unavailable",
                "This bootstrap HTTP API was not configured with a public absence boundary.",
            )
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        response = absence_public_api.explain_search_miss(
            ExplainSearchMissRequest.from_parts(query_text),
        )
        return json_response(
            response.status_code,
            absence_envelope_to_view_model(response.body),
        )

    if path == "/api/export/manifest":
        if actions_public_api is None:
            return _service_unavailable(
                "resolution_actions_unavailable",
                "This bootstrap HTTP API was not configured with a public action boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        response = actions_public_api.export_resolution_manifest(
            ResolutionActionRequest.from_parts(target_ref),
        )
        return json_response(response.status_code, response.body)

    if path == "/api/export/bundle":
        if actions_public_api is None:
            return _service_unavailable(
                "resolution_actions_unavailable",
                "This bootstrap HTTP API was not configured with a public action boundary.",
            )
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        response = actions_public_api.export_resolution_bundle(
            ResolutionActionRequest.from_parts(target_ref),
        )
        return bytes_response(
            response.status_code,
            content_type=response.content_type,
            payload=response.payload,
            filename=response.filename,
        )

    if path == "/api/inspect/bundle":
        if bundle_inspection_public_api is None:
            return _service_unavailable(
                "bundle_inspection_unavailable",
                "This bootstrap HTTP API was not configured with a public bundle inspection boundary.",
            )
        bundle_path = _required_query_value(query, "bundle_path")
        if bundle_path is None:
            return _missing_query_value("bundle_path")
        response = bundle_inspection_public_api.inspect_bundle(
            InspectResolutionBundleRequest.from_bundle_path(bundle_path),
        )
        return json_response(
            response.status_code,
            bundle_inspection_envelope_to_view_model(response.body),
        )

    if path == "/api/store/manifest":
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        stored_public_api = _required_store_public_api(query)
        if isinstance(stored_public_api, SerializedHttpResponse):
            return stored_public_api
        response = stored_public_api.store_resolution_manifest(
            StoredExportsTargetRequest.from_parts(target_ref),
        )
        return json_response(response.status_code, response.body)

    if path == "/api/store/bundle":
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        stored_public_api = _required_store_public_api(query)
        if isinstance(stored_public_api, SerializedHttpResponse):
            return stored_public_api
        response = stored_public_api.store_resolution_bundle(
            StoredExportsTargetRequest.from_parts(target_ref),
        )
        return json_response(response.status_code, response.body)

    if path == "/api/stored":
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        stored_public_api = _required_store_public_api(query)
        if isinstance(stored_public_api, SerializedHttpResponse):
            return stored_public_api
        response = stored_public_api.list_stored_exports(
            StoredExportsTargetRequest.from_parts(target_ref),
        )
        return json_response(
            response.status_code,
            stored_exports_envelope_to_view_model(response.body),
        )

    if path == "/api/stored/artifact":
        artifact_id = _required_query_value(query, "artifact_id")
        if artifact_id is None:
            return _missing_query_value("artifact_id")
        stored_public_api = _required_store_public_api(query)
        if isinstance(stored_public_api, SerializedHttpResponse):
            return stored_public_api
        response = stored_public_api.get_stored_artifact_content(
            StoredArtifactRequest.from_parts(artifact_id),
        )
        return bytes_response(
            response.status_code,
            content_type=response.content_type,
            payload=response.payload,
            filename=response.filename,
        )

    return error_response(
        404,
        code="api_route_not_found",
        message=f"Unknown bootstrap API route '{path}'.",
        extra_fields={"path": path},
    )


def _required_query_value(query: Mapping[str, list[str]], name: str) -> str | None:
    raw_values = query.get(name)
    if not raw_values:
        return None
    normalized = raw_values[0].strip()
    return normalized or None


def _optional_query_value(query: Mapping[str, list[str]], name: str) -> str | None:
    raw_values = query.get(name)
    if not raw_values:
        return None
    normalized = raw_values[0].strip()
    return normalized or None


def _optional_store_public_api(query: Mapping[str, list[str]]):
    store_root = _required_query_value(query, "store_root")
    if store_root is None:
        return None
    return build_demo_stored_exports_public_api(store_root)


def _required_store_public_api(
    query: Mapping[str, list[str]],
):
    store_root = _required_query_value(query, "store_root")
    if store_root is None:
        return _missing_query_value(
            "store_root",
            message="Provide a local store_root query parameter for this bootstrap local-store API route.",
        )
    return build_demo_stored_exports_public_api(store_root)


def _required_runs_public_api(
    query: Mapping[str, list[str]],
):
    run_store_root = _required_query_value(query, "run_store_root")
    if run_store_root is None:
        return _missing_query_value(
            "run_store_root",
            message="Provide a local run_store_root query parameter for this bootstrap resolution-run API route.",
        )
    return build_demo_resolution_runs_public_api(run_store_root)


def _required_tasks_public_api(
    query: Mapping[str, list[str]],
):
    task_store_root = _required_query_value(query, "task_store_root")
    if task_store_root is None:
        return _missing_query_value(
            "task_store_root",
            message="Provide a local task_store_root query parameter for this bootstrap local-task API route.",
        )
    return build_demo_local_tasks_public_api(task_store_root)


def _missing_query_value(name: str, *, message: str | None = None) -> SerializedHttpResponse:
    return error_response(
        400,
        code=f"{name}_required",
        message=message or f"Provide a non-empty '{name}' query parameter.",
    )


def _service_unavailable(code: str, message: str) -> SerializedHttpResponse:
    return error_response(503, code=code, message=message)

from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import parse_qs

from runtime.gateway.public_api import (
    CompareTargetsRequest,
    ComparisonPublicApi,
    InspectResolutionBundleRequest,
    ResolutionActionRequest,
    ResolutionBundleInspectionPublicApi,
    ResolutionActionsPublicApi,
    ResolutionJobsPublicApi,
    ResolutionWorkspaceReadError,
    SearchCatalogRequest,
    SearchPublicApi,
    StoredArtifactRequest,
    StoredExportsTargetRequest,
    build_demo_stored_exports_public_api,
    build_resolution_workspace_view_models,
    bundle_inspection_envelope_to_view_model,
    comparison_envelope_to_view_model,
    search_response_envelope_to_search_results_view_model,
    stored_exports_envelope_to_view_model,
)
from surfaces.web.server.api_serialization import (
    SerializedHttpResponse,
    bytes_response,
    error_response,
    json_response,
)


def build_api_index_document() -> dict[str, Any]:
    return {
        "api_kind": "eureka.bootstrap_http_api",
        "api_version": "0.1.0-draft",
        "status": "local_bootstrap",
        "endpoints": [
            {
                "path": "/api/resolve",
                "method": "GET",
                "query_parameters": ["target_ref", "store_root"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/compare",
                "method": "GET",
                "query_parameters": ["left", "right"],
                "response_content_types": ["application/json"],
            },
            {
                "path": "/api/search",
                "method": "GET",
                "query_parameters": ["q"],
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
        ],
    }


def handle_api_request(
    method: str,
    path: str,
    query_string: str,
    *,
    resolution_public_api: ResolutionJobsPublicApi,
    comparison_public_api: ComparisonPublicApi | None,
    actions_public_api: ResolutionActionsPublicApi | None,
    bundle_inspection_public_api: ResolutionBundleInspectionPublicApi | None,
    search_public_api: SearchPublicApi,
    session_id: str,
) -> SerializedHttpResponse | None:
    if not path.startswith("/api"):
        return None

    if method != "GET":
        return error_response(
            405,
            code="method_not_allowed",
            message="This bootstrap HTTP API accepts GET requests only.",
            extra_fields={"allowed_methods": ["GET"]},
            headers=(("Allow", "GET"),),
        )

    query = parse_qs(query_string, keep_blank_values=False)
    if path in {"/api", "/api/", "/api/index"}:
        return json_response(200, build_api_index_document())

    if path == "/api/resolve":
        target_ref = _required_query_value(query, "target_ref")
        if target_ref is None:
            return _missing_query_value("target_ref")
        stored_exports_public_api = _optional_store_public_api(query)
        try:
            workspace = build_resolution_workspace_view_models(
                resolution_public_api,
                target_ref,
                actions_public_api=actions_public_api,
                stored_exports_public_api=stored_exports_public_api,
                session_id=session_id,
            )
        except ResolutionWorkspaceReadError as error:
            return error_response(
                404,
                code="resolution_job_not_found",
                message=str(error),
                extra_fields={"target_ref": target_ref},
            )

        payload: dict[str, Any] = {
            "workbench_session": workspace.workbench_session,
        }
        if workspace.resolution_actions is not None:
            payload["resolution_actions"] = workspace.resolution_actions
        if workspace.stored_exports is not None:
            payload["stored_exports"] = workspace.stored_exports
        return json_response(200, payload)

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

    if path == "/api/search":
        query_text = _required_query_value(query, "q")
        if query_text is None:
            return _missing_query_value("q")
        response = search_public_api.search_records(SearchCatalogRequest.from_parts(query_text))
        return json_response(
            response.status_code,
            search_response_envelope_to_search_results_view_model(response.body),
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


def _missing_query_value(name: str, *, message: str | None = None) -> SerializedHttpResponse:
    return error_response(
        400,
        code=f"{name}_required",
        message=message or f"Provide a non-empty '{name}' query parameter.",
    )


def _service_unavailable(code: str, message: str) -> SerializedHttpResponse:
    return error_response(503, code=code, message=message)

from __future__ import annotations

import json
from html import escape
from typing import Callable
from urllib.parse import parse_qs

from runtime.gateway.public_api import (
    ActionPlanEvaluationRequest,
    ActionPlanPublicApi,
    AbsencePublicApi,
    BOOTSTRAP_HOST_PROFILE_PRESETS,
    CompareTargetsRequest,
    ComparisonPublicApi,
    CompatibilityEvaluationRequest,
    CompatibilityPublicApi,
    ExplainResolveMissRequest,
    ExplainSearchMissRequest,
    InspectResolutionBundleRequest,
    RepresentationCatalogRequest,
    RepresentationsPublicApi,
    ResolutionActionRequest,
    ResolutionBundleInspectionPublicApi,
    ResolutionActionsPublicApi,
    ResolutionJobsPublicApi,
    ResolutionWorkspaceReadError,
    SearchCatalogRequest,
    SearchPublicApi,
    SubjectStatesCatalogRequest,
    SubjectStatesPublicApi,
    StoredArtifactRequest,
    StoredExportsPublicApi,
    StoredExportsTargetRequest,
    action_plan_envelope_to_view_model,
    build_resolution_workspace_view_models,
    absence_envelope_to_view_model,
    bundle_inspection_envelope_to_view_model,
    comparison_envelope_to_view_model,
    compatibility_envelope_to_view_model,
    representations_envelope_to_view_model,
    search_response_envelope_to_search_results_view_model,
    subject_states_envelope_to_view_model,
)
from surfaces.web.server.api_routes import handle_api_request
from surfaces.web.server.api_serialization import SerializedHttpResponse
from surfaces.web.workbench import (
    render_action_plan_html,
    render_absence_report_html,
    render_bundle_inspection_html,
    render_compatibility_html,
    render_comparison_html,
    render_representations_html,
    render_resolution_workspace_html,
    render_search_results_html,
    render_subject_states_html,
)


def render_resolution_workspace_page(
    resolution_public_api: ResolutionJobsPublicApi,
    target_ref: str,
    *,
    action_plan_public_api: ActionPlanPublicApi | None = None,
    actions_public_api: ResolutionActionsPublicApi | None = None,
    stored_exports_public_api: StoredExportsPublicApi | None = None,
    session_id: str = "session.web-workbench",
) -> str:
    try:
        workspace = build_resolution_workspace_view_models(
            resolution_public_api,
            target_ref,
            action_plan_public_api=action_plan_public_api,
            actions_public_api=actions_public_api,
            stored_exports_public_api=stored_exports_public_api,
            session_id=session_id,
        )
    except ResolutionWorkspaceReadError as error:
        return _render_error_page(
            title="Eureka Compatibility Workbench",
            heading="Resolution Job Not Found",
            message=str(error),
        )
    return render_resolution_workspace_html(
        workspace.workbench_session,
        action_plan=workspace.action_plan,
        resolution_actions=workspace.resolution_actions,
        stored_exports=workspace.stored_exports,
        host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
    )


def render_action_plan_page(
    public_api: ActionPlanPublicApi | None,
    target_ref: str,
    host_profile_id: str | None,
    *,
    store_actions_enabled: bool = False,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_host_profile_id = (host_profile_id or "").strip() or None
    if not normalized_target_ref:
        return render_action_plan_html(
            None,
            target_ref="",
            host_profile_id=normalized_host_profile_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            message="Provide a bounded target ref to build an action plan.",
        )
    if public_api is None:
        return render_action_plan_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            message="This bootstrap workbench was not configured with a public action-plan boundary.",
        )
    try:
        response = public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                normalized_target_ref,
                normalized_host_profile_id,
                store_actions_enabled=store_actions_enabled,
            )
        )
    except ValueError as error:
        return render_action_plan_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            message=str(error),
        )
    return render_action_plan_html(
        action_plan_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        host_profile_id=normalized_host_profile_id,
        host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
    )


def render_subject_states_page(
    subject_states_public_api: SubjectStatesPublicApi | None,
    subject_key: str,
) -> str:
    normalized_subject_key = subject_key.strip().casefold()
    if not normalized_subject_key:
        return render_subject_states_html(
            None,
            subject_key="",
            message="Provide a bounded subject key to list known states.",
        )
    if subject_states_public_api is None:
        return render_subject_states_html(
            None,
            subject_key=normalized_subject_key,
            message="This bootstrap workbench was not configured with a subject/state boundary.",
        )
    response = subject_states_public_api.list_subject_states(
        SubjectStatesCatalogRequest.from_parts(normalized_subject_key),
    )
    subject_states = subject_states_envelope_to_view_model(response.body)
    return render_subject_states_html(
        subject_states,
        subject_key=normalized_subject_key,
    )


def render_resolve_absence_page(
    absence_public_api: AbsencePublicApi | None,
    target_ref: str,
) -> str:
    normalized_target_ref = target_ref.strip()
    if not normalized_target_ref:
        return render_absence_report_html(
            None,
            request_kind="resolve",
            requested_value="",
            message="Provide a bounded target ref to explain an exact-resolution miss.",
        )
    if absence_public_api is None:
        return render_absence_report_html(
            None,
            request_kind="resolve",
            requested_value=normalized_target_ref,
            message="This bootstrap workbench was not configured with a public absence boundary.",
        )
    response = absence_public_api.explain_resolution_miss(
        ExplainResolveMissRequest.from_parts(normalized_target_ref),
    )
    return render_absence_report_html(
        absence_envelope_to_view_model(response.body),
        request_kind="resolve",
        requested_value=normalized_target_ref,
    )


def render_search_absence_page(
    absence_public_api: AbsencePublicApi | None,
    query: str,
) -> str:
    normalized_query = query.strip()
    if not normalized_query:
        return render_absence_report_html(
            None,
            request_kind="search",
            requested_value="",
            message="Provide a bounded query to explain a deterministic search miss.",
        )
    if absence_public_api is None:
        return render_absence_report_html(
            None,
            request_kind="search",
            requested_value=normalized_query,
            message="This bootstrap workbench was not configured with a public absence boundary.",
        )
    response = absence_public_api.explain_search_miss(
        ExplainSearchMissRequest.from_parts(normalized_query),
    )
    return render_absence_report_html(
        absence_envelope_to_view_model(response.body),
        request_kind="search",
        requested_value=normalized_query,
    )


def render_representations_page(
    public_api: RepresentationsPublicApi | None,
    target_ref: str,
) -> str:
    normalized_target_ref = target_ref.strip()
    if not normalized_target_ref:
        return render_representations_html(
            {
                "status": "blocked",
                "target_ref": "",
                "representations": [],
                "notices": [
                    {
                        "code": "target_ref_required",
                        "severity": "warning",
                        "message": "Provide a bounded target ref to list known representations.",
                    }
                ],
            }
        )
    if public_api is None:
        return render_representations_html(
            {
                "status": "blocked",
                "target_ref": normalized_target_ref,
                "representations": [],
                "notices": [
                    {
                        "code": "representations_unavailable",
                        "severity": "warning",
                        "message": "This bootstrap workbench was not configured with a public representations boundary.",
                    }
                ],
            }
        )
    response = public_api.list_representations(
        RepresentationCatalogRequest.from_parts(normalized_target_ref),
    )
    return render_representations_html(representations_envelope_to_view_model(response.body))


def render_compatibility_page(
    public_api: CompatibilityPublicApi | None,
    target_ref: str,
    host_profile_id: str,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_host_profile_id = host_profile_id.strip() or "windows-x86_64"
    if not normalized_target_ref:
        return render_compatibility_html(
            None,
            target_ref="",
            host_profile_id=normalized_host_profile_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            message="Provide a bounded target ref to evaluate compatibility.",
        )
    if public_api is None:
        return render_compatibility_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            message="This bootstrap workbench was not configured with a public compatibility boundary.",
        )
    try:
        response = public_api.evaluate_compatibility(
            CompatibilityEvaluationRequest.from_parts(normalized_target_ref, normalized_host_profile_id),
        )
    except ValueError as error:
        return render_compatibility_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            message=str(error),
        )
    return render_compatibility_html(
        compatibility_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        host_profile_id=normalized_host_profile_id,
        host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
    )


class WorkbenchWsgiApp:
    def __init__(
        self,
        resolution_public_api: ResolutionJobsPublicApi,
        *,
        absence_public_api: AbsencePublicApi | None = None,
        comparison_public_api: ComparisonPublicApi | None = None,
        compatibility_public_api: CompatibilityPublicApi | None = None,
        action_plan_public_api: ActionPlanPublicApi | None = None,
        subject_states_public_api: SubjectStatesPublicApi | None = None,
        representations_public_api: RepresentationsPublicApi | None = None,
        actions_public_api: ResolutionActionsPublicApi | None = None,
        bundle_inspection_public_api: ResolutionBundleInspectionPublicApi | None = None,
        stored_exports_public_api: StoredExportsPublicApi | None = None,
        search_public_api: SearchPublicApi,
        default_target_ref: str,
        session_id: str = "session.web-workbench",
    ) -> None:
        self._resolution_public_api = resolution_public_api
        self._absence_public_api = absence_public_api
        self._comparison_public_api = comparison_public_api
        self._compatibility_public_api = compatibility_public_api
        self._action_plan_public_api = action_plan_public_api
        self._subject_states_public_api = subject_states_public_api
        self._representations_public_api = representations_public_api
        self._actions_public_api = actions_public_api
        self._bundle_inspection_public_api = bundle_inspection_public_api
        self._stored_exports_public_api = stored_exports_public_api
        self._search_public_api = search_public_api
        self._default_target_ref = default_target_ref
        self._session_id = session_id

    def __call__(
        self,
        environ: dict[str, object],
        start_response: Callable[[str, list[tuple[str, str]]], object],
    ) -> list[bytes]:
        path = str(environ.get("PATH_INFO") or "/")
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        query_string = str(environ.get("QUERY_STRING", ""))
        api_response = handle_api_request(
            method,
            path,
            query_string,
            resolution_public_api=self._resolution_public_api,
            absence_public_api=self._absence_public_api,
            comparison_public_api=self._comparison_public_api,
            compatibility_public_api=self._compatibility_public_api,
            action_plan_public_api=self._action_plan_public_api,
            subject_states_public_api=self._subject_states_public_api,
            representations_public_api=self._representations_public_api,
            actions_public_api=self._actions_public_api,
            bundle_inspection_public_api=self._bundle_inspection_public_api,
            search_public_api=self._search_public_api,
            session_id=self._session_id,
        )
        if api_response is not None:
            return self._respond_serialized(start_response, api_response)

        if method != "GET":
            return self._respond(
                start_response,
                status="405 Method Not Allowed",
                body=_render_error_page(
                    title="Eureka Compatibility Workbench",
                    heading="Method Not Allowed",
                    message="This bootstrap workbench accepts GET requests only.",
                ),
                extra_headers=[("Allow", "GET")],
            )

        if path not in {
            "/",
            "/absence/resolve",
            "/absence/search",
            "/compare",
            "/compatibility",
            "/action-plan",
            "/representations",
            "/subject",
            "/search",
            "/inspect/bundle",
            "/actions/export-resolution-manifest",
            "/actions/export-resolution-bundle",
            "/store/manifest",
            "/store/bundle",
            "/stored/artifact",
        }:
            return self._respond(
                start_response,
                status="404 Not Found",
                body=_render_error_page(
                    title="Eureka Compatibility Workbench",
                    heading="Page Not Found",
                    message=(
                        "This bootstrap workbench serves compatibility-first pages at '/', '/search', "
                        "'/absence/resolve', '/absence/search', '/compare', '/compatibility', '/action-plan', '/representations', '/subject', '/inspect/bundle', '/actions/export-resolution-manifest', and "
                        "'/actions/export-resolution-bundle', '/store/manifest', "
                        "'/store/bundle', and '/stored/artifact'."
                    ),
                ),
            )

        if path == "/":
            target_ref = self._resolve_target_ref(query_string)
            page = render_resolution_workspace_page(
                self._resolution_public_api,
                target_ref,
                action_plan_public_api=self._action_plan_public_api,
                actions_public_api=self._actions_public_api,
                stored_exports_public_api=self._stored_exports_public_api,
                session_id=self._session_id,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/action-plan":
            target_ref = self._resolve_target_ref(query_string)
            host_profile_id = self._resolve_optional_host_profile_id(query_string)
            page = render_action_plan_page(
                self._action_plan_public_api,
                target_ref,
                host_profile_id,
                store_actions_enabled=self._stored_exports_public_api is not None,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/compare":
            left_target_ref = self._resolve_left_target_ref(query_string)
            right_target_ref = self._resolve_right_target_ref(query_string)
            page = render_comparison_page(
                self._comparison_public_api,
                left_target_ref,
                right_target_ref,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/compatibility":
            target_ref = self._resolve_target_ref(query_string)
            host_profile_id = self._resolve_host_profile_id(query_string)
            page = render_compatibility_page(
                self._compatibility_public_api,
                target_ref,
                host_profile_id,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/representations":
            target_ref = self._resolve_target_ref(query_string)
            page = render_representations_page(
                self._representations_public_api,
                target_ref,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/absence/resolve":
            target_ref = self._resolve_target_ref(query_string)
            page = render_resolve_absence_page(self._absence_public_api, target_ref)
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/absence/search":
            query = self._resolve_search_query(query_string)
            page = render_search_absence_page(self._absence_public_api, query)
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/subject":
            subject_key = self._resolve_subject_key(query_string)
            page = render_subject_states_page(
                self._subject_states_public_api,
                subject_key,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/search":
            query = self._resolve_search_query(query_string)
            page = render_search_results_page(
                self._search_public_api,
                query,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/inspect/bundle":
            bundle_path = self._resolve_bundle_path(query_string)
            page = render_bundle_inspection_page(
                self._bundle_inspection_public_api,
                bundle_path,
            )
            return self._respond(start_response, status="200 OK", body=page)

        target_ref = self._resolve_target_ref(query_string)
        if self._actions_public_api is None:
            if path in {"/actions/export-resolution-manifest", "/actions/export-resolution-bundle"}:
                return self._respond(
                    start_response,
                    status="404 Not Found",
                    body=_render_error_page(
                        title="Eureka Compatibility Workbench",
                        heading="Resolution Export Unavailable",
                        message="This bootstrap workbench was not configured with a public action boundary.",
                    ),
                )
        if path == "/actions/export-resolution-manifest":
            request = ResolutionActionRequest.from_parts(target_ref)
            export_response = self._actions_public_api.export_resolution_manifest(request)
            return self._respond_json(
                start_response,
                status="200 OK" if export_response.status_code == 200 else "404 Not Found",
                payload=export_response.body,
            )
        if path == "/actions/export-resolution-bundle":
            request = ResolutionActionRequest.from_parts(target_ref)
            bundle_response = self._actions_public_api.export_resolution_bundle(request)
            extra_headers: list[tuple[str, str]] = []
            if bundle_response.filename is not None:
                extra_headers.append(
                    ("Content-Disposition", f"attachment; filename=\"{bundle_response.filename}\""),
                )
            return self._respond_bytes(
                start_response,
                status="200 OK" if bundle_response.status_code == 200 else "404 Not Found",
                payload=bundle_response.payload,
                content_type=bundle_response.content_type,
                extra_headers=extra_headers,
            )

        if path in {"/store/manifest", "/store/bundle"}:
            if self._stored_exports_public_api is None:
                return self._respond_json(
                    start_response,
                    status="503 Service Unavailable",
                    payload={
                        "status": "blocked",
                        "code": "export_store_unavailable",
                        "message": "Provide a local store root to enable bootstrap stored-export routes.",
                    },
                )
            store_request = StoredExportsTargetRequest.from_parts(target_ref)
            if path == "/store/manifest":
                store_response = self._stored_exports_public_api.store_resolution_manifest(store_request)
            else:
                store_response = self._stored_exports_public_api.store_resolution_bundle(store_request)
            return self._respond_json(
                start_response,
                status="200 OK" if store_response.status_code == 200 else "404 Not Found",
                payload=store_response.body,
            )

        artifact_id = self._resolve_artifact_id(query_string)
        if not artifact_id:
            return self._respond_json(
                start_response,
                status="404 Not Found",
                payload={
                    "status": "blocked",
                    "code": "stored_artifact_id_required",
                    "message": "Provide an artifact_id query parameter to fetch a stored artifact in this bootstrap demo.",
                },
            )
        if self._stored_exports_public_api is None:
            return self._respond_json(
                start_response,
                status="503 Service Unavailable",
                payload={
                    "status": "blocked",
                    "artifact_id": artifact_id,
                    "code": "export_store_unavailable",
                    "message": "Provide a local store root to enable bootstrap stored-artifact routes.",
                },
            )
        artifact_response = self._stored_exports_public_api.get_stored_artifact_content(
            StoredArtifactRequest.from_parts(artifact_id),
        )
        extra_headers: list[tuple[str, str]] = []
        if artifact_response.filename is not None:
            extra_headers.append(
                ("Content-Disposition", f"attachment; filename=\"{artifact_response.filename}\""),
            )
        return self._respond_bytes(
            start_response,
            status="200 OK" if artifact_response.status_code == 200 else "404 Not Found",
            payload=artifact_response.payload,
            content_type=artifact_response.content_type,
            extra_headers=extra_headers,
        )

    def _resolve_target_ref(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_target_ref = query.get("target_ref", [self._default_target_ref])[0].strip()
        return raw_target_ref or self._default_target_ref

    def _resolve_search_query(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_query = query.get("q", [""])[0].strip()
        return raw_query

    def _resolve_left_target_ref(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        return query.get("left", [""])[0].strip()

    def _resolve_right_target_ref(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        return query.get("right", [""])[0].strip()

    def _resolve_host_profile_id(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_host_profile_id = query.get("host", ["windows-x86_64"])[0].strip()
        return raw_host_profile_id or "windows-x86_64"

    def _resolve_optional_host_profile_id(self, query_string: str) -> str | None:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_host_profile_id = query.get("host", [""])[0].strip()
        return raw_host_profile_id or None

    def _resolve_bundle_path(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_bundle_path = query.get("bundle_path", [""])[0].strip()
        return raw_bundle_path

    def _resolve_subject_key(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        return query.get("key", [""])[0].strip()

    def _resolve_artifact_id(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_artifact_id = query.get("artifact_id", [""])[0].strip()
        return raw_artifact_id

    def _respond(
        self,
        start_response: Callable[[str, list[tuple[str, str]]], object],
        *,
        status: str,
        body: str,
        extra_headers: list[tuple[str, str]] | None = None,
    ) -> list[bytes]:
        payload = body.encode("utf-8")
        headers = [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(payload))),
        ]
        if extra_headers:
            headers.extend(extra_headers)
        start_response(status, headers)
        return [payload]

    def _respond_serialized(
        self,
        start_response: Callable[[str, list[tuple[str, str]]], object],
        response: SerializedHttpResponse,
    ) -> list[bytes]:
        headers = [
            ("Content-Type", response.content_type),
            ("Content-Length", str(len(response.payload))),
        ]
        headers.extend(response.headers)
        start_response(response.status, headers)
        return [response.payload]

    def _respond_json(
        self,
        start_response: Callable[[str, list[tuple[str, str]]], object],
        *,
        status: str,
        payload: dict[str, object],
    ) -> list[bytes]:
        body = json.dumps(payload, indent=2, sort_keys=True)
        encoded = f"{body}\n".encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(encoded))),
        ]
        start_response(status, headers)
        return [encoded]

    def _respond_bytes(
        self,
        start_response: Callable[[str, list[tuple[str, str]]], object],
        *,
        status: str,
        payload: bytes,
        content_type: str,
        extra_headers: list[tuple[str, str]] | None = None,
    ) -> list[bytes]:
        headers = [
            ("Content-Type", content_type),
            ("Content-Length", str(len(payload))),
        ]
        if extra_headers:
            headers.extend(extra_headers)
        start_response(status, headers)
        return [payload]


def _render_error_page(*, title: str, heading: str, message: str) -> str:
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\">\n"
        f"    <title>{escape(title)}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"    <h1>{escape(heading)}</h1>\n"
        f"    <p>{escape(message)}</p>\n"
        "  </body>\n"
        "</html>\n"
    )


def render_search_results_page(
    public_api: SearchPublicApi,
    query: str,
) -> str:
    normalized_query = query.strip()
    if not normalized_query:
        return render_search_results_html(
            {
                "query": "",
                "result_count": 0,
                "results": [],
            }
        )

    response = public_api.search_records(SearchCatalogRequest.from_parts(normalized_query))
    search_results = search_response_envelope_to_search_results_view_model(response.body)
    return render_search_results_html(search_results)


def render_comparison_page(
    public_api: ComparisonPublicApi | None,
    left_target_ref: str,
    right_target_ref: str,
) -> str:
    left = left_target_ref.strip()
    right = right_target_ref.strip()
    if not left or not right:
        return render_comparison_html(
            None,
            left_target_ref=left,
            right_target_ref=right,
            message=(
                "Provide both left and right target references to compare two bounded results side by side."
            ),
        )

    if public_api is None:
        return render_comparison_html(
            None,
            left_target_ref=left,
            right_target_ref=right,
            message="This bootstrap workbench was not configured with a public comparison boundary.",
        )

    response = public_api.compare_targets(CompareTargetsRequest.from_parts(left, right))
    comparison = comparison_envelope_to_view_model(response.body)
    return render_comparison_html(
        comparison,
        left_target_ref=left,
        right_target_ref=right,
    )


def render_bundle_inspection_page(
    public_api: ResolutionBundleInspectionPublicApi | None,
    bundle_path: str,
) -> str:
    normalized_bundle_path = bundle_path.strip()
    if not normalized_bundle_path:
        return render_bundle_inspection_html(
            {
                "status": "blocked",
                "inspection_mode": "local_offline",
                "source": {
                    "kind": "local_path",
                    "locator": "(not provided)",
                },
                "notices": [
                    {
                        "code": "bundle_path_required",
                        "severity": "error",
                        "message": "Provide a local bundle_path query parameter to inspect a bundle in this bootstrap demo.",
                    }
                ],
            }
        )

    if public_api is None:
        return render_bundle_inspection_html(
            {
                "status": "blocked",
                "inspection_mode": "local_offline",
                "source": {
                    "kind": "local_path",
                    "locator": normalized_bundle_path,
                },
                "notices": [
                    {
                        "code": "bundle_inspection_unavailable",
                        "severity": "error",
                        "message": "This bootstrap workbench was not configured with a public bundle inspection boundary.",
                    }
                ],
            }
        )

    response = public_api.inspect_bundle(
        InspectResolutionBundleRequest.from_bundle_path(normalized_bundle_path),
    )
    bundle_inspection = bundle_inspection_envelope_to_view_model(response.body)
    return render_bundle_inspection_html(bundle_inspection)

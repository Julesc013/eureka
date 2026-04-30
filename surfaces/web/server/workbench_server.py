from __future__ import annotations

import json
from html import escape
from typing import Callable
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
    ResolutionMemoryPublicApi,
    ResolutionMemoryReadRequest,
    LocalTaskReadRequest,
    LocalTaskRunRequest,
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
    PublicSearchPublicApi,
    ResolutionRunReadRequest,
    ResolutionWorkspaceReadError,
    SearchCatalogRequest,
    SearchPublicApi,
    SourceCatalogRequest,
    SourceReadRequest,
    SourceRegistryPublicApi,
    SubjectStatesCatalogRequest,
    SubjectStatesPublicApi,
    StoredArtifactRequest,
    StoredExportsPublicApi,
    StoredExportsTargetRequest,
    acquisition_envelope_to_view_model,
    action_plan_envelope_to_view_model,
    archive_resolution_evals_envelope_to_view_model,
    build_demo_local_index_public_api,
    build_demo_local_tasks_public_api,
    build_demo_public_search_public_api,
    build_demo_archive_resolution_evals_public_api,
    build_demo_resolution_memory_public_api,
    build_demo_resolution_runs_public_api,
    build_resolution_workspace_view_models,
    absence_envelope_to_view_model,
    bundle_inspection_envelope_to_view_model,
    comparison_envelope_to_view_model,
    compatibility_envelope_to_view_model,
    local_index_envelope_to_view_model,
    local_tasks_envelope_to_view_model,
    resolution_memory_envelope_to_view_model,
    representations_envelope_to_view_model,
    resolution_runs_envelope_to_view_model,
    query_plan_envelope_to_view_model,
    search_response_envelope_to_search_results_view_model,
    source_registry_envelope_to_view_model,
    subject_states_envelope_to_view_model,
)
from surfaces.web.server.api_routes import handle_api_request
from surfaces.web.server.api_serialization import SerializedHttpResponse, status_line
from surfaces.web.server.route_policy import PublicAlphaRoutePolicy
from surfaces.web.server.server_config import WebServerConfig, default_web_server_config
from surfaces.web.workbench import (
    render_acquisition_html,
    render_action_plan_html,
    render_absence_report_html,
    render_archive_resolution_evals_html,
    render_bundle_inspection_html,
    render_compatibility_html,
    render_comparison_html,
    render_decomposition_html,
    render_handoff_html,
    render_local_index_html,
    render_resolution_memory_html,
    render_local_tasks_html,
    render_member_access_html,
    render_query_plan_html,
    render_public_search_html,
    render_representations_html,
    render_resolution_runs_html,
    render_resolution_workspace_html,
    render_search_results_html,
    render_source_registry_html,
    render_subject_states_html,
)


def render_resolution_workspace_page(
    resolution_public_api: ResolutionJobsPublicApi,
    target_ref: str,
    *,
    action_plan_public_api: ActionPlanPublicApi | None = None,
    handoff_public_api: RepresentationSelectionPublicApi | None = None,
    actions_public_api: ResolutionActionsPublicApi | None = None,
    stored_exports_public_api: StoredExportsPublicApi | None = None,
    session_id: str = "session.web-workbench",
    host_profile_id: str | None = None,
    strategy_id: str | None = None,
    allow_payload_readback: bool = True,
) -> str:
    try:
        workspace = build_resolution_workspace_view_models(
            resolution_public_api,
            target_ref,
            action_plan_public_api=action_plan_public_api,
            handoff_public_api=handoff_public_api,
            actions_public_api=actions_public_api,
            stored_exports_public_api=stored_exports_public_api,
            session_id=session_id,
            host_profile_id=host_profile_id,
            strategy_id=strategy_id,
        )
    except ResolutionWorkspaceReadError as error:
        return _render_error_page(
            title="Eureka Compatibility Workbench",
            heading="Resolution Job Not Found",
            message=str(error),
        )
    except ValueError as error:
        return _render_error_page(
            title="Eureka Compatibility Workbench",
            heading="Invalid Workspace Request",
            message=str(error),
        )
    return render_resolution_workspace_html(
        workspace.workbench_session,
        action_plan=workspace.action_plan,
        handoff=workspace.handoff,
        resolution_actions=workspace.resolution_actions,
        stored_exports=workspace.stored_exports,
        host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
        strategy_profile_presets=BOOTSTRAP_STRATEGY_PROFILES,
        allow_payload_readback=allow_payload_readback,
    )


def render_action_plan_page(
    public_api: ActionPlanPublicApi | None,
    target_ref: str,
    host_profile_id: str | None,
    strategy_id: str | None,
    *,
    store_actions_enabled: bool = False,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_host_profile_id = (host_profile_id or "").strip() or None
    normalized_strategy_id = (strategy_id or "").strip() or None
    if not normalized_target_ref:
        return render_action_plan_html(
            None,
            target_ref="",
            host_profile_id=normalized_host_profile_id,
            strategy_id=normalized_strategy_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
            message="Provide a bounded target ref to build an action plan.",
        )
    if public_api is None:
        return render_action_plan_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            strategy_id=normalized_strategy_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
            message="This bootstrap workbench was not configured with a public action-plan boundary.",
        )
    try:
        response = public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                normalized_target_ref,
                normalized_host_profile_id,
                normalized_strategy_id,
                store_actions_enabled=store_actions_enabled,
            )
        )
    except ValueError as error:
        return render_action_plan_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            strategy_id=normalized_strategy_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
            message=str(error),
        )
    return render_action_plan_html(
        action_plan_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        host_profile_id=normalized_host_profile_id,
        strategy_id=normalized_strategy_id,
        host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
        strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
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
    *,
    allow_payload_readback: bool = True,
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
    return render_representations_html(
        representations_envelope_to_view_model(response.body),
        allow_payload_readback=allow_payload_readback,
    )


def render_decomposition_page(
    public_api: DecompositionPublicApi | None,
    target_ref: str,
    representation_id: str,
    *,
    allow_member_readback: bool = True,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_representation_id = representation_id.strip()
    if not normalized_representation_id:
        return render_decomposition_html(
            None,
            target_ref=normalized_target_ref,
            representation_id="",
            message="Provide a bounded representation_id to inspect one fetched representation.",
            allow_member_readback=allow_member_readback,
        )
    if public_api is None:
        return render_decomposition_html(
            None,
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
            message="This bootstrap workbench was not configured with a public decomposition boundary.",
            allow_member_readback=allow_member_readback,
        )
    try:
        response = public_api.decompose_representation(
            DecompositionInspectionRequest.from_parts(
                normalized_target_ref,
                normalized_representation_id,
            )
        )
    except ValueError as error:
        return render_decomposition_html(
            None,
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
            message=str(error),
            allow_member_readback=allow_member_readback,
        )
    return render_decomposition_html(
        decomposition_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        representation_id=normalized_representation_id,
        allow_member_readback=allow_member_readback,
    )


def render_member_access_page(
    public_api: MemberAccessPublicApi | None,
    target_ref: str,
    representation_id: str,
    member_path: str,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_representation_id = representation_id.strip()
    normalized_member_path = member_path.strip()
    if not normalized_representation_id or not normalized_member_path:
        return render_member_access_html(
            None,
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
            member_path=normalized_member_path,
            message="Provide bounded representation_id and member_path values to read one listed package member.",
        )
    if public_api is None:
        return render_member_access_html(
            None,
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
            member_path=normalized_member_path,
            message="This bootstrap workbench was not configured with a public member-access boundary.",
        )
    try:
        response = public_api.read_member(
            MemberAccessReadRequest.from_parts(
                normalized_target_ref,
                normalized_representation_id,
                normalized_member_path,
            )
        )
    except ValueError as error:
        return render_member_access_html(
            None,
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
            member_path=normalized_member_path,
            message=str(error),
        )
    return render_member_access_html(
        member_access_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        representation_id=normalized_representation_id,
        member_path=normalized_member_path,
    )


def render_handoff_page(
    public_api: RepresentationSelectionPublicApi | None,
    target_ref: str,
    host_profile_id: str | None,
    strategy_id: str | None,
    *,
    allow_payload_readback: bool = True,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_host_profile_id = (host_profile_id or "").strip() or None
    normalized_strategy_id = (strategy_id or "").strip() or None
    if not normalized_target_ref:
        return render_handoff_html(
            None,
            target_ref="",
            host_profile_id=normalized_host_profile_id,
            strategy_id=normalized_strategy_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
            message="Provide a bounded target ref to evaluate a representation handoff recommendation.",
            allow_payload_readback=allow_payload_readback,
        )
    if public_api is None:
        return render_handoff_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            strategy_id=normalized_strategy_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
            message="This bootstrap workbench was not configured with a public representation-selection boundary.",
            allow_payload_readback=allow_payload_readback,
        )
    try:
        response = public_api.select_representation(
            RepresentationSelectionEvaluationRequest.from_parts(
                normalized_target_ref,
                normalized_host_profile_id,
                normalized_strategy_id,
            )
        )
    except ValueError as error:
        return render_handoff_html(
            None,
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            strategy_id=normalized_strategy_id,
            host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
            strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
            message=str(error),
            allow_payload_readback=allow_payload_readback,
        )
    return render_handoff_html(
        representation_selection_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        host_profile_id=normalized_host_profile_id,
        strategy_id=normalized_strategy_id,
        host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
        strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
        allow_payload_readback=allow_payload_readback,
    )


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
        acquisition_public_api: AcquisitionPublicApi | None = None,
        decomposition_public_api: DecompositionPublicApi | None = None,
        member_access_public_api: MemberAccessPublicApi | None = None,
        action_plan_public_api: ActionPlanPublicApi | None = None,
        archive_resolution_evals_public_api: ArchiveResolutionEvalsPublicApi | None = None,
        handoff_public_api: RepresentationSelectionPublicApi | None = None,
        query_planner_public_api: QueryPlannerPublicApi | None = None,
        subject_states_public_api: SubjectStatesPublicApi | None = None,
        representations_public_api: RepresentationsPublicApi | None = None,
        actions_public_api: ResolutionActionsPublicApi | None = None,
        bundle_inspection_public_api: ResolutionBundleInspectionPublicApi | None = None,
        local_index_public_api: LocalIndexPublicApi | None = None,
        stored_exports_public_api: StoredExportsPublicApi | None = None,
        search_public_api: SearchPublicApi,
        public_search_public_api: PublicSearchPublicApi | None = None,
        source_registry_public_api: SourceRegistryPublicApi | None = None,
        default_target_ref: str,
        session_id: str = "session.web-workbench",
        server_config: WebServerConfig | None = None,
    ) -> None:
        self._resolution_public_api = resolution_public_api
        self._absence_public_api = absence_public_api
        self._comparison_public_api = comparison_public_api
        self._compatibility_public_api = compatibility_public_api
        self._acquisition_public_api = acquisition_public_api
        self._decomposition_public_api = decomposition_public_api
        self._member_access_public_api = member_access_public_api
        self._action_plan_public_api = action_plan_public_api
        self._archive_resolution_evals_public_api = archive_resolution_evals_public_api
        self._handoff_public_api = handoff_public_api
        self._query_planner_public_api = query_planner_public_api
        self._subject_states_public_api = subject_states_public_api
        self._representations_public_api = representations_public_api
        self._actions_public_api = actions_public_api
        self._bundle_inspection_public_api = bundle_inspection_public_api
        self._local_index_public_api = local_index_public_api
        self._stored_exports_public_api = stored_exports_public_api
        self._search_public_api = search_public_api
        self._public_search_public_api = public_search_public_api
        self._source_registry_public_api = source_registry_public_api
        self._default_target_ref = default_target_ref
        self._session_id = session_id
        self._server_config = server_config or default_web_server_config()

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
            acquisition_public_api=self._acquisition_public_api,
            decomposition_public_api=self._decomposition_public_api,
            member_access_public_api=self._member_access_public_api,
            action_plan_public_api=self._action_plan_public_api,
            archive_resolution_evals_public_api=self._archive_resolution_evals_public_api,
            handoff_public_api=self._handoff_public_api,
            query_planner_public_api=self._query_planner_public_api,
            subject_states_public_api=self._subject_states_public_api,
            representations_public_api=self._representations_public_api,
            actions_public_api=self._actions_public_api,
            bundle_inspection_public_api=self._bundle_inspection_public_api,
            local_index_public_api=self._local_index_public_api,
            search_public_api=self._search_public_api,
            source_registry_public_api=self._source_registry_public_api,
            session_id=self._session_id,
            public_search_public_api=self._public_search_public_api,
            server_config=self._server_config,
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
            "/status",
            "/absence/resolve",
            "/absence/search",
            "/compare",
            "/compatibility",
            "/decompose",
            "/evals/archive-resolution",
            "/fetch",
            "/member",
            "/query-plan",
            "/action-plan",
            "/handoff",
            "/index/build",
            "/index/search",
            "/index/status",
            "/memories",
            "/memory",
            "/memory/create",
            "/representations",
            "/task",
            "/task/run/build-local-index",
            "/task/run/query-local-index",
            "/task/run/validate-archive-resolution-evals",
            "/task/run/validate-source-registry",
            "/tasks",
            "/run",
            "/run/resolve",
            "/run/search",
            "/run/planned-search",
            "/source",
            "/sources",
            "/runs",
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
                        "'/status', '/absence/resolve', '/absence/search', '/compare', '/compatibility', '/decompose', '/evals/archive-resolution', '/fetch', '/member', '/query-plan', '/action-plan', '/handoff', '/index/build', '/index/status', '/index/search', '/representations', '/tasks', '/task', '/task/run/validate-source-registry', '/task/run/build-local-index', '/task/run/query-local-index', '/task/run/validate-archive-resolution-evals', '/runs', '/run', '/run/resolve', '/run/search', '/run/planned-search', '/sources', '/source', '/subject', '/inspect/bundle', '/actions/export-resolution-manifest', and "
                        "'/actions/export-resolution-bundle', '/store/manifest', "
                        "'/store/bundle', '/stored/artifact', '/memories', '/memory', and "
                        "'/memory/create'."
                    ),
                ),
            )

        query = parse_qs(query_string, keep_blank_values=False)
        route_decision = PublicAlphaRoutePolicy(self._server_config).evaluate_web_request(path, query)
        if not route_decision.allowed:
            return self._respond(
                start_response,
                status="403 Forbidden",
                body=_render_blocked_page(route_decision.to_blocked_payload()),
            )

        if path == "/status":
            return self._respond(
                start_response,
                status="200 OK",
                body=_render_status_page(self._server_config.to_status_dict()),
            )

        if path == "/":
            target_ref = self._resolve_target_ref(query_string)
            page = render_resolution_workspace_page(
                self._resolution_public_api,
                target_ref,
                action_plan_public_api=self._action_plan_public_api,
                handoff_public_api=self._handoff_public_api,
                actions_public_api=(
                    self._actions_public_api
                    if self._server_config.allow_write_actions
                    else None
                ),
                stored_exports_public_api=(
                    self._stored_exports_public_api
                    if self._server_config.allow_write_actions
                    else None
                ),
                session_id=self._session_id,
                host_profile_id=self._resolve_optional_host_profile_id(query_string),
                strategy_id=self._resolve_optional_strategy_id(query_string),
                allow_payload_readback=self._server_config.allow_local_paths,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/action-plan":
            target_ref = self._resolve_target_ref(query_string)
            host_profile_id = self._resolve_optional_host_profile_id(query_string)
            page = render_action_plan_page(
                self._action_plan_public_api,
                target_ref,
                host_profile_id,
                self._resolve_optional_strategy_id(query_string),
                store_actions_enabled=(
                    self._stored_exports_public_api is not None
                    and self._server_config.allow_write_actions
                ),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/query-plan":
            page = render_query_plan_page(
                self._query_planner_public_api,
                self._resolve_search_query(query_string),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/evals/archive-resolution":
            page = render_archive_resolution_evals_page(
                self._archive_resolution_evals_public_api
                or build_demo_archive_resolution_evals_public_api(),
                task_id=self._resolve_optional_query_value(query_string, "task_id"),
                index_path=(
                    self._resolve_optional_query_value(query_string, "index_path")
                    if self._server_config.allow_local_paths
                    else None
                ),
                allow_index_path=self._server_config.allow_local_paths,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/handoff":
            target_ref = self._resolve_target_ref(query_string)
            page = render_handoff_page(
                self._handoff_public_api,
                target_ref,
                self._resolve_optional_host_profile_id(query_string),
                self._resolve_optional_strategy_id(query_string),
                allow_payload_readback=self._server_config.allow_local_paths,
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
        if path == "/fetch":
            target_ref = self._resolve_target_ref(query_string)
            representation_id = self._resolve_representation_id(query_string)
            if not representation_id:
                return self._respond(
                    start_response,
                    status="200 OK",
                    body=render_acquisition_html(
                        None,
                        target_ref=target_ref,
                        representation_id="",
                        message="Provide a bounded representation_id to fetch one local fixture payload.",
                    ),
                )
            if self._acquisition_public_api is None:
                return self._respond(
                    start_response,
                    status="200 OK",
                    body=render_acquisition_html(
                        None,
                        target_ref=target_ref,
                        representation_id=representation_id,
                        message="This bootstrap workbench was not configured with a public acquisition boundary.",
                    ),
                )
            try:
                response = self._acquisition_public_api.fetch_representation(
                    AcquisitionFetchRequest.from_parts(target_ref, representation_id),
                )
            except ValueError as error:
                return self._respond(
                    start_response,
                    status="200 OK",
                    body=render_acquisition_html(
                        None,
                        target_ref=target_ref,
                        representation_id=representation_id,
                        message=str(error),
                    ),
                )
            if response.status_code == 200 and response.payload is not None and response.content_type is not None:
                extra_headers: list[tuple[str, str]] = []
                if response.filename is not None:
                    extra_headers.append(
                        ("Content-Disposition", f"attachment; filename=\"{response.filename}\""),
                    )
                return self._respond_bytes(
                    start_response,
                    status="200 OK",
                    payload=response.payload,
                    content_type=response.content_type,
                    extra_headers=extra_headers,
                )
            return self._respond(
                start_response,
                status=(
                    "404 Not Found"
                    if response.status_code == 404
                    else "422 Unprocessable Entity"
                    if response.status_code == 422
                    else "503 Service Unavailable"
                ),
                body=render_acquisition_html(
                    acquisition_envelope_to_view_model(response.body),
                    target_ref=target_ref,
                    representation_id=representation_id,
                ),
            )
        if path == "/decompose":
            target_ref = self._resolve_target_ref(query_string)
            representation_id = self._resolve_representation_id(query_string)
            page = render_decomposition_page(
                self._decomposition_public_api,
                target_ref,
                representation_id,
                allow_member_readback=self._server_config.allow_local_paths,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/member":
            target_ref = self._resolve_target_ref(query_string)
            representation_id = self._resolve_representation_id(query_string)
            member_path = self._resolve_member_path(query_string)
            if self._resolve_raw_requested(query_string):
                if not representation_id or not member_path:
                    return self._respond(
                        start_response,
                        status="200 OK",
                        body=render_member_access_html(
                            None,
                            target_ref=target_ref,
                            representation_id=representation_id,
                            member_path=member_path,
                            message="Provide bounded representation_id and member_path values to read raw member bytes.",
                        ),
                    )
                if self._member_access_public_api is None:
                    return self._respond(
                        start_response,
                        status="200 OK",
                        body=render_member_access_html(
                            None,
                            target_ref=target_ref,
                            representation_id=representation_id,
                            member_path=member_path,
                            message="This bootstrap workbench was not configured with a public member-access boundary.",
                        ),
                    )
                try:
                    response = self._member_access_public_api.read_member(
                        MemberAccessReadRequest.from_parts(target_ref, representation_id, member_path)
                    )
                except ValueError as error:
                    return self._respond(
                        start_response,
                        status="200 OK",
                        body=render_member_access_html(
                            None,
                            target_ref=target_ref,
                            representation_id=representation_id,
                            member_path=member_path,
                            message=str(error),
                        ),
                    )
                if response.status_code == 200 and response.payload is not None and response.content_type is not None:
                    extra_headers: list[tuple[str, str]] = []
                    if response.filename is not None:
                        extra_headers.append(
                            ("Content-Disposition", f"attachment; filename=\"{response.filename}\""),
                        )
                    return self._respond_bytes(
                        start_response,
                        status="200 OK",
                        payload=response.payload,
                        content_type=response.content_type,
                        extra_headers=extra_headers,
                    )
                return self._respond(
                    start_response,
                    status=(
                        "404 Not Found"
                        if response.status_code == 404
                        else "422 Unprocessable Entity"
                        if response.status_code == 422
                        else "503 Service Unavailable"
                    ),
                    body=render_member_access_html(
                        member_access_envelope_to_view_model(response.body),
                        target_ref=target_ref,
                        representation_id=representation_id,
                        member_path=member_path,
                    ),
                )
            page = render_member_access_page(
                self._member_access_public_api,
                target_ref,
                representation_id,
                member_path,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/representations":
            target_ref = self._resolve_target_ref(query_string)
            page = render_representations_page(
                self._representations_public_api,
                target_ref,
                allow_payload_readback=self._server_config.allow_local_paths,
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
            status, page = render_public_search_page(
                self._public_search_public_api or build_demo_public_search_public_api(),
                parse_qs(query_string, keep_blank_values=False),
            )
            return self._respond(start_response, status=status, body=page)
        if path == "/index/build":
            page = render_local_index_page(
                self._local_index_public_api or build_demo_local_index_public_api(),
                index_path=self._resolve_optional_query_value(query_string, "index_path") or "",
                build=True,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/index/status":
            page = render_local_index_page(
                self._local_index_public_api or build_demo_local_index_public_api(),
                index_path=self._resolve_optional_query_value(query_string, "index_path") or "",
                status_only=True,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/index/search":
            page = render_local_index_page(
                self._local_index_public_api or build_demo_local_index_public_api(),
                index_path=self._resolve_optional_query_value(query_string, "index_path") or "",
                query=self._resolve_search_query(query_string),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/tasks":
            page = render_local_tasks_page(
                self._resolve_optional_query_value(query_string, "task_store_root"),
                requested_index_path=self._resolve_optional_query_value(query_string, "index_path") or "",
                requested_query=self._resolve_optional_query_value(query_string, "q") or "",
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/task":
            page = render_local_tasks_page(
                self._resolve_optional_query_value(query_string, "task_store_root"),
                task_id=self._resolve_optional_query_value(query_string, "id"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/task/run/validate-source-registry":
            page = render_validate_source_registry_task_page(
                self._resolve_optional_query_value(query_string, "task_store_root"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/task/run/build-local-index":
            page = render_build_local_index_task_page(
                self._resolve_optional_query_value(query_string, "task_store_root"),
                self._resolve_optional_query_value(query_string, "index_path") or "",
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/task/run/query-local-index":
            page = render_query_local_index_task_page(
                self._resolve_optional_query_value(query_string, "task_store_root"),
                self._resolve_optional_query_value(query_string, "index_path") or "",
                self._resolve_search_query(query_string),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/task/run/validate-archive-resolution-evals":
            page = render_validate_archive_resolution_evals_task_page(
                self._resolve_optional_query_value(query_string, "task_store_root"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/memories":
            page = render_resolution_memory_page(
                self._resolve_optional_query_value(query_string, "memory_store_root"),
                run_store_root=self._resolve_optional_query_value(query_string, "run_store_root"),
                requested_run_id=self._resolve_optional_query_value(query_string, "run_id") or "",
                memory_kind=self._resolve_optional_query_value(query_string, "kind"),
                source_run_id=self._resolve_optional_query_value(query_string, "source_run_id"),
                task_kind=self._resolve_optional_query_value(query_string, "task_kind"),
                checked_source_id=self._resolve_optional_query_value(query_string, "source_id"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/memory":
            page = render_resolution_memory_page(
                self._resolve_optional_query_value(query_string, "memory_store_root"),
                memory_id=self._resolve_optional_query_value(query_string, "id"),
                run_store_root=self._resolve_optional_query_value(query_string, "run_store_root"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/memory/create":
            page = render_create_resolution_memory_page(
                self._resolve_optional_query_value(query_string, "memory_store_root"),
                run_store_root=self._resolve_optional_query_value(query_string, "run_store_root"),
                run_id=self._resolve_optional_query_value(query_string, "run_id") or "",
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/sources":
            page = render_source_registry_page(
                self._source_registry_public_api,
                status=self._resolve_optional_query_value(query_string, "status"),
                source_family=self._resolve_optional_query_value(query_string, "family"),
                role=self._resolve_optional_query_value(query_string, "role"),
                surface=self._resolve_optional_query_value(query_string, "surface"),
                coverage_depth=self._resolve_optional_query_value(query_string, "coverage_depth"),
                capability=self._resolve_optional_query_value(query_string, "capability"),
                connector_mode=self._resolve_optional_query_value(query_string, "connector_mode"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/source":
            page = render_source_registry_page(
                self._source_registry_public_api,
                source_id=self._resolve_optional_query_value(query_string, "id"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/runs":
            page = render_resolution_runs_page(
                self._resolve_optional_query_value(query_string, "run_store_root"),
                requested_target_ref=self._resolve_optional_query_value(query_string, "target_ref") or "",
                requested_query=self._resolve_optional_query_value(query_string, "q") or "",
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/run":
            page = render_resolution_runs_page(
                self._resolve_optional_query_value(query_string, "run_store_root"),
                run_id=self._resolve_optional_query_value(query_string, "id"),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/run/resolve":
            page = render_exact_resolution_run_page(
                self._resolve_optional_query_value(query_string, "run_store_root"),
                self._resolve_optional_query_value(query_string, "target_ref") or "",
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/run/search":
            page = render_deterministic_search_run_page(
                self._resolve_optional_query_value(query_string, "run_store_root"),
                self._resolve_search_query(query_string),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/run/planned-search":
            page = render_planned_search_run_page(
                self._resolve_optional_query_value(query_string, "run_store_root"),
                self._resolve_search_query(query_string),
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

    def _resolve_optional_strategy_id(self, query_string: str) -> str | None:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_strategy_id = query.get("strategy", [""])[0].strip()
        return raw_strategy_id or None

    def _resolve_bundle_path(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_bundle_path = query.get("bundle_path", [""])[0].strip()
        return raw_bundle_path

    def _resolve_subject_key(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        return query.get("key", [""])[0].strip()

    def _resolve_optional_query_value(self, query_string: str, name: str) -> str | None:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_value = query.get(name, [""])[0].strip()
        return raw_value or None

    def _resolve_artifact_id(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_artifact_id = query.get("artifact_id", [""])[0].strip()
        return raw_artifact_id

    def _resolve_representation_id(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_representation_id = query.get("representation_id", [""])[0].strip()
        return raw_representation_id

    def _resolve_member_path(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_member_path = query.get("member_path", [""])[0].strip()
        return raw_member_path

    def _resolve_raw_requested(self, query_string: str) -> bool:
        query = parse_qs(query_string, keep_blank_values=False)
        return bool(query.get("raw", [""])[0].strip())

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


def _render_blocked_page(payload: dict[str, object]) -> str:
    blocked_parameters = payload.get("blocked_parameters")
    parameter_text = ""
    if isinstance(blocked_parameters, list) and blocked_parameters:
        parameter_text = (
            "      <p>Blocked parameters: "
            f"{escape(', '.join(str(item) for item in blocked_parameters))}</p>\n"
        )
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\">\n"
        "    <title>Eureka Public Alpha Blocked</title>\n"
        "  </head>\n"
        "  <body>\n"
        "    <h1>Operation Blocked</h1>\n"
        f"    <p>{escape(str(payload.get('message') or 'This operation is blocked.'))}</p>\n"
        f"    <p>Mode: {escape(str(payload.get('mode') or 'unknown'))}</p>\n"
        f"    <p>Code: {escape(str(payload.get('code') or 'blocked'))}</p>\n"
        f"{parameter_text}"
        "    <p><a href=\"/status\">View server status</a></p>\n"
        "  </body>\n"
        "</html>\n"
    )


def _render_status_page(status: dict[str, object]) -> str:
    configured_roots = _string_mapping(status.get("configured_root_kinds"))
    enabled = _string_list(status.get("enabled_capabilities"))
    disabled = _string_list(status.get("disabled_capabilities"))
    notices = status.get("notices")
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Server Status</title>",
        "  </head>",
        "  <body>",
        "    <h1>Eureka Server Status</h1>",
        "    <dl>",
        f"      <dt>Mode</dt><dd>{escape(str(status.get('mode') or 'unknown'))}</dd>",
        f"      <dt>Safe mode</dt><dd>{escape(str(status.get('safe_mode_enabled')))}</dd>",
        f"      <dt>Created by</dt><dd>{escape(str(status.get('created_by_slice') or 'unknown'))}</dd>",
        "    </dl>",
        "    <h2>Configured Root Kinds</h2>",
        f"    <p>{escape(configured_roots)}</p>",
        "    <h2>Enabled Capabilities</h2>",
        f"    <p>{escape(enabled)}</p>",
        "    <h2>Disabled Capabilities</h2>",
        f"    <p>{escape(disabled)}</p>",
    ]
    if isinstance(notices, list) and notices:
        parts.extend(["    <h2>Notices</h2>", "    <ul>"])
        for item in notices:
            if isinstance(item, dict):
                parts.append(
                    "      <li>"
                    f"{escape(str(item.get('code') or 'notice'))}: "
                    f"{escape(str(item.get('message') or ''))}"
                    "</li>"
                )
        parts.append("    </ul>")
    parts.extend(["  </body>", "</html>", ""])
    return "\n".join(parts)


def _string_mapping(value: object) -> str:
    if not isinstance(value, dict) or not value:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in sorted(value.items()))


def _string_list(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "(none)"
    return ", ".join(str(item) for item in value)


def render_public_search_page(
    public_api: PublicSearchPublicApi,
    query: dict[str, list[str]],
) -> tuple[str, str]:
    raw_query_values = query.get("q") or []
    if not query or (raw_query_values and not raw_query_values[0].strip() and len(query) == 1):
        return "200 OK", render_public_search_html(None)

    response = public_api.search(query, default_profile="standard_web")
    return status_line(response.status_code), render_public_search_html(response.body)


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


def render_query_plan_page(
    public_api: QueryPlannerPublicApi | None,
    query: str,
) -> str:
    normalized_query = query.strip()
    if public_api is None:
        return render_query_plan_html(
            {
                "status": "blocked",
                "query_plan": None,
                "raw_query": normalized_query,
                "notices": [
                    {
                        "code": "query_planner_unavailable",
                        "severity": "warning",
                        "message": "This bootstrap workbench was not configured with a public query-planner boundary.",
                    }
                ],
            }
        )
    response = public_api.plan_query_text(normalized_query)
    return render_query_plan_html(query_plan_envelope_to_view_model(response.body))


def render_archive_resolution_evals_page(
    public_api: ArchiveResolutionEvalsPublicApi | None,
    *,
    task_id: str | None = None,
    index_path: str | None = None,
    allow_index_path: bool = True,
) -> str:
    normalized_task_id = (task_id or "").strip()
    normalized_index_path = (index_path or "").strip()
    if public_api is None:
        return render_archive_resolution_evals_html(
            {
                "status": "blocked",
                "eval_suite": None,
                "notices": [
                    {
                        "code": "archive_resolution_evals_unavailable",
                        "severity": "warning",
                        "message": "This bootstrap workbench was not configured with a public archive-resolution eval boundary.",
                    }
                ],
            },
            requested_task_id=normalized_task_id,
            requested_index_path=normalized_index_path,
            allow_index_path=allow_index_path,
        )
    request = ArchiveResolutionEvalRunRequest.from_parts(
        task_id=normalized_task_id,
        index_path=normalized_index_path,
    )
    response = public_api.run_task(request) if request.task_id is not None else public_api.run_suite(request)
    return render_archive_resolution_evals_html(
        archive_resolution_evals_envelope_to_view_model(response.body),
        requested_task_id=normalized_task_id,
        requested_index_path=normalized_index_path,
        allow_index_path=allow_index_path,
    )


def render_local_index_page(
    public_api: LocalIndexPublicApi | None,
    *,
    index_path: str,
    query: str = "",
    build: bool = False,
    status_only: bool = False,
) -> str:
    normalized_index_path = index_path.strip()
    normalized_query = query.strip()
    if public_api is None:
        return render_local_index_html(
            {
                "status": "blocked",
                "index": {
                    "index_path_kind": "bootstrap_local_path",
                    "index_path": normalized_index_path or None,
                    "fts_mode": "fallback_like",
                    "record_count": 0,
                    "record_kind_counts": {},
                },
                "results": [],
                "notices": [
                    {
                        "code": "local_index_unavailable",
                        "severity": "warning",
                        "message": "This bootstrap workbench was not configured with a public local-index boundary.",
                    }
                ],
            },
            requested_index_path=normalized_index_path,
            requested_query=normalized_query,
        )
    if not normalized_index_path:
        return render_local_index_html(
            {
                "status": "blocked",
                "index": {
                    "index_path_kind": "bootstrap_local_path",
                    "index_path": None,
                    "fts_mode": "fallback_like",
                    "record_count": 0,
                    "record_kind_counts": {},
                },
                "results": [],
                "notices": [
                    {
                        "code": "index_path_required",
                        "severity": "warning",
                        "message": "Provide a bootstrap local index_path to build, inspect, or search the Local Index v0 database.",
                    }
                ],
            },
            requested_query=normalized_query,
        )
    if build:
        response = public_api.build_index(LocalIndexBuildRequest.from_parts(normalized_index_path))
        return render_local_index_html(
            local_index_envelope_to_view_model(response.body),
            requested_index_path=normalized_index_path,
            requested_query=normalized_query,
        )
    if status_only:
        response = public_api.get_index_status(LocalIndexStatusRequest.from_parts(normalized_index_path))
        return render_local_index_html(
            local_index_envelope_to_view_model(response.body),
            requested_index_path=normalized_index_path,
            requested_query=normalized_query,
        )
    if not normalized_query:
        return render_local_index_html(
            {
                "status": "available",
                "index": {
                    "index_path_kind": "bootstrap_local_path",
                    "index_path": normalized_index_path,
                    "fts_mode": "fallback_like",
                    "record_count": 0,
                    "record_kind_counts": {},
                },
                "results": [],
                "query": "",
                "result_count": 0,
                "notices": [
                    {
                        "code": "query_required",
                        "severity": "warning",
                        "message": "Provide a bounded text query to search the Local Index v0 database.",
                    }
                ],
            },
            requested_index_path=normalized_index_path,
            requested_query=normalized_query,
        )
    response = public_api.query_index(
        LocalIndexQueryRequest.from_parts(normalized_index_path, normalized_query),
    )
    return render_local_index_html(
        local_index_envelope_to_view_model(response.body),
        requested_index_path=normalized_index_path,
        requested_query=normalized_query,
    )


def render_source_registry_page(
    public_api: SourceRegistryPublicApi | None,
    *,
    source_id: str | None = None,
    status: str | None = None,
    source_family: str | None = None,
    role: str | None = None,
    surface: str | None = None,
    coverage_depth: str | None = None,
    capability: str | None = None,
    connector_mode: str | None = None,
) -> str:
    if public_api is None:
        return render_source_registry_html(
            {
                "status": "blocked",
                "source_count": 0,
                "sources": [],
                "notices": [
                    {
                        "code": "source_registry_unavailable",
                        "severity": "warning",
                        "message": "This bootstrap workbench was not configured with a public source-registry boundary.",
                    }
                ],
            }
        )

    if source_id is not None and source_id.strip():
        try:
            response = public_api.get_source(SourceReadRequest.from_parts(source_id))
        except ValueError as error:
            return render_source_registry_html(
                {
                    "status": "blocked",
                    "source_count": 0,
                    "selected_source_id": "",
                    "sources": [],
                    "notices": [
                        {
                            "code": "invalid_source_request",
                            "severity": "warning",
                            "message": str(error),
                        }
                    ],
                }
            )
        return render_source_registry_html(source_registry_envelope_to_view_model(response.body))

    response = public_api.list_sources(
        SourceCatalogRequest.from_parts(
            status=status,
            source_family=source_family,
            role=role,
            surface=surface,
            coverage_depth=coverage_depth,
            capability=capability,
            connector_mode=connector_mode,
        )
    )
    return render_source_registry_html(source_registry_envelope_to_view_model(response.body))


def render_local_tasks_page(
    task_store_root: str | None,
    *,
    task_id: str | None = None,
    requested_index_path: str = "",
    requested_query: str = "",
    message: str | None = None,
) -> str:
    empty_view_model = {
        "status": "listed",
        "task_count": 0,
        "tasks": [],
    }
    normalized_task_store_root = (task_store_root or "").strip() or None
    if normalized_task_store_root is None:
        return render_local_tasks_html(
            empty_view_model,
            requested_index_path=requested_index_path,
            requested_query=requested_query,
            message=message
            or "Provide a bootstrap task_store_root to list or inspect persisted local tasks.",
        )

    public_api = build_demo_local_tasks_public_api(normalized_task_store_root)
    if task_id is not None and task_id.strip():
        try:
            response = public_api.get_task(LocalTaskReadRequest.from_parts(task_id))
        except ValueError as error:
            return render_local_tasks_html(
                {
                    "status": "blocked",
                    "task_count": 0,
                    "selected_task_id": "",
                    "tasks": [],
                    "notices": [
                        {
                            "code": "invalid_task_request",
                            "severity": "warning",
                            "message": str(error),
                        }
                    ],
                },
                task_store_root=normalized_task_store_root,
                requested_index_path=requested_index_path,
                requested_query=requested_query,
            )
        return render_local_tasks_html(
            local_tasks_envelope_to_view_model(response.body),
            task_store_root=normalized_task_store_root,
            requested_index_path=requested_index_path,
            requested_query=requested_query,
        )
    response = public_api.list_tasks()
    return render_local_tasks_html(
        local_tasks_envelope_to_view_model(response.body),
        task_store_root=normalized_task_store_root,
        requested_index_path=requested_index_path,
        requested_query=requested_query,
        message=message,
    )


def render_validate_source_registry_task_page(task_store_root: str | None) -> str:
    return _render_run_local_task_page(
        task_store_root,
        task_kind="validate-source-registry",
        requested_inputs={},
        message_when_missing_root=(
            "Provide a bootstrap task_store_root to persist a source-registry validation task."
        ),
    )


def render_build_local_index_task_page(task_store_root: str | None, index_path: str) -> str:
    normalized_index_path = index_path.strip()
    return _render_run_local_task_page(
        task_store_root,
        task_kind="build-local-index",
        requested_inputs={"index_path": normalized_index_path},
        requested_index_path=normalized_index_path,
        message_when_missing_root=(
            "Provide a bootstrap task_store_root to persist a local-index build task."
        ),
    )


def render_query_local_index_task_page(
    task_store_root: str | None,
    index_path: str,
    query: str,
) -> str:
    normalized_index_path = index_path.strip()
    normalized_query = query.strip()
    return _render_run_local_task_page(
        task_store_root,
        task_kind="query-local-index",
        requested_inputs={"index_path": normalized_index_path, "query": normalized_query},
        requested_index_path=normalized_index_path,
        requested_query=normalized_query,
        message_when_missing_root=(
            "Provide a bootstrap task_store_root to persist a local-index query task."
        ),
    )


def render_validate_archive_resolution_evals_task_page(task_store_root: str | None) -> str:
    return _render_run_local_task_page(
        task_store_root,
        task_kind="validate-archive-resolution-evals",
        requested_inputs={},
        message_when_missing_root=(
            "Provide a bootstrap task_store_root to persist an archive-resolution eval validation task."
        ),
    )


def _render_run_local_task_page(
    task_store_root: str | None,
    *,
    task_kind: str,
    requested_inputs: dict[str, str],
    requested_index_path: str = "",
    requested_query: str = "",
    message_when_missing_root: str,
) -> str:
    normalized_task_store_root = (task_store_root or "").strip() or None
    if normalized_task_store_root is None:
        return render_local_tasks_html(
            {"status": "listed", "task_count": 0, "tasks": []},
            requested_index_path=requested_index_path,
            requested_query=requested_query,
            message=message_when_missing_root,
        )
    public_api = build_demo_local_tasks_public_api(normalized_task_store_root)
    response = public_api.run_task(
        LocalTaskRunRequest.from_parts(task_kind, requested_inputs),
    )
    return render_local_tasks_html(
        local_tasks_envelope_to_view_model(response.body),
        task_store_root=normalized_task_store_root,
        requested_index_path=requested_index_path,
        requested_query=requested_query,
    )


def render_resolution_memory_page(
    memory_store_root: str | None,
    *,
    memory_id: str | None = None,
    run_store_root: str | None = None,
    requested_run_id: str = "",
    memory_kind: str | None = None,
    source_run_id: str | None = None,
    task_kind: str | None = None,
    checked_source_id: str | None = None,
) -> str:
    empty_view_model = {
        "status": "listed",
        "memory_count": 0,
        "memories": [],
    }
    normalized_memory_store_root = (memory_store_root or "").strip() or None
    normalized_run_store_root = (run_store_root or "").strip() or None
    if normalized_memory_store_root is None:
        return render_resolution_memory_html(
            empty_view_model,
            run_store_root=normalized_run_store_root,
            requested_run_id=requested_run_id,
            message="Provide a bootstrap memory_store_root to list or inspect persisted resolution memory.",
        )

    public_api = build_demo_resolution_memory_public_api(
        normalized_memory_store_root,
        run_store_root=normalized_run_store_root,
    )
    if memory_id is not None and memory_id.strip():
        try:
            response = public_api.get_memory(ResolutionMemoryReadRequest.from_parts(memory_id))
        except ValueError as error:
            return render_resolution_memory_html(
                {
                    "status": "blocked",
                    "memory_count": 0,
                    "selected_memory_id": "",
                    "memories": [],
                    "notices": [
                        {
                            "code": "invalid_resolution_memory_request",
                            "severity": "warning",
                            "message": str(error),
                        }
                    ],
                },
                memory_store_root=normalized_memory_store_root,
                run_store_root=normalized_run_store_root,
                requested_run_id=requested_run_id,
            )
        return render_resolution_memory_html(
            resolution_memory_envelope_to_view_model(response.body),
            memory_store_root=normalized_memory_store_root,
            run_store_root=normalized_run_store_root,
            requested_run_id=requested_run_id,
        )

    response = public_api.list_memories(
        ResolutionMemoryCatalogRequest.from_parts(
            memory_kind=memory_kind,
            source_run_id=source_run_id,
            task_kind=task_kind,
            checked_source_id=checked_source_id,
        )
    )
    return render_resolution_memory_html(
        resolution_memory_envelope_to_view_model(response.body),
        memory_store_root=normalized_memory_store_root,
        run_store_root=normalized_run_store_root,
        requested_run_id=requested_run_id,
    )


def render_create_resolution_memory_page(
    memory_store_root: str | None,
    *,
    run_store_root: str | None,
    run_id: str,
) -> str:
    normalized_memory_store_root = (memory_store_root or "").strip() or None
    normalized_run_store_root = (run_store_root or "").strip() or None
    if normalized_memory_store_root is None:
        return render_resolution_memory_html(
            {
                "status": "blocked",
                "memory_count": 0,
                "memories": [],
                "notices": [
                    {
                        "code": "memory_store_root_required",
                        "severity": "warning",
                        "message": "Provide a bootstrap memory_store_root to create a resolution memory record.",
                    }
                ],
            },
            run_store_root=normalized_run_store_root,
            requested_run_id=run_id,
        )
    public_api = build_demo_resolution_memory_public_api(
        normalized_memory_store_root,
        run_store_root=normalized_run_store_root,
    )
    try:
        response = public_api.create_memory_from_run(
            ResolutionMemoryCreateRequest.from_parts(run_id),
        )
    except ValueError as error:
        return render_resolution_memory_html(
            {
                "status": "blocked",
                "memory_count": 0,
                "memories": [],
                "notices": [
                    {
                        "code": "invalid_resolution_memory_request",
                        "severity": "warning",
                        "message": str(error),
                    }
                ],
            },
            memory_store_root=normalized_memory_store_root,
            run_store_root=normalized_run_store_root,
            requested_run_id=run_id,
        )
    return render_resolution_memory_html(
        resolution_memory_envelope_to_view_model(response.body),
        memory_store_root=normalized_memory_store_root,
        run_store_root=normalized_run_store_root,
        requested_run_id=run_id,
    )


def render_resolution_runs_page(
    run_store_root: str | None,
    *,
    run_id: str | None = None,
    requested_target_ref: str = "",
    requested_query: str = "",
) -> str:
    empty_view_model = {
        "status": "listed",
        "run_count": 0,
        "runs": [],
    }
    normalized_run_store_root = (run_store_root or "").strip() or None
    if normalized_run_store_root is None:
        return render_resolution_runs_html(
            empty_view_model,
            requested_target_ref=requested_target_ref,
            requested_query=requested_query,
            message="Provide a bootstrap run_store_root to list or inspect persisted resolution runs.",
        )

    public_api = build_demo_resolution_runs_public_api(normalized_run_store_root)
    if run_id is not None and run_id.strip():
        try:
            response = public_api.get_run(ResolutionRunReadRequest.from_parts(run_id))
        except ValueError as error:
            return render_resolution_runs_html(
                {
                    "status": "blocked",
                    "run_count": 0,
                    "selected_run_id": "",
                    "runs": [],
                    "notices": [
                        {
                            "code": "invalid_run_request",
                            "severity": "warning",
                            "message": str(error),
                        }
                    ],
                },
                run_store_root=normalized_run_store_root,
                requested_target_ref=requested_target_ref,
                requested_query=requested_query,
            )
        return render_resolution_runs_html(
            resolution_runs_envelope_to_view_model(response.body),
            run_store_root=normalized_run_store_root,
            requested_target_ref=requested_target_ref,
            requested_query=requested_query,
        )
    response = public_api.list_runs()
    return render_resolution_runs_html(
        resolution_runs_envelope_to_view_model(response.body),
        run_store_root=normalized_run_store_root,
        requested_target_ref=requested_target_ref,
        requested_query=requested_query,
    )


def render_exact_resolution_run_page(
    run_store_root: str | None,
    target_ref: str,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_run_store_root = (run_store_root or "").strip() or None
    if normalized_target_ref == "":
        return render_resolution_runs_html(
            {"status": "listed", "run_count": 0, "runs": []},
            run_store_root=normalized_run_store_root,
            requested_target_ref="",
            message="Provide a bounded target_ref to start an exact-resolution run.",
        )
    if normalized_run_store_root is None:
        return render_resolution_runs_html(
            {"status": "listed", "run_count": 0, "runs": []},
            requested_target_ref=normalized_target_ref,
            message="Provide a bootstrap run_store_root to persist an exact-resolution run.",
        )
    public_api = build_demo_resolution_runs_public_api(normalized_run_store_root)
    response = public_api.start_exact_resolution_run(
        ExactResolutionRunRequest.from_parts(normalized_target_ref),
    )
    return render_resolution_runs_html(
        resolution_runs_envelope_to_view_model(response.body),
        run_store_root=normalized_run_store_root,
        requested_target_ref=normalized_target_ref,
    )


def render_deterministic_search_run_page(
    run_store_root: str | None,
    query: str,
) -> str:
    normalized_query = query.strip()
    normalized_run_store_root = (run_store_root or "").strip() or None
    if normalized_query == "":
        return render_resolution_runs_html(
            {"status": "listed", "run_count": 0, "runs": []},
            run_store_root=normalized_run_store_root,
            requested_query="",
            message="Provide a bounded query to start a deterministic-search run.",
        )
    if normalized_run_store_root is None:
        return render_resolution_runs_html(
            {"status": "listed", "run_count": 0, "runs": []},
            requested_query=normalized_query,
            message="Provide a bootstrap run_store_root to persist a deterministic-search run.",
        )
    public_api = build_demo_resolution_runs_public_api(normalized_run_store_root)
    response = public_api.start_deterministic_search_run(
        DeterministicSearchRunRequest.from_parts(normalized_query),
    )
    return render_resolution_runs_html(
        resolution_runs_envelope_to_view_model(response.body),
        run_store_root=normalized_run_store_root,
        requested_query=normalized_query,
    )


def render_planned_search_run_page(
    run_store_root: str | None,
    query: str,
) -> str:
    normalized_query = query.strip()
    normalized_run_store_root = (run_store_root or "").strip() or None
    if normalized_query == "":
        return render_resolution_runs_html(
            {"status": "listed", "run_count": 0, "runs": []},
            run_store_root=normalized_run_store_root,
            requested_query="",
            message="Provide a bounded raw query to start a planned-search run.",
        )
    if normalized_run_store_root is None:
        return render_resolution_runs_html(
            {"status": "listed", "run_count": 0, "runs": []},
            requested_query=normalized_query,
            message="Provide a bootstrap run_store_root to persist a planned-search run.",
        )
    public_api = build_demo_resolution_runs_public_api(normalized_run_store_root)
    response = public_api.start_planned_search_run(
        PlannedSearchRunRequest.from_parts(normalized_query),
    )
    return render_resolution_runs_html(
        resolution_runs_envelope_to_view_model(response.body),
        run_store_root=normalized_run_store_root,
        requested_query=normalized_query,
    )


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

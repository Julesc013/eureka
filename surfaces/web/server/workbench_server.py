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
    build_demo_local_index_public_api,
    build_demo_resolution_runs_public_api,
    build_resolution_workspace_view_models,
    absence_envelope_to_view_model,
    bundle_inspection_envelope_to_view_model,
    comparison_envelope_to_view_model,
    compatibility_envelope_to_view_model,
    local_index_envelope_to_view_model,
    representations_envelope_to_view_model,
    resolution_runs_envelope_to_view_model,
    query_plan_envelope_to_view_model,
    search_response_envelope_to_search_results_view_model,
    source_registry_envelope_to_view_model,
    subject_states_envelope_to_view_model,
)
from surfaces.web.server.api_routes import handle_api_request
from surfaces.web.server.api_serialization import SerializedHttpResponse
from surfaces.web.workbench import (
    render_acquisition_html,
    render_action_plan_html,
    render_absence_report_html,
    render_bundle_inspection_html,
    render_compatibility_html,
    render_comparison_html,
    render_decomposition_html,
    render_handoff_html,
    render_local_index_html,
    render_member_access_html,
    render_query_plan_html,
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


def render_decomposition_page(
    public_api: DecompositionPublicApi | None,
    target_ref: str,
    representation_id: str,
) -> str:
    normalized_target_ref = target_ref.strip()
    normalized_representation_id = representation_id.strip()
    if not normalized_representation_id:
        return render_decomposition_html(
            None,
            target_ref=normalized_target_ref,
            representation_id="",
            message="Provide a bounded representation_id to inspect one fetched representation.",
        )
    if public_api is None:
        return render_decomposition_html(
            None,
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
            message="This bootstrap workbench was not configured with a public decomposition boundary.",
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
        )
    return render_decomposition_html(
        decomposition_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        representation_id=normalized_representation_id,
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
        )
    return render_handoff_html(
        representation_selection_envelope_to_view_model(response.body),
        target_ref=normalized_target_ref,
        host_profile_id=normalized_host_profile_id,
        strategy_id=normalized_strategy_id,
        host_profile_presets=BOOTSTRAP_HOST_PROFILE_PRESETS,
        strategy_profiles=BOOTSTRAP_STRATEGY_PROFILES,
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
        handoff_public_api: RepresentationSelectionPublicApi | None = None,
        query_planner_public_api: QueryPlannerPublicApi | None = None,
        subject_states_public_api: SubjectStatesPublicApi | None = None,
        representations_public_api: RepresentationsPublicApi | None = None,
        actions_public_api: ResolutionActionsPublicApi | None = None,
        bundle_inspection_public_api: ResolutionBundleInspectionPublicApi | None = None,
        local_index_public_api: LocalIndexPublicApi | None = None,
        stored_exports_public_api: StoredExportsPublicApi | None = None,
        search_public_api: SearchPublicApi,
        source_registry_public_api: SourceRegistryPublicApi | None = None,
        default_target_ref: str,
        session_id: str = "session.web-workbench",
    ) -> None:
        self._resolution_public_api = resolution_public_api
        self._absence_public_api = absence_public_api
        self._comparison_public_api = comparison_public_api
        self._compatibility_public_api = compatibility_public_api
        self._acquisition_public_api = acquisition_public_api
        self._decomposition_public_api = decomposition_public_api
        self._member_access_public_api = member_access_public_api
        self._action_plan_public_api = action_plan_public_api
        self._handoff_public_api = handoff_public_api
        self._query_planner_public_api = query_planner_public_api
        self._subject_states_public_api = subject_states_public_api
        self._representations_public_api = representations_public_api
        self._actions_public_api = actions_public_api
        self._bundle_inspection_public_api = bundle_inspection_public_api
        self._local_index_public_api = local_index_public_api
        self._stored_exports_public_api = stored_exports_public_api
        self._search_public_api = search_public_api
        self._source_registry_public_api = source_registry_public_api
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
            acquisition_public_api=self._acquisition_public_api,
            decomposition_public_api=self._decomposition_public_api,
            member_access_public_api=self._member_access_public_api,
            action_plan_public_api=self._action_plan_public_api,
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
            "/decompose",
            "/fetch",
            "/member",
            "/query-plan",
            "/action-plan",
            "/handoff",
            "/index/build",
            "/index/search",
            "/index/status",
            "/representations",
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
                        "'/absence/resolve', '/absence/search', '/compare', '/compatibility', '/decompose', '/fetch', '/member', '/query-plan', '/action-plan', '/handoff', '/index/build', '/index/status', '/index/search', '/representations', '/runs', '/run', '/run/resolve', '/run/search', '/run/planned-search', '/sources', '/source', '/subject', '/inspect/bundle', '/actions/export-resolution-manifest', and "
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
                handoff_public_api=self._handoff_public_api,
                actions_public_api=self._actions_public_api,
                stored_exports_public_api=self._stored_exports_public_api,
                session_id=self._session_id,
                host_profile_id=self._resolve_optional_host_profile_id(query_string),
                strategy_id=self._resolve_optional_strategy_id(query_string),
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
                store_actions_enabled=self._stored_exports_public_api is not None,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/query-plan":
            page = render_query_plan_page(
                self._query_planner_public_api,
                self._resolve_search_query(query_string),
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/handoff":
            target_ref = self._resolve_target_ref(query_string)
            page = render_handoff_page(
                self._handoff_public_api,
                target_ref,
                self._resolve_optional_host_profile_id(query_string),
                self._resolve_optional_strategy_id(query_string),
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
        if path == "/sources":
            page = render_source_registry_page(
                self._source_registry_public_api,
                status=self._resolve_optional_query_value(query_string, "status"),
                source_family=self._resolve_optional_query_value(query_string, "family"),
                role=self._resolve_optional_query_value(query_string, "role"),
                surface=self._resolve_optional_query_value(query_string, "surface"),
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
        )
    )
    return render_source_registry_html(source_registry_envelope_to_view_model(response.body))


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

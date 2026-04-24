from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

from runtime.gateway.public_api import (
    AcquisitionFetchRequest,
    AcquisitionPublicApi,
    ActionPlanEvaluationRequest,
    ActionPlanPublicApi,
    AbsencePublicApi,
    BOOTSTRAP_HOST_PROFILE_PRESETS,
    BOOTSTRAP_STRATEGY_PROFILES,
    acquisition_envelope_to_view_model,
    build_demo_acquisition_public_api,
    build_demo_action_plan_public_api,
    build_demo_absence_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_query_planner_public_api,
    build_demo_local_index_public_api,
    build_demo_local_tasks_public_api,
    build_demo_resolution_memory_public_api,
    build_demo_representation_selection_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_resolution_runs_public_api,
    build_demo_representations_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
    build_demo_stored_exports_public_api,
    build_demo_subject_states_public_api,
    ExplainResolveMissRequest,
    ExplainSearchMissRequest,
    CompareTargetsRequest,
    ComparisonPublicApi,
    CompatibilityEvaluationRequest,
    CompatibilityPublicApi,
    DeterministicSearchRunRequest,
    PlannedSearchRunRequest,
    DecompositionInspectionRequest,
    DecompositionPublicApi,
    ExactResolutionRunRequest,
    LocalIndexBuildRequest,
    LocalIndexPublicApi,
    LocalIndexQueryRequest,
    LocalIndexStatusRequest,
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
    ResolutionMemoryPublicApi,
    LocalTaskReadRequest,
    LocalTaskRunRequest,
    LocalTasksPublicApi,
    MemberAccessPublicApi,
    MemberAccessReadRequest,
    local_index_envelope_to_view_model,
    local_tasks_envelope_to_view_model,
    resolution_memory_envelope_to_view_model,
    member_access_envelope_to_view_model,
    InspectResolutionBundleRequest,
    RepresentationSelectionEvaluationRequest,
    RepresentationCatalogRequest,
    RepresentationSelectionPublicApi,
    RepresentationsPublicApi,
    ResolutionActionRequest,
    ResolutionBundleInspectionPublicApi,
    ResolutionJobsPublicApi,
    QueryPlanRequest,
    QueryPlannerPublicApi,
    ResolutionRunReadRequest,
    ResolutionRunsPublicApi,
    ResolutionWorkspaceViewModels,
    ResolutionActionsPublicApi,
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
    action_plan_envelope_to_view_model,
    build_resolution_workspace_view_models,
    build_demo_decomposition_public_api,
    build_demo_member_access_public_api,
    bundle_inspection_envelope_to_view_model,
    comparison_envelope_to_view_model,
    compatibility_envelope_to_view_model,
    decomposition_envelope_to_view_model,
    query_plan_envelope_to_view_model,
    representations_envelope_to_view_model,
    resolution_runs_envelope_to_view_model,
    search_response_envelope_to_search_results_view_model,
    source_registry_envelope_to_view_model,
    stored_exports_envelope_to_view_model,
    subject_states_envelope_to_view_model,
)
from surfaces.native.cli.formatters import (
    format_acquisition,
    format_action_plan,
    format_absence_report,
    format_blocked_response,
    format_bundle_export_summary,
    format_bundle_inspection,
    format_compatibility,
    format_comparison,
    format_decomposition,
    format_handoff,
    format_local_index,
    format_resolution_memory,
    format_local_tasks,
    format_member_access,
    format_manifest_export,
    format_query_plan,
    format_representations,
    format_resolution_workspace,
    format_resolution_runs,
    format_search_results,
    format_source_registry,
    format_store_result,
    format_stored_artifact_bundle,
    format_stored_artifact_json,
    format_stored_exports_listing,
    format_subject_states,
)


DEFAULT_SESSION_ID = "session.native-cli"


@dataclass(frozen=True)
class CliContext:
    acquisition_public_api: AcquisitionPublicApi
    action_plan_public_api: ActionPlanPublicApi
    decomposition_public_api: DecompositionPublicApi
    member_access_public_api: MemberAccessPublicApi
    resolution_public_api: ResolutionJobsPublicApi
    actions_public_api: ResolutionActionsPublicApi
    inspection_public_api: ResolutionBundleInspectionPublicApi
    search_public_api: SearchPublicApi
    source_registry_public_api: SourceRegistryPublicApi
    absence_public_api: AbsencePublicApi
    comparison_public_api: ComparisonPublicApi
    compatibility_public_api: CompatibilityPublicApi
    handoff_public_api: RepresentationSelectionPublicApi
    subject_states_public_api: SubjectStatesPublicApi
    representations_public_api: RepresentationsPublicApi
    query_planner_public_api: QueryPlannerPublicApi
    local_index_public_api: LocalIndexPublicApi
    resolution_memory_public_api: ResolutionMemoryPublicApi | None = None
    local_tasks_public_api: LocalTasksPublicApi | None = None
    resolution_runs_public_api: ResolutionRunsPublicApi | None = None
    stored_exports_public_api: StoredExportsPublicApi | None = None
    session_id: str = DEFAULT_SESSION_ID


def main(
    argv: Sequence[str] | None = None,
    *,
    context: CliContext | None = None,
    stdout: TextIO | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    output = stdout or sys.stdout
    cli_context = context or build_cli_context(
        store_root=getattr(args, "store_root", None),
        run_store_root=getattr(args, "run_store_root", None),
        memory_store_root=getattr(args, "memory_store_root", None),
        task_store_root=getattr(args, "task_store_root", None),
    )

    try:
        if args.command == "plan":
            response = cli_context.action_plan_public_api.plan_actions(
                ActionPlanEvaluationRequest.from_parts(
                    args.target_ref,
                    args.host_profile_id,
                    args.strategy_id,
                    store_actions_enabled=cli_context.stored_exports_public_api is not None,
                ),
            )
            action_plan = action_plan_envelope_to_view_model(response.body)
            return _emit(output, args.json, action_plan, format_action_plan(action_plan))

        if args.command == "fetch":
            response = cli_context.acquisition_public_api.fetch_representation(
                AcquisitionFetchRequest.from_parts(
                    args.target_ref,
                    args.representation_id,
                )
            )
            acquisition = acquisition_envelope_to_view_model(response.body)
            emitted_payload: dict[str, Any] = dict(acquisition)
            if response.status_code == 200 and args.output is not None and response.payload is not None:
                output_path = _write_output_payload(Path(args.output), response.payload)
                emitted_payload["output_path"] = str(output_path)
                return _emit(
                    output,
                    args.json,
                    emitted_payload,
                    format_acquisition(acquisition, output_path=str(output_path)),
                )
            return _emit(output, args.json, emitted_payload, format_acquisition(acquisition))

        if args.command == "decompose":
            response = cli_context.decomposition_public_api.decompose_representation(
                DecompositionInspectionRequest.from_parts(
                    args.target_ref,
                    args.representation_id,
                )
            )
            decomposition = decomposition_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                decomposition,
                format_decomposition(decomposition),
            )

        if args.command == "member":
            response = cli_context.member_access_public_api.read_member(
                MemberAccessReadRequest.from_parts(
                    args.target_ref,
                    args.representation_id,
                    args.member_path,
                )
            )
            member_access = member_access_envelope_to_view_model(response.body)
            emitted_payload: dict[str, Any] = dict(member_access)
            if response.status_code == 200 and args.output is not None and response.payload is not None:
                output_path = _write_output_payload(Path(args.output), response.payload)
                emitted_payload["output_path"] = str(output_path)
                return _emit(
                    output,
                    args.json,
                    emitted_payload,
                    format_member_access(member_access, output_path=str(output_path)),
                )
            return _emit(
                output,
                args.json,
                emitted_payload,
                format_member_access(member_access),
            )

        if args.command == "resolve":
            workspace = _resolve_workspace(args.target_ref, cli_context)
            payload: dict[str, Any] = {"workbench_session": workspace.workbench_session}
            if workspace.resolution_actions is not None:
                payload["resolution_actions"] = workspace.resolution_actions
            return _emit(
                output,
                args.json,
                payload,
                format_resolution_workspace(
                    workspace.workbench_session,
                    resolution_actions=workspace.resolution_actions,
                ),
            )

        if args.command == "search":
            response = cli_context.search_public_api.search_records(
                SearchCatalogRequest.from_parts(args.query),
            )
            search_results = search_response_envelope_to_search_results_view_model(response.body)
            return _emit(
                output,
                args.json,
                search_results,
                format_search_results(search_results),
            )

        if args.command == "query-plan":
            response = cli_context.query_planner_public_api.plan_query(
                QueryPlanRequest.from_parts(args.query),
            )
            query_plan = query_plan_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                query_plan,
                format_query_plan(query_plan),
            )

        if args.command == "index-build":
            response = cli_context.local_index_public_api.build_index(
                LocalIndexBuildRequest.from_parts(args.index_path),
            )
            local_index = local_index_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                local_index,
                format_local_index(local_index),
            )

        if args.command == "index-status":
            response = cli_context.local_index_public_api.get_index_status(
                LocalIndexStatusRequest.from_parts(args.index_path),
            )
            local_index = local_index_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                local_index,
                format_local_index(local_index),
            )

        if args.command == "index-query":
            response = cli_context.local_index_public_api.query_index(
                LocalIndexQueryRequest.from_parts(args.index_path, args.query),
            )
            local_index = local_index_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                local_index,
                format_local_index(local_index),
            )

        if args.command == "task-run":
            tasks_public_api = _require_tasks_public_api(cli_context)
            requested_inputs: dict[str, Any] = {}
            if args.index_path is not None:
                requested_inputs["index_path"] = args.index_path
            if args.query is not None:
                requested_inputs["query"] = args.query
            response = tasks_public_api.run_task(
                LocalTaskRunRequest.from_parts(args.task_kind, requested_inputs),
            )
            local_tasks = local_tasks_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                local_tasks,
                format_local_tasks(local_tasks),
            )

        if args.command == "task-status":
            tasks_public_api = _require_tasks_public_api(cli_context)
            response = tasks_public_api.get_task(
                LocalTaskReadRequest.from_parts(args.task_id),
            )
            local_tasks = local_tasks_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                local_tasks,
                format_local_tasks(local_tasks),
            )

        if args.command == "tasks":
            tasks_public_api = _require_tasks_public_api(cli_context)
            response = tasks_public_api.list_tasks()
            local_tasks = local_tasks_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                local_tasks,
                format_local_tasks(local_tasks),
            )

        if args.command == "memory-create":
            memory_public_api = _require_resolution_memory_public_api(cli_context)
            response = memory_public_api.create_memory_from_run(
                ResolutionMemoryCreateRequest.from_parts(args.run_id),
            )
            resolution_memory = resolution_memory_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_memory,
                format_resolution_memory(resolution_memory),
            )

        if args.command == "memory":
            memory_public_api = _require_resolution_memory_public_api(cli_context)
            response = memory_public_api.get_memory(
                ResolutionMemoryReadRequest.from_parts(args.memory_id),
            )
            resolution_memory = resolution_memory_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_memory,
                format_resolution_memory(resolution_memory),
            )

        if args.command == "memories":
            memory_public_api = _require_resolution_memory_public_api(cli_context)
            response = memory_public_api.list_memories(
                ResolutionMemoryCatalogRequest.from_parts(
                    memory_kind=args.kind,
                    source_run_id=args.run_id,
                    task_kind=args.task_kind,
                    checked_source_id=args.source_id,
                )
            )
            resolution_memory = resolution_memory_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_memory,
                format_resolution_memory(resolution_memory),
            )

        if args.command == "run-resolve":
            runs_public_api = _require_runs_public_api(cli_context)
            response = runs_public_api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(args.target_ref),
            )
            resolution_runs = resolution_runs_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_runs,
                format_resolution_runs(resolution_runs),
            )

        if args.command == "run-search":
            runs_public_api = _require_runs_public_api(cli_context)
            response = runs_public_api.start_deterministic_search_run(
                DeterministicSearchRunRequest.from_parts(args.query),
            )
            resolution_runs = resolution_runs_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_runs,
                format_resolution_runs(resolution_runs),
            )

        if args.command == "run-planned-search":
            runs_public_api = _require_runs_public_api(cli_context)
            response = runs_public_api.start_planned_search_run(
                PlannedSearchRunRequest.from_parts(args.query),
            )
            resolution_runs = resolution_runs_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_runs,
                format_resolution_runs(resolution_runs),
            )

        if args.command == "run-status":
            runs_public_api = _require_runs_public_api(cli_context)
            response = runs_public_api.get_run(
                ResolutionRunReadRequest.from_parts(args.run_id),
            )
            resolution_runs = resolution_runs_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_runs,
                format_resolution_runs(resolution_runs),
            )

        if args.command == "runs":
            runs_public_api = _require_runs_public_api(cli_context)
            response = runs_public_api.list_runs()
            resolution_runs = resolution_runs_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                resolution_runs,
                format_resolution_runs(resolution_runs),
            )

        if args.command == "sources":
            response = cli_context.source_registry_public_api.list_sources(
                SourceCatalogRequest.from_parts(
                    status=args.status,
                    source_family=args.family,
                    role=args.role,
                    surface=args.surface,
                )
            )
            source_registry = source_registry_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                source_registry,
                format_source_registry(source_registry),
            )

        if args.command == "source":
            response = cli_context.source_registry_public_api.get_source(
                SourceReadRequest.from_parts(args.source_id),
            )
            source_registry = source_registry_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                source_registry,
                format_source_registry(source_registry),
            )

        if args.command == "explain-resolve-miss":
            response = cli_context.absence_public_api.explain_resolution_miss(
                ExplainResolveMissRequest.from_parts(args.target_ref),
            )
            return _emit(
                output,
                args.json,
                response.body,
                format_absence_report(response.body),
            )

        if args.command == "explain-search-miss":
            response = cli_context.absence_public_api.explain_search_miss(
                ExplainSearchMissRequest.from_parts(args.query),
            )
            return _emit(
                output,
                args.json,
                response.body,
                format_absence_report(response.body),
            )

        if args.command == "compare":
            response = cli_context.comparison_public_api.compare_targets(
                CompareTargetsRequest.from_parts(args.left_target_ref, args.right_target_ref),
            )
            comparison = comparison_envelope_to_view_model(response.body)
            return _emit(output, args.json, comparison, format_comparison(comparison))

        if args.command == "compatibility":
            response = cli_context.compatibility_public_api.evaluate_compatibility(
                CompatibilityEvaluationRequest.from_parts(args.target_ref, args.host_profile_id),
            )
            compatibility = compatibility_envelope_to_view_model(response.body)
            return _emit(output, args.json, compatibility, format_compatibility(compatibility))

        if args.command == "handoff":
            response = cli_context.handoff_public_api.select_representation(
                RepresentationSelectionEvaluationRequest.from_parts(
                    args.target_ref,
                    args.host_profile_id,
                    args.strategy_id,
                )
            )
            return _emit(output, args.json, response.body, format_handoff(response.body))

        if args.command == "states":
            response = cli_context.subject_states_public_api.list_subject_states(
                SubjectStatesCatalogRequest.from_parts(args.subject_key),
            )
            subject_states = subject_states_envelope_to_view_model(response.body)
            return _emit(output, args.json, subject_states, format_subject_states(subject_states))

        if args.command == "representations":
            response = cli_context.representations_public_api.list_representations(
                RepresentationCatalogRequest.from_parts(args.target_ref),
            )
            representations = representations_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                representations,
                format_representations(representations),
            )

        if args.command == "export-manifest":
            response = cli_context.actions_public_api.export_resolution_manifest(
                ResolutionActionRequest.from_parts(args.target_ref),
            )
            if response.status_code == 200:
                return _emit(output, args.json, response.body, format_manifest_export(response.body))
            return _emit(
                output,
                args.json,
                response.body,
                format_blocked_response(response.body, title="Manifest export"),
            )

        if args.command == "export-bundle":
            return _handle_export_bundle(args.target_ref, cli_context, output, as_json=args.json)

        if args.command == "inspect-bundle":
            response = cli_context.inspection_public_api.inspect_bundle(
                InspectResolutionBundleRequest.from_bundle_path(args.bundle_path),
            )
            bundle_inspection = bundle_inspection_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                bundle_inspection,
                format_bundle_inspection(bundle_inspection),
            )

        if args.command == "store-manifest":
            return _handle_store_target(
                args.target_ref,
                cli_context,
                output,
                as_json=args.json,
                artifact_kind="resolution_manifest",
            )

        if args.command == "store-bundle":
            return _handle_store_target(
                args.target_ref,
                cli_context,
                output,
                as_json=args.json,
                artifact_kind="resolution_bundle",
            )

        if args.command == "list-stored":
            stored_public_api = _require_store_public_api(cli_context)
            response = stored_public_api.list_stored_exports(
                StoredExportsTargetRequest.from_parts(args.target_ref),
            )
            stored_exports = stored_exports_envelope_to_view_model(response.body)
            return _emit(
                output,
                args.json,
                stored_exports,
                format_stored_exports_listing(stored_exports),
            )

        if args.command == "read-stored":
            return _handle_read_stored(
                args.artifact_id,
                cli_context,
                output,
                as_json=args.json,
            )
    except ValueError as error:
        payload = {
            "status": "blocked",
            "code": "invalid_request",
            "message": str(error),
        }
        return _emit(output, getattr(args, "json", False), payload, format_blocked_response(payload))

    raise AssertionError(f"Unhandled command '{args.command}'.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local stdlib-only Eureka CLI surface for the bootstrap workbench.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    json_parent = argparse.ArgumentParser(add_help=False)
    json_parent.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON for inspection or scripting.",
    )

    resolve_parser = subparsers.add_parser(
        "resolve",
        parents=[json_parent],
        help="Resolve an exact target reference through the public boundary.",
    )
    resolve_parser.add_argument("target_ref")

    plan_parser = subparsers.add_parser(
        "plan",
        parents=[json_parent],
        help="Build a bounded action plan for one resolved target through the public boundary.",
    )
    plan_parser.add_argument("target_ref")
    plan_parser.add_argument(
        "--host",
        dest="host_profile_id",
        choices=tuple(
            str(profile["host_profile_id"]) for profile in BOOTSTRAP_HOST_PROFILE_PRESETS
        ),
        help="Optional bootstrap host profile preset used to shape host-aware recommendations.",
    )
    plan_parser.add_argument(
        "--strategy",
        dest="strategy_id",
        choices=tuple(
            str(profile["strategy_id"]) for profile in BOOTSTRAP_STRATEGY_PROFILES
        ),
        help="Optional bootstrap strategy profile used to vary bounded recommendation emphasis.",
    )
    plan_parser.add_argument(
        "--store-root",
        help="Optional local deterministic store root used to mark store actions as available.",
    )

    search_parser = subparsers.add_parser(
        "search",
        parents=[json_parent],
        help="Run deterministic search through the public boundary.",
    )
    search_parser.add_argument("query")

    query_plan_parser = subparsers.add_parser(
        "query-plan",
        parents=[json_parent],
        help="Compile one raw query into a bounded deterministic resolution task through the public boundary.",
    )
    query_plan_parser.add_argument("query")

    index_build_parser = subparsers.add_parser(
        "index-build",
        parents=[json_parent],
        help="Build or replace the bootstrap local SQLite index through the public boundary.",
    )
    index_build_parser.add_argument(
        "--index-path",
        required=True,
        help="Bootstrap local SQLite index path.",
    )

    index_status_parser = subparsers.add_parser(
        "index-status",
        parents=[json_parent],
        help="Read bootstrap local index metadata through the public boundary.",
    )
    index_status_parser.add_argument(
        "--index-path",
        required=True,
        help="Bootstrap local SQLite index path.",
    )

    index_query_parser = subparsers.add_parser(
        "index-query",
        parents=[json_parent],
        help="Run one bounded text query against the bootstrap local SQLite index through the public boundary.",
    )
    index_query_parser.add_argument("query")
    index_query_parser.add_argument(
        "--index-path",
        required=True,
        help="Bootstrap local SQLite index path.",
    )

    task_run_parser = subparsers.add_parser(
        "task-run",
        parents=[json_parent],
        help="Create, execute, and persist one synchronous bootstrap local task through the public boundary.",
    )
    task_run_parser.add_argument(
        "task_kind",
        help="Supported task kind, such as validate-source-registry, build-local-index, query-local-index, or validate-archive-resolution-evals.",
    )
    task_run_parser.add_argument(
        "--task-store-root",
        required=True,
        help="Bootstrap local root for persisted local-task JSON records.",
    )
    task_run_parser.add_argument(
        "--index-path",
        help="Bootstrap local SQLite index path for build-local-index or query-local-index.",
    )
    task_run_parser.add_argument(
        "--query",
        help="Bounded text query for query-local-index.",
    )

    task_status_parser = subparsers.add_parser(
        "task-status",
        parents=[json_parent],
        help="Read one persisted synchronous bootstrap local task by task_id through the public boundary.",
    )
    task_status_parser.add_argument("task_id")
    task_status_parser.add_argument(
        "--task-store-root",
        required=True,
        help="Bootstrap local root for persisted local-task JSON records.",
    )

    tasks_parser = subparsers.add_parser(
        "tasks",
        parents=[json_parent],
        help="List persisted synchronous bootstrap local tasks through the public boundary.",
    )
    tasks_parser.add_argument(
        "--task-store-root",
        required=True,
        help="Bootstrap local root for persisted local-task JSON records.",
    )

    run_resolve_parser = subparsers.add_parser(
        "run-resolve",
        parents=[json_parent],
        help="Start and persist a synchronous exact-resolution run through the public boundary.",
    )
    run_resolve_parser.add_argument("target_ref")
    run_resolve_parser.add_argument(
        "--run-store-root",
        required=True,
        help="Bootstrap local root for persisted resolution-run JSON records.",
    )

    run_search_parser = subparsers.add_parser(
        "run-search",
        parents=[json_parent],
        help="Start and persist a synchronous deterministic-search run through the public boundary.",
    )
    run_search_parser.add_argument("query")
    run_search_parser.add_argument(
        "--run-store-root",
        required=True,
        help="Bootstrap local root for persisted resolution-run JSON records.",
    )

    run_planned_search_parser = subparsers.add_parser(
        "run-planned-search",
        parents=[json_parent],
        help="Plan one raw query deterministically, then persist a synchronous planned-search resolution run through the public boundary.",
    )
    run_planned_search_parser.add_argument("query")
    run_planned_search_parser.add_argument(
        "--run-store-root",
        required=True,
        help="Bootstrap local root for persisted resolution-run JSON records.",
    )

    run_status_parser = subparsers.add_parser(
        "run-status",
        parents=[json_parent],
        help="Read one persisted synchronous resolution run by run_id through the public boundary.",
    )
    run_status_parser.add_argument("run_id")
    run_status_parser.add_argument(
        "--run-store-root",
        required=True,
        help="Bootstrap local root for persisted resolution-run JSON records.",
    )

    runs_parser = subparsers.add_parser(
        "runs",
        parents=[json_parent],
        help="List persisted synchronous resolution runs through the public boundary.",
    )
    runs_parser.add_argument(
        "--run-store-root",
        required=True,
        help="Bootstrap local root for persisted resolution-run JSON records.",
    )

    memory_create_parser = subparsers.add_parser(
        "memory-create",
        parents=[json_parent],
        help="Create and persist one explicit local resolution-memory record from one existing run through the public boundary.",
    )
    memory_create_parser.add_argument("--run-store-root", required=True)
    memory_create_parser.add_argument("--memory-store-root", required=True)
    memory_create_parser.add_argument("--run-id", required=True)

    memory_parser = subparsers.add_parser(
        "memory",
        parents=[json_parent],
        help="Read one persisted local resolution-memory record by memory_id through the public boundary.",
    )
    memory_parser.add_argument("memory_id")
    memory_parser.add_argument("--memory-store-root", required=True)

    memories_parser = subparsers.add_parser(
        "memories",
        parents=[json_parent],
        help="List persisted local resolution-memory records through the public boundary.",
    )
    memories_parser.add_argument("--memory-store-root", required=True)
    memories_parser.add_argument("--kind")
    memories_parser.add_argument("--run-id")
    memories_parser.add_argument("--task-kind")
    memories_parser.add_argument("--source-id")

    sources_parser = subparsers.add_parser(
        "sources",
        parents=[json_parent],
        help="List governed source-registry records through the public boundary.",
    )
    sources_parser.add_argument("--status")
    sources_parser.add_argument("--family", dest="family")
    sources_parser.add_argument("--role")
    sources_parser.add_argument("--surface")

    source_parser = subparsers.add_parser(
        "source",
        parents=[json_parent],
        help="Read one governed source-registry record by source_id through the public boundary.",
    )
    source_parser.add_argument("source_id")

    explain_resolve_parser = subparsers.add_parser(
        "explain-resolve-miss",
        parents=[json_parent],
        help="Explain an exact-resolution miss through the public absence boundary.",
    )
    explain_resolve_parser.add_argument("target_ref")

    explain_search_parser = subparsers.add_parser(
        "explain-search-miss",
        parents=[json_parent],
        help="Explain a deterministic search miss through the public absence boundary.",
    )
    explain_search_parser.add_argument("query")

    compare_parser = subparsers.add_parser(
        "compare",
        parents=[json_parent],
        help="Compare two bounded targets side by side through the public boundary.",
    )
    compare_parser.add_argument("left_target_ref")
    compare_parser.add_argument("right_target_ref")

    compatibility_parser = subparsers.add_parser(
        "compatibility",
        parents=[json_parent],
        help="Evaluate bounded compatibility for one resolved target against one bootstrap host preset.",
    )
    compatibility_parser.add_argument("target_ref")
    compatibility_parser.add_argument(
        "--host",
        dest="host_profile_id",
        required=True,
        choices=tuple(
            str(profile["host_profile_id"]) for profile in BOOTSTRAP_HOST_PROFILE_PRESETS
        ),
        help="Bootstrap host profile preset to evaluate against.",
    )

    states_parser = subparsers.add_parser(
        "states",
        parents=[json_parent],
        help="List bounded ordered states for one bootstrap subject key through the public boundary.",
    )
    states_parser.add_argument("subject_key")

    representations_parser = subparsers.add_parser(
        "representations",
        parents=[json_parent],
        help="List bounded known representations/access paths for one resolved target through the public boundary.",
    )
    representations_parser.add_argument("target_ref")

    handoff_parser = subparsers.add_parser(
        "handoff",
        parents=[json_parent],
        help="Select a bounded preferred representation/access path for one resolved target through the public boundary.",
    )
    handoff_parser.add_argument("target_ref")
    handoff_parser.add_argument(
        "--host",
        dest="host_profile_id",
        choices=tuple(
            str(profile["host_profile_id"]) for profile in BOOTSTRAP_HOST_PROFILE_PRESETS
        ),
        help="Optional bootstrap host profile preset used to evaluate suitability.",
    )
    handoff_parser.add_argument(
        "--strategy",
        dest="strategy_id",
        choices=tuple(
            str(profile["strategy_id"]) for profile in BOOTSTRAP_STRATEGY_PROFILES
        ),
        help="Optional bootstrap strategy profile used to vary bounded handoff emphasis.",
    )

    fetch_parser = subparsers.add_parser(
        "fetch",
        parents=[json_parent],
        help="Fetch a bounded local payload fixture for one selected representation through the public boundary.",
    )
    fetch_parser.add_argument("target_ref")
    fetch_parser.add_argument(
        "--representation",
        dest="representation_id",
        required=True,
        help="Explicit bounded representation_id to fetch.",
    )
    fetch_parser.add_argument(
        "--output",
        help="Optional local path to write fetched bytes to instead of only reporting metadata.",
    )

    decompose_parser = subparsers.add_parser(
        "decompose",
        parents=[json_parent],
        help="Inspect a bounded fetched representation into a compact member list through the public boundary.",
    )
    decompose_parser.add_argument("target_ref")
    decompose_parser.add_argument(
        "--representation",
        dest="representation_id",
        required=True,
        help="Explicit bounded representation_id to inspect.",
    )

    member_parser = subparsers.add_parser(
        "member",
        parents=[json_parent],
        help="Read one bounded member from one decomposed representation through the public boundary.",
    )
    member_parser.add_argument("target_ref")
    member_parser.add_argument(
        "--representation",
        dest="representation_id",
        required=True,
        help="Explicit bounded representation_id containing the member.",
    )
    member_parser.add_argument(
        "--member",
        dest="member_path",
        required=True,
        help="Explicit bounded member_path to read.",
    )
    member_parser.add_argument(
        "--output",
        help="Optional local path to write member bytes to instead of only reporting metadata or preview text.",
    )

    export_manifest_parser = subparsers.add_parser(
        "export-manifest",
        parents=[json_parent],
        help="Export a deterministic manifest for a resolved target.",
    )
    export_manifest_parser.add_argument("target_ref")

    export_bundle_parser = subparsers.add_parser(
        "export-bundle",
        parents=[json_parent],
        help="Export a deterministic bundle for a resolved target and summarize it locally.",
    )
    export_bundle_parser.add_argument("target_ref")

    inspect_bundle_parser = subparsers.add_parser(
        "inspect-bundle",
        parents=[json_parent],
        help="Inspect a local bundle path through the public inspection boundary.",
    )
    inspect_bundle_parser.add_argument("bundle_path")

    for command_name, help_text in (
        ("store-manifest", "Store a deterministic manifest in the local export store."),
        ("store-bundle", "Store a deterministic bundle in the local export store."),
        ("list-stored", "List locally stored exports for a target."),
    ):
        command_parser = subparsers.add_parser(
            command_name,
            parents=[json_parent],
            help=help_text,
        )
        command_parser.add_argument("target_ref")
        command_parser.add_argument(
            "--store-root",
            required=True,
            help="Local root for the deterministic bootstrap export store.",
        )

    read_stored_parser = subparsers.add_parser(
        "read-stored",
        parents=[json_parent],
        help="Read a locally stored artifact by artifact_id.",
    )
    read_stored_parser.add_argument("artifact_id")
    read_stored_parser.add_argument(
        "--store-root",
        required=True,
        help="Local root for the deterministic bootstrap export store.",
    )

    return parser


def build_cli_context(
    *,
    store_root: str | None,
    run_store_root: str | None,
    memory_store_root: str | None,
    task_store_root: str | None,
) -> CliContext:
    return CliContext(
        acquisition_public_api=build_demo_acquisition_public_api(),
        action_plan_public_api=build_demo_action_plan_public_api(),
        decomposition_public_api=build_demo_decomposition_public_api(),
        member_access_public_api=build_demo_member_access_public_api(),
        resolution_public_api=build_demo_resolution_jobs_public_api(),
        actions_public_api=build_demo_resolution_actions_public_api(),
        inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
        search_public_api=build_demo_search_public_api(),
        query_planner_public_api=build_demo_query_planner_public_api(),
        local_index_public_api=build_demo_local_index_public_api(),
        resolution_memory_public_api=(
            build_demo_resolution_memory_public_api(
                memory_store_root,
                run_store_root=run_store_root,
            )
            if memory_store_root is not None
            else None
        ),
        local_tasks_public_api=(
            build_demo_local_tasks_public_api(task_store_root)
            if task_store_root is not None
            else None
        ),
        source_registry_public_api=build_demo_source_registry_public_api(),
        resolution_runs_public_api=(
            build_demo_resolution_runs_public_api(run_store_root)
            if run_store_root is not None
            else None
        ),
        absence_public_api=build_demo_absence_public_api(),
        comparison_public_api=build_demo_comparison_public_api(),
        compatibility_public_api=build_demo_compatibility_public_api(),
        handoff_public_api=build_demo_representation_selection_public_api(),
        subject_states_public_api=build_demo_subject_states_public_api(),
        representations_public_api=build_demo_representations_public_api(),
        stored_exports_public_api=(
            build_demo_stored_exports_public_api(store_root) if store_root is not None else None
        ),
    )


def _resolve_workspace(target_ref: str, context: CliContext) -> ResolutionWorkspaceViewModels:
    return build_resolution_workspace_view_models(
        context.resolution_public_api,
        target_ref,
        actions_public_api=context.actions_public_api,
        session_id=context.session_id,
    )


def _handle_export_bundle(
    target_ref: str,
    context: CliContext,
    output: TextIO,
    *,
    as_json: bool,
) -> int:
    response = context.actions_public_api.export_resolution_bundle(
        ResolutionActionRequest.from_parts(target_ref),
    )
    if response.status_code != 200:
        blocked = response.json_body()
        return _emit(output, as_json, blocked, format_blocked_response(blocked, title="Bundle export"))

    source_name = response.filename or "resolution_bundle.zip"
    inspection_response = context.inspection_public_api.inspect_bundle(
        InspectResolutionBundleRequest.from_bundle_bytes(
            response.payload,
            source_name=source_name,
        ),
    )
    bundle_inspection = bundle_inspection_envelope_to_view_model(inspection_response.body)
    payload: dict[str, Any] = {
        "status": "exported",
        "target_ref": target_ref,
        "filename": source_name,
        "content_type": response.content_type,
        "byte_length": len(response.payload),
        "bundle_inspection": bundle_inspection,
    }
    resolved_resource_id = bundle_inspection.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        payload["resolved_resource_id"] = resolved_resource_id
    return _emit(output, as_json, payload, format_bundle_export_summary(payload))


def _handle_store_target(
    target_ref: str,
    context: CliContext,
    output: TextIO,
    *,
    as_json: bool,
    artifact_kind: str,
) -> int:
    stored_public_api = _require_store_public_api(context)
    request = StoredExportsTargetRequest.from_parts(target_ref)
    if artifact_kind == "resolution_manifest":
        response = stored_public_api.store_resolution_manifest(request)
    else:
        response = stored_public_api.store_resolution_bundle(request)

    if response.status_code == 200:
        return _emit(output, as_json, response.body, format_store_result(response.body))
    return _emit(
        output,
        as_json,
        response.body,
        format_blocked_response(response.body, title="Store result"),
    )


def _handle_read_stored(
    artifact_id: str,
    context: CliContext,
    output: TextIO,
    *,
    as_json: bool,
) -> int:
    stored_public_api = _require_store_public_api(context)
    metadata_response = stored_public_api.get_stored_artifact_metadata(
        StoredArtifactRequest.from_parts(artifact_id),
    )
    if metadata_response.status_code != 200:
        return _emit(
            output,
            as_json,
            metadata_response.body,
            format_blocked_response(metadata_response.body, title="Stored artifact"),
        )

    artifact = metadata_response.body["artifact"]
    content_response = stored_public_api.get_stored_artifact_content(
        StoredArtifactRequest.from_parts(artifact_id),
    )
    if content_response.status_code != 200:
        blocked = content_response.json_body()
        return _emit(
            output,
            as_json,
            blocked,
            format_blocked_response(blocked, title="Stored artifact"),
        )

    if _is_json_content_type(str(artifact.get("content_type", ""))):
        content = json.loads(content_response.payload.decode("utf-8"))
        payload = {
            "artifact": artifact,
            "content": content,
        }
        return _emit(output, as_json, payload, format_stored_artifact_json(artifact, content))

    bundle_inspection = bundle_inspection_envelope_to_view_model(
        context.inspection_public_api.inspect_bundle(
            InspectResolutionBundleRequest.from_bundle_bytes(
                content_response.payload,
                source_name=str(artifact.get("filename") or f"{artifact_id}.zip"),
            ),
        ).body
    )
    payload = {
        "artifact": artifact,
        "bundle_inspection": bundle_inspection,
    }
    return _emit(output, as_json, payload, format_stored_artifact_bundle(artifact, bundle_inspection))


def _require_store_public_api(context: CliContext) -> StoredExportsPublicApi:
    if context.stored_exports_public_api is None:
        raise ValueError("Provide --store-root to enable bootstrap stored-export operations.")
    return context.stored_exports_public_api


def _require_runs_public_api(context: CliContext) -> ResolutionRunsPublicApi:
    if context.resolution_runs_public_api is None:
        raise ValueError("Provide --run-store-root to enable bootstrap resolution-run operations.")
    return context.resolution_runs_public_api


def _require_tasks_public_api(context: CliContext) -> LocalTasksPublicApi:
    if context.local_tasks_public_api is None:
        raise ValueError("Provide --task-store-root to enable bootstrap local-task operations.")
    return context.local_tasks_public_api


def _require_resolution_memory_public_api(context: CliContext) -> ResolutionMemoryPublicApi:
    if context.resolution_memory_public_api is None:
        raise ValueError(
            "Provide --memory-store-root to enable bootstrap resolution-memory operations."
        )
    return context.resolution_memory_public_api


def _write_output_payload(output_path: Path, payload: bytes) -> Path:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(payload)
    except OSError as error:
        raise ValueError(f"output path '{output_path}' could not be written: {error}.") from error
    return output_path


def _emit(
    output: TextIO,
    as_json: bool,
    payload: Mapping[str, Any],
    text: str,
) -> int:
    if as_json:
        output.write(json.dumps(dict(payload), indent=2, sort_keys=True))
        output.write("\n")
        return 0
    output.write(text)
    return 0


def _is_json_content_type(content_type: str) -> bool:
    return content_type.startswith("application/json")


if __name__ == "__main__":
    raise SystemExit(main())

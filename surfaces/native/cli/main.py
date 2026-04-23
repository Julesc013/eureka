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
    build_demo_representation_selection_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_representations_public_api,
    build_demo_search_public_api,
    build_demo_stored_exports_public_api,
    build_demo_subject_states_public_api,
    ExplainResolveMissRequest,
    ExplainSearchMissRequest,
    CompareTargetsRequest,
    ComparisonPublicApi,
    CompatibilityEvaluationRequest,
    CompatibilityPublicApi,
    InspectResolutionBundleRequest,
    RepresentationSelectionEvaluationRequest,
    RepresentationCatalogRequest,
    RepresentationSelectionPublicApi,
    RepresentationsPublicApi,
    ResolutionActionRequest,
    ResolutionBundleInspectionPublicApi,
    ResolutionJobsPublicApi,
    ResolutionWorkspaceViewModels,
    ResolutionActionsPublicApi,
    SearchCatalogRequest,
    SearchPublicApi,
    SubjectStatesCatalogRequest,
    SubjectStatesPublicApi,
    StoredArtifactRequest,
    StoredExportsPublicApi,
    StoredExportsTargetRequest,
    action_plan_envelope_to_view_model,
    build_resolution_workspace_view_models,
    bundle_inspection_envelope_to_view_model,
    comparison_envelope_to_view_model,
    compatibility_envelope_to_view_model,
    representations_envelope_to_view_model,
    search_response_envelope_to_search_results_view_model,
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
    format_handoff,
    format_manifest_export,
    format_representations,
    format_resolution_workspace,
    format_search_results,
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
    resolution_public_api: ResolutionJobsPublicApi
    actions_public_api: ResolutionActionsPublicApi
    inspection_public_api: ResolutionBundleInspectionPublicApi
    search_public_api: SearchPublicApi
    absence_public_api: AbsencePublicApi
    comparison_public_api: ComparisonPublicApi
    compatibility_public_api: CompatibilityPublicApi
    handoff_public_api: RepresentationSelectionPublicApi
    subject_states_public_api: SubjectStatesPublicApi
    representations_public_api: RepresentationsPublicApi
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
    cli_context = context or build_cli_context(store_root=getattr(args, "store_root", None))

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


def build_cli_context(*, store_root: str | None) -> CliContext:
    return CliContext(
        acquisition_public_api=build_demo_acquisition_public_api(),
        action_plan_public_api=build_demo_action_plan_public_api(),
        resolution_public_api=build_demo_resolution_jobs_public_api(),
        actions_public_api=build_demo_resolution_actions_public_api(),
        inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
        search_public_api=build_demo_search_public_api(),
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

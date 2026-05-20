#!/usr/bin/env python3
"""Validate WORKBENCH-FOUNDATION-00 governance artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "WORKBENCH-FOUNDATION-00"

REQUIRED_ROUTES = {
    "search", "hunt", "hunt_detail", "need", "need_detail", "workunit", "workunit_detail",
    "source", "source_detail", "source_cache", "evidence", "evidence_detail", "candidate",
    "candidate_detail", "review", "promotion", "index", "ia", "syn", "domain", "scout",
    "extraction", "snapshots", "relay", "ops", "audit",
}
REQUIRED_PROFILES = {
    "operator_workbench", "local_user_read_only", "public_web", "public_api", "cli", "tui",
    "relay_client", "snapshot_client", "native_desktop_read_only", "mobile_read_only",
    "future_marketplace_admin",
}
REQUIRED_PERMISSIONS = {
    "view_reviewed_results", "view_candidates", "view_evidence_summary", "view_full_evidence",
    "view_source_cache", "run_search", "start_hunt", "pause_resume_hunt", "steer_hunt",
    "create_workunit", "run_workunit", "run_source_probe", "inspect_source_cache",
    "create_evidence_candidate", "review_candidate", "promote_preview", "rebuild_reviewed_index",
    "export_packet", "manage_domain_pack", "view_scout_trails", "run_extraction",
    "call_model_provider", "deploy_public_site", "mutate_master_index",
}
REQUIRED_VIEWS = {
    "SearchView", "HuntView", "SearchNeedView", "WorkUnitView", "SourceView", "SourceCacheView",
    "EvidenceView", "CandidateView", "ReviewQueueView", "PromotionPreviewView", "ReviewedIndexView",
    "AbsenceView", "IAConnectorView", "SynFoundryView", "DomainPackView", "ScoutTrailView",
    "ExtractionLabView", "SnapshotView", "RelayView", "OpsStatusView", "AuditView",
}
REQUIRED_LOCATIONS = {
    "contracts/search_interaction/", "contracts/workbench/", "contracts/view_models/",
    "contracts/projections/", "contracts/domain/", "contracts/scout/", "contracts/snapshots/",
    "contracts/relay/",
}
REQUIRED_JSON = {
    "control/inventory/workbench_foundation_input_state.json": "workbench_foundation_input_state.v0",
    "control/inventory/workbench_surface_doctrine.json": "workbench_surface_doctrine.v0",
    "control/inventory/workbench_route_matrix.json": "workbench_route_matrix.v0",
    "control/inventory/workbench_projection_matrix.json": "workbench_projection_matrix.v0",
    "control/inventory/workbench_permission_matrix.json": "workbench_permission_matrix.v0",
    "control/inventory/workbench_view_model_inventory.json": "workbench_view_model_inventory.v0",
    "control/inventory/workbench_packet_location_matrix.json": "workbench_packet_location_matrix.v0",
    "control/inventory/workbench_future_module_matrix.json": "workbench_future_module_matrix.v0",
    "control/inventory/workbench_public_projection_boundary.json": "workbench_public_projection_boundary.v0",
    "control/inventory/workbench_native_projection_boundary.json": "workbench_native_projection_boundary.v0",
    "control/inventory/workbench_foundation_validator_matrix.json": "workbench_foundation_validator_matrix.v0",
    "control/inventory/workbench_foundation_result.json": "workbench_foundation_result.v0",
    "control/inventory/workbench_foundation_next_task_decision.json": "workbench_foundation_next_task_decision.v0",
    "control/policies/workbench_projection_policy.json": "workbench_projection_policy.v0",
    "control/policies/workbench_permission_policy.json": "workbench_permission_policy.v0",
    "control/policies/workbench_non_claim_policy.json": "workbench_non_claim_policy.v0",
    "control/policies/workbench_future_surface_policy.json": "workbench_future_surface_policy.v0",
    "control/audits/workbench-foundation-00-v0/workbench_foundation_report.json": "workbench_foundation_report.v0",
}
REQUIRED_FILES = [
    "docs/architecture/WORKBENCH_FOUNDATION.md",
    "docs/architecture/WORKBENCH_AS_INTERNAL_SUPERSET.md",
    "docs/architecture/PROJECTION_MODEL.md",
    "docs/architecture/VIEW_MODEL_AND_PACKET_BOUNDARY.md",
    "docs/operations/WORKBENCH_FOUNDATION_PLAN.md",
    "docs/operations/POST_WORKBENCH_FOUNDATION_PLAN.md",
    "contracts/workbench/README.md",
    "contracts/workbench/workbench_route.v0.json",
    "contracts/workbench/workbench_module.v0.json",
    "contracts/workbench/workbench_permission.v0.json",
    "contracts/projections/README.md",
    "contracts/projections/projection_profile.v0.json",
    "contracts/view_models/README.md",
    "contracts/view_models/view_model_packet.v0.json",
    "contracts/search_interaction/README.md",
    "contracts/domain/README.md",
    "contracts/scout/README.md",
    "contracts/snapshots/README.md",
    "contracts/relay/README.md",
    "control/audits/workbench-foundation-00-v0/README.md",
    "control/audits/workbench-foundation-00-v0/surface_doctrine.md",
    "control/audits/workbench-foundation-00-v0/route_matrix.md",
    "control/audits/workbench-foundation-00-v0/projection_matrix.md",
    "control/audits/workbench-foundation-00-v0/permission_matrix.md",
    "control/audits/workbench-foundation-00-v0/view_model_inventory.md",
    "control/audits/workbench-foundation-00-v0/future_module_matrix.md",
    "control/audits/workbench-foundation-00-v0/validation.md",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("Workbench foundation validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty file: {rel}")

    doctrine = (root / "docs/architecture/WORKBENCH_FOUNDATION.md").read_text(encoding="utf-8") if (root / "docs/architecture/WORKBENCH_FOUNDATION.md").is_file() else ""
    for phrase in ("internal/operator superset", "restricted projection", "does not implement HTTP routes", "production readiness"):
        if phrase not in doctrine:
            errors.append(f"Workbench doctrine missing phrase: {phrase}")

    routes = {str(item.get("route_id")) for item in payloads["control/inventory/workbench_route_matrix.json"].get("routes", [])}
    missing_routes = REQUIRED_ROUTES - routes
    if missing_routes:
        errors.append(f"route matrix missing routes: {', '.join(sorted(missing_routes))}")

    projection = payloads["control/inventory/workbench_projection_matrix.json"]
    profiles = set(projection.get("projection_profiles", []))
    if REQUIRED_PROFILES - profiles:
        errors.append(f"projection matrix missing profiles: {', '.join(sorted(REQUIRED_PROFILES - profiles))}")
    projection_rows = {str(item.get("projection_profile")): item for item in projection.get("rows", []) if isinstance(item, Mapping)}
    public = projection_rows.get("public_web", {})
    native = projection_rows.get("native_desktop_read_only", {})
    if public.get("can_run_source_probe") is not False:
        errors.append("public_web cannot run source probes by default")
    if public.get("can_rebuild_index") is not False:
        errors.append("public_web cannot mutate/rebuild reviewed index")
    if native.get("can_mutate_instance") is not False:
        errors.append("native read-only cannot mutate instance")
    for key in ("can_download", "can_extract", "can_call_model", "can_deploy"):
        if public.get(key) is not False or native.get(key) is not False:
            errors.append(f"{key} must be disabled for public/native projections")

    permissions = {str(item.get("permission_id")): item for item in payloads["control/inventory/workbench_permission_matrix.json"].get("permissions", []) if isinstance(item, Mapping)}
    if REQUIRED_PERMISSIONS - set(permissions):
        errors.append(f"permission matrix missing permissions: {', '.join(sorted(REQUIRED_PERMISSIONS - set(permissions)))}")
    for permission in ("run_source_probe", "run_extraction", "call_model_provider", "deploy_public_site", "mutate_master_index"):
        row = permissions.get(permission, {})
        if row.get("public_web") is not False:
            errors.append(f"{permission} must be false for public_web")
        if row.get("native_read_only") is not False:
            errors.append(f"{permission} must be false for native_read_only")

    views = {str(item.get("view_id")) for item in payloads["control/inventory/workbench_view_model_inventory.json"].get("views", [])}
    if REQUIRED_VIEWS - views:
        errors.append(f"view inventory missing views: {', '.join(sorted(REQUIRED_VIEWS - views))}")

    locations = {str(item.get("path")): item for item in payloads["control/inventory/workbench_packet_location_matrix.json"].get("locations", []) if isinstance(item, Mapping)}
    if REQUIRED_LOCATIONS - set(locations):
        errors.append(f"packet location matrix missing locations: {', '.join(sorted(REQUIRED_LOCATIONS - set(locations)))}")
    for path, item in locations.items():
        if item.get("runtime_owns_contracts") is not False or item.get("surfaces_own_contracts") is not False:
            errors.append(f"{path} must not be owned by runtime or surfaces")

    for rel in ("control/inventory/workbench_public_projection_boundary.json", "control/inventory/workbench_native_projection_boundary.json"):
        boundary = payloads[rel]
        for key in (
            "source_probes_allowed", "downloads_allowed", "uploads_allowed", "extraction_allowed",
            "model_provider_calls_allowed", "reviewed_index_mutation_allowed", "master_index_mutation_allowed",
            "deployment_allowed", "raw_source_cache_access_allowed", "private_local_paths_allowed",
            "operator_tokens_allowed", "unreviewed_truth_claims_allowed",
        ):
            if boundary.get(key) is not False:
                errors.append(f"{rel}: {key} must be false")

    policy = payloads["control/policies/workbench_permission_policy.json"]
    for key in ("public_web_can_run_source_probe_by_default", "public_web_can_mutate_reviewed_index", "native_read_only_can_mutate_instance", "downloads_enabled_by_default", "extraction_enabled_by_default", "model_provider_enabled_by_default", "deployment_enabled_by_default"):
        if policy.get(key) is not False:
            errors.append(f"permission policy {key} must be false")

    result = payloads["control/inventory/workbench_foundation_result.json"]
    for key in (
        "doctrine_added", "projection_model_added", "view_model_boundary_added", "workbench_contracts_added",
        "projection_contracts_added", "view_model_contracts_added", "route_matrix_added", "projection_matrix_added",
        "permission_matrix_added", "view_model_inventory_added", "packet_location_matrix_added", "future_module_matrix_added",
        "public_projection_boundary_added", "native_projection_boundary_added", "policies_added", "validator_added", "tests_added",
    ):
        require_true(result, key, errors)
    for key in (
        "runtime_behavior_changed", "html_ui_implemented", "search_interaction_implemented", "ia_hunt_bridge_implemented",
        "source_probe_executed", "extraction_executed", "model_provider_used", "deployment_performed",
        "production_readiness_claimed", "public_launch_readiness_claimed", "marketplace_or_app_store_readiness_claimed",
    ):
        require_false(result, key, errors)
    if not str(result.get("recommended_next_task", "")).startswith("SEARCH-INTERACTION-00"):
        errors.append("recommended next task must be SEARCH-INTERACTION-00")

    next_task = payloads["control/inventory/workbench_foundation_next_task_decision.json"]
    if next_task.get("decision") != "SEARCH-INTERACTION-00":
        errors.append("next task decision must be SEARCH-INTERACTION-00")

    report = payloads["control/audits/workbench-foundation-00-v0/workbench_foundation_report.json"]
    if report.get("status") != "pass":
        errors.append("audit report status must be pass")

    return {
        "schema_version": "workbench_foundation_validation.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "runtime_behavior_changed": False,
        "html_ui_implemented": False,
        "source_probe_executed": False,
        "model_provider_calls_made": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON file {path}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{path} schema_version must be {schema_version}")
    return payload


def require_true(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not True:
        errors.append(f"{key} must be true")


def require_false(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not False:
        errors.append(f"{key} must be false")


if __name__ == "__main__":
    raise SystemExit(main())

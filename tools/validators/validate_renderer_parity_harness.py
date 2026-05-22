"""Validate renderer parity harness contracts and parity-case inventories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/representations/renderer_parity_harness.v0.json"
POLICY_PATH = "control/inventory/publication/renderer_parity_harness_policy.json"
MATRIX_PATH = "control/inventory/publication/renderer_parity_check_matrix.json"
REPRESENTATION_PROFILES_PATH = "control/inventory/publication/representation_profiles.json"
DESIGN_PROFILE_MATRIX_PATH = "control/inventory/publication/design_profile_matrix.json"
ROUTE_MATRIX_PATH = "control/inventory/publication/route_view_representation_matrix.json"
SEMANTIC_PARITY_POLICY_PATH = "control/inventory/publication/semantic_renderer_parity_policy.json"
EXAMPLE_CASE_PATHS = (
    "examples/renderer_parity/object_page_parity_case_future_v0.json",
    "examples/renderer_parity/search_page_parity_case_v0.json",
    "examples/renderer_parity/source_page_parity_case_future_v0.json",
)

CONTRACT_REQUIRED_FIELDS = {
    "allowed_degradations",
    "description",
    "forbidden_claims",
    "forbidden_omissions",
    "harness_id",
    "harness_status",
    "label",
    "no_goals",
    "notes",
    "optional_checks",
    "parity_result",
    "product_boundary",
    "projection_outputs",
    "representation_profiles",
    "required_checks",
    "schema_version",
    "semantic_categories",
    "source_view_model",
    "view_family",
}
CASE_REQUIRED_FIELDS = {
    "allowed_degradation_notes",
    "design_profile_refs",
    "expected_status",
    "forbidden_json_claims",
    "forbidden_text_markers",
    "notes",
    "output_bindings",
    "parity_case_id",
    "representation_profile_refs",
    "required_json_paths",
    "required_semantic_categories",
    "required_text_markers",
    "route_family",
    "schema_version",
    "semantic_requirements_ref",
    "source_view_model_path",
    "view_family",
    "view_model_policy_ref",
}
OUTPUT_REQUIRED_FIELDS = {
    "degradation_allowed",
    "design_profile",
    "exists_required",
    "json_claims_forbidden",
    "json_paths_required",
    "notes",
    "output_id",
    "output_kind",
    "output_path",
    "representation_profile",
    "semantic_categories_required",
    "text_markers_forbidden",
    "text_markers_required",
}
REQUIRED_OUTPUT_KINDS = {
    "file_tree_static",
    "html32_future",
    "lite_static_html",
    "native_card_future",
    "print_future",
    "relay_future",
    "snapshot_future",
    "standard_static_html",
    "static_json_handoff",
    "terminal_future",
    "text_static",
}
REQUIRED_SEMANTIC_CATEGORIES = {
    "absence_scope",
    "allowed_actions",
    "blocked_actions",
    "candidate_identity",
    "candidate_review_state",
    "compatibility_posture",
    "download_unavailable_posture",
    "evidence_posture",
    "hosted_unavailable_posture",
    "live_probe_unavailable_posture",
    "limitations",
    "master_index_boundary",
    "need_identity",
    "object_identity",
    "query_identity",
    "result_identity",
    "rights_posture",
    "risk_posture",
    "route_identity",
    "source_identity",
    "source_posture",
    "unresolved_gaps",
    "upload_account_telemetry_unavailable_posture",
    "view_identity",
}
REQUIRED_BOUNDARY_FIELDS = {
    "changed_generated_site_artifacts",
    "changed_product_behavior",
    "changed_public_routes",
    "claimed_automatic_merge_or_promotion",
    "claimed_exhaustive_global_search",
    "claimed_google_affiliation",
    "claimed_malware_safety",
    "claimed_rights_clearance",
    "claimed_verified_installability",
    "created_native_projects",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_execution",
    "enabled_hosting",
    "enabled_installers",
    "enabled_live_probes",
    "enabled_source_connectors",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "mutated_master_index",
    "regenerated_site_dist",
}
REQUIRED_FORBIDDEN_MARKERS = {
    "accounts_enabled",
    "direct_downloads_enabled",
    "external_search_engine_affiliation",
    "google_affiliation_or_copied_branding",
    "hosted_backend_active",
    "live_probes_enabled",
    "malware_safety",
    "master_index_mutation",
    "rights_clearance",
    "telemetry_enabled",
    "uploads_enabled",
    "verified_installability",
}
FUTURE_STATUSES = {"deferred", "future", "no_active_outputs_required", "skipped"}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka renderer parity harness files.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_renderer_parity_harness(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_renderer_parity_harness(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors)
    policy = _load_json(root / POLICY_PATH, errors)
    matrix = _load_json(root / MATRIX_PATH, errors)
    representation_profiles = _load_json(root / REPRESENTATION_PROFILES_PATH, errors)
    design_matrix = _load_json(root / DESIGN_PROFILE_MATRIX_PATH, errors)
    route_matrix = _load_json(root / ROUTE_MATRIX_PATH, errors)
    semantic_policy = _load_json(root / SEMANTIC_PARITY_POLICY_PATH, errors)

    representation_ids = _representation_ids(representation_profiles)
    design_profile_ids = _design_profile_ids(design_matrix)
    route_family_ids = _route_family_ids(route_matrix)
    semantic_policy_ids = _semantic_policy_ids(semantic_policy)
    semantic_categories = set(_string_items(_mapping(policy).get("semantic_category_vocabulary")))

    errors.extend(validate_contract_schema(contract, CONTRACT_PATH))
    errors.extend(validate_policy_inventory(policy, POLICY_PATH, representation_ids, design_profile_ids))
    errors.extend(
        validate_check_matrix(
            matrix,
            MATRIX_PATH,
            root,
            representation_ids,
            design_profile_ids,
            route_family_ids,
            semantic_policy_ids,
            semantic_categories,
        )
    )
    for path in EXAMPLE_CASE_PATHS:
        case = _load_json(root / path, errors)
        errors.extend(
            validate_parity_case(
                case,
                path,
                root,
                representation_ids,
                design_profile_ids,
                route_family_ids,
                semantic_policy_ids,
                semantic_categories,
            )
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "contract": CONTRACT_PATH,
        "policy": POLICY_PATH,
        "matrix": MATRIX_PATH,
        "examples": list(EXAMPLE_CASE_PATHS),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_contract_schema(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    for field in {"$schema", "$id", "title", "description", "type", "required", "properties"}:
        if field not in data:
            errors.append(f"{source}: missing schema field {field}")
    required = set(_string_items(data.get("required")))
    for field in sorted(CONTRACT_REQUIRED_FIELDS):
        if field not in required:
            errors.append(f"{source}: schema required list missing {field}")
    return errors


def validate_policy_inventory(
    payload: Any,
    source: str,
    representation_ids: set[str],
    design_profile_ids: set[str],
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source}: schema_version must be {SCHEMA_VERSION}")
    if data.get("contract_ref") != CONTRACT_PATH:
        errors.append(f"{source}: contract_ref must be {CONTRACT_PATH}")
    for output_kind in sorted(REQUIRED_OUTPUT_KINDS):
        if output_kind not in _string_items(data.get("allowed_output_kinds")):
            errors.append(f"{source}: allowed_output_kinds missing {output_kind}")
    for profile in _string_items(data.get("allowed_representation_profiles")):
        if profile not in representation_ids:
            errors.append(f"{source}: unknown representation profile {profile}")
    for profile in _string_items(data.get("allowed_design_profiles")):
        if profile not in design_profile_ids:
            errors.append(f"{source}: unknown design profile {profile}")
    categories = set(_string_items(data.get("semantic_category_vocabulary")))
    for category in sorted(REQUIRED_SEMANTIC_CATEGORIES):
        if category not in categories:
            errors.append(f"{source}: semantic_category_vocabulary missing {category}")
    markers = set(_string_items(data.get("forbidden_claim_markers")))
    for marker in sorted(REQUIRED_FORBIDDEN_MARKERS):
        if marker not in markers:
            errors.append(f"{source}: forbidden_claim_markers missing {marker}")
    for field in sorted(REQUIRED_BOUNDARY_FIELDS):
        if field not in _string_items(data.get("required_current_product_boundary_booleans")):
            errors.append(f"{source}: required_current_product_boundary_booleans missing {field}")
    errors.extend(_product_boundary_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_check_matrix(
    payload: Any,
    source: str,
    repo_root: Path,
    representation_ids: set[str],
    design_profile_ids: set[str],
    route_family_ids: set[str],
    semantic_policy_ids: set[str],
    semantic_categories: set[str],
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source}: schema_version must be {SCHEMA_VERSION}")
    if data.get("policy_ref") != POLICY_PATH:
        errors.append(f"{source}: policy_ref must be {POLICY_PATH}")
    cases = data.get("parity_cases")
    if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)) or not cases:
        errors.append(f"{source}: parity_cases must be a non-empty array")
        return errors
    seen: set[str] = set()
    for index, item in enumerate(cases):
        record = _mapping(item)
        case_id = record.get("parity_case_id")
        if not isinstance(case_id, str):
            errors.append(f"{source}: parity_cases[{index}] missing parity_case_id")
            continue
        if case_id in seen:
            errors.append(f"{source}: duplicate parity_case_id {case_id}")
        seen.add(case_id)
        if record.get("route_family") not in route_family_ids:
            errors.append(f"{source}: {case_id} unknown route_family {record.get('route_family')}")
        case_payload, case_source = _matrix_case_payload(record, source, repo_root, errors)
        if case_payload is not None:
            errors.extend(
                validate_parity_case(
                    case_payload,
                    case_source,
                    repo_root,
                    representation_ids,
                    design_profile_ids,
                    route_family_ids,
                    semantic_policy_ids,
                    semantic_categories,
                )
            )
    errors.extend(_product_boundary_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_parity_case(
    payload: Any,
    source: str,
    repo_root: Path,
    representation_ids: set[str],
    design_profile_ids: set[str],
    route_family_ids: set[str],
    semantic_policy_ids: set[str],
    semantic_categories: set[str],
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if not data:
        return [f"{source}: expected JSON object"]
    for field in sorted(CASE_REQUIRED_FIELDS):
        if field not in data:
            errors.append(f"{source}: missing required field {field}")
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source}: schema_version must be {SCHEMA_VERSION}")
    case_id = str(data.get("parity_case_id", source))
    route_family = data.get("route_family")
    if route_family not in route_family_ids:
        errors.append(f"{source}: unknown route_family {route_family}")
    for profile in _string_items(data.get("representation_profile_refs")):
        if profile not in representation_ids:
            errors.append(f"{source}: unknown representation profile {profile}")
    for profile in _string_items(data.get("design_profile_refs")):
        if profile not in design_profile_ids:
            errors.append(f"{source}: unknown design profile {profile}")
    semantic_policy_ref = data.get("semantic_parity_policy_ref")
    if isinstance(semantic_policy_ref, str) and semantic_policy_ref and semantic_policy_ref not in semantic_policy_ids:
        errors.append(f"{source}: unknown semantic parity policy {semantic_policy_ref}")
    errors.extend(_path_ref_errors(data.get("view_model_policy_ref"), repo_root, source, allow_fragment=False))
    errors.extend(_path_ref_errors(data.get("semantic_requirements_ref"), repo_root, source, allow_fragment=True))
    categories = _string_items(data.get("required_semantic_categories"))
    if not categories:
        errors.append(f"{source}: required_semantic_categories must be non-empty")
    for category in categories:
        if category not in semantic_categories:
            errors.append(f"{source}: unknown semantic category {category}")
    status_values = {str(data.get("case_status", "")), str(data.get("expected_status", ""))}
    future_case = bool(status_values & FUTURE_STATUSES)
    source_view_model_path = data.get("source_view_model_path")
    if isinstance(source_view_model_path, str) and source_view_model_path:
        if not (repo_root / source_view_model_path).is_file():
            errors.append(f"{source}: source_view_model_path missing {source_view_model_path}")
    elif not future_case:
        errors.append(f"{source}: current case {case_id} must define source_view_model_path")
    outputs = data.get("output_bindings")
    if not isinstance(outputs, Sequence) or isinstance(outputs, (str, bytes)):
        errors.append(f"{source}: output_bindings must be an array")
        outputs = []
    if not outputs and not future_case:
        errors.append(f"{source}: current case {case_id} must define output_bindings")
    for index, item in enumerate(outputs):
        errors.extend(
            validate_output_binding(
                item,
                f"{source}: output_bindings[{index}]",
                repo_root,
                representation_ids,
                design_profile_ids,
                semantic_categories,
                require_existing=not future_case,
            )
        )
    errors.extend(_product_boundary_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_output_binding(
    payload: Any,
    source: str,
    repo_root: Path,
    representation_ids: set[str],
    design_profile_ids: set[str],
    semantic_categories: set[str],
    *,
    require_existing: bool,
) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    for field in sorted(OUTPUT_REQUIRED_FIELDS):
        if field not in data:
            errors.append(f"{source}: missing {field}")
    output_kind = data.get("output_kind")
    if output_kind not in REQUIRED_OUTPUT_KINDS:
        errors.append(f"{source}: unknown output_kind {output_kind}")
    representation = data.get("representation_profile")
    if representation not in representation_ids:
        errors.append(f"{source}: unknown representation profile {representation}")
    design = data.get("design_profile")
    if design not in design_profile_ids:
        errors.append(f"{source}: unknown design profile {design}")
    for category in _string_items(data.get("semantic_categories_required")):
        if category not in semantic_categories:
            errors.append(f"{source}: unknown semantic category {category}")
    output_path = data.get("output_path")
    if require_existing and data.get("exists_required") is True and isinstance(output_path, str):
        if not (repo_root / output_path).is_file():
            errors.append(f"{source}: required output missing {output_path}")
    return errors


def _matrix_case_payload(record: Mapping[str, Any], source: str, repo_root: Path, errors: list[str]) -> tuple[Any | None, str]:
    case_ref = record.get("case_ref")
    if isinstance(case_ref, str) and case_ref:
        return _load_json(repo_root / case_ref, errors), case_ref
    inline = record.get("case_inline")
    if isinstance(inline, Mapping):
        return inline, f"{source}: {record.get('parity_case_id')}.case_inline"
    errors.append(f"{source}: {record.get('parity_case_id')} must define case_ref or case_inline")
    return None, source


def _path_ref_errors(value: Any, repo_root: Path, source: str, *, allow_fragment: bool) -> list[str]:
    if not isinstance(value, str) or not value:
        return [f"{source}: expected non-empty path ref"]
    path_part = value.split("#", 1)[0] if allow_fragment else value
    if not (repo_root / path_part).is_file():
        return [f"{source}: referenced path missing {path_part}"]
    return []


def _product_boundary_errors(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED_BOUNDARY_FIELDS):
        if field not in boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _representation_ids(payload: Any) -> set[str]:
    profiles = _mapping(payload).get("profiles")
    if not isinstance(profiles, Sequence) or isinstance(profiles, (str, bytes)):
        return set()
    return {
        str(item["representation_profile_id"])
        for item in profiles
        if isinstance(item, Mapping) and isinstance(item.get("representation_profile_id"), str)
    }


def _design_profile_ids(payload: Any) -> set[str]:
    profiles = _mapping(payload).get("profiles")
    if not isinstance(profiles, Sequence) or isinstance(profiles, (str, bytes)):
        return set()
    return {
        str(item["profile_id"])
        for item in profiles
        if isinstance(item, Mapping) and isinstance(item.get("profile_id"), str)
    }


def _route_family_ids(payload: Any) -> set[str]:
    families = _mapping(payload).get("route_families")
    if not isinstance(families, Sequence) or isinstance(families, (str, bytes)):
        return set()
    return {
        str(item["route_family_id"])
        for item in families
        if isinstance(item, Mapping) and isinstance(item.get("route_family_id"), str)
    }


def _semantic_policy_ids(payload: Any) -> set[str]:
    policies = _mapping(payload).get("policies")
    if not isinstance(policies, Sequence) or isinstance(policies, (str, bytes)):
        return set()
    return {
        str(item["parity_policy_id"])
        for item in policies
        if isinstance(item, Mapping) and isinstance(item.get("parity_policy_id"), str)
    }


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_renderer_parity_harness: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"matrix: {report['matrix']}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

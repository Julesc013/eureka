from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/view/pages/view_model_policy_index.v0.json"
POLICY_INDEX_PATH = "control/inventory/publication/view_model_policy_index.json"
EXAMPLE_INDEX_PATH = "examples/view_models/policy_index/minimal_view_model_policy_index_v0.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"

REQUIRED_SCHEMA_FIELDS = {"$schema", "$id", "title", "description", "type", "required", "properties"}
TOP_LEVEL_FIELDS = {
    "schema_version", "index_id", "label", "description", "track", "status", "view_model_families",
    "policy_files", "schema_files", "documentation_files", "example_roots", "validator_files",
    "route_matrix_ref", "semantic_parity_policy_ref", "representation_profile_inventory_ref",
    "host_profile_inventory_ref", "capability_negotiation_policy_ref", "validation_groups",
    "product_boundary", "no_goals", "notes",
}
FAMILY_FIELDS = {
    "view_family", "route_families", "schema_path", "policy_inventory_path", "documentation_path",
    "example_paths", "validator_path", "test_path", "semantic_parity_policy_ids",
    "allowed_representation_profiles", "current_status", "future_status",
    "required_product_boundary_fields", "blocked_claims", "notes",
}
VALIDATION_GROUP_FIELDS = {
    "group_id", "label", "validators", "policy_files", "example_roots", "required_before", "no_goals", "notes",
}
EXPECTED_VIEW_FAMILIES = {
    "AbsencePageView", "CandidatePageView", "ComparePageView", "DownloadManifestView", "EvidencePageView",
    "NeedPageView", "ObjectPageView", "PackPageView", "ReviewPageView", "SearchPageView", "SourcePageView",
    "TaskPageView",
}
EXPECTED_POLICY_FILES = {
    "control/inventory/publication/host_profiles.json",
    "control/inventory/publication/representation_profiles.json",
    "control/inventory/publication/capability_negotiation_policy.json",
    "control/inventory/publication/semantic_renderer_parity_policy.json",
    "control/inventory/publication/route_view_representation_matrix.json",
    "control/inventory/publication/search_page_view_model_policy.json",
    "control/inventory/publication/object_page_view_model_policy.json",
    "control/inventory/publication/source_page_view_model_policy.json",
    "control/inventory/publication/need_page_view_model_policy.json",
    "control/inventory/publication/candidate_page_view_model_policy.json",
    "control/inventory/publication/pack_page_view_model_policy.json",
    "control/inventory/publication/task_page_view_model_policy.json",
    "control/inventory/publication/review_page_view_model_policy.json",
    "control/inventory/publication/download_manifest_view_model_policy.json",
    "control/inventory/publication/evidence_page_view_model_policy.json",
    "control/inventory/publication/absence_page_view_model_policy.json",
    "control/inventory/publication/compare_page_view_model_policy.json",
}
EXPECTED_VALIDATION_GROUPS = {
    "all_track_a_contracts", "download_evidence_absence_compare_view_models", "need_candidate_page_view_models",
    "object_page_view_model", "pack_task_review_page_view_models", "representation_contracts",
    "route_view_matrix", "search_page_view_model", "semantic_renderer_parity", "source_page_view_model",
}
PRODUCT_BOUNDARY_FIELDS = {
    "changed_product_behavior", "changed_public_routes", "changed_generated_site_artifacts",
    "enabled_hosting", "enabled_live_probes", "enabled_source_sync", "enabled_source_connectors",
    "enabled_downloads", "enabled_installers", "enabled_execution", "enabled_uploads", "enabled_accounts",
    "enabled_telemetry", "enabled_node_runtime", "enabled_pack_import_runtime", "enabled_review_runtime",
    "created_native_projects", "mutated_master_index", "claimed_rights_clearance", "claimed_malware_safety",
    "claimed_verified_installability", "claimed_public_truth_from_candidates", "claimed_public_truth_from_packs",
    "claimed_public_truth_from_reviews", "claimed_public_truth_from_evidence", "claimed_exhaustive_global_search",
    "claimed_automatic_merge_or_promotion",
}
FORBIDDEN_TRUE_FIELDS = PRODUCT_BOUNDARY_FIELDS | {
    "accepted_public_status", "active_node_runtime", "automatic_dedup_enabled", "automatic_merge_enabled",
    "automatic_promotion_enabled", "download_runtime_enabled", "evidence_truth_claimed",
    "exhaustive_global_search_claimed", "hosted_backend_claimed", "live_source_claimed",
    "master_index_mutation_allowed", "native_project_created", "pack_import_runtime_enabled",
    "production_deployment_claimed", "review_runtime_enabled", "source_connector_enabled",
    "source_sync_runtime_enabled",
}
UNSAFE_PATTERNS = [
    re.compile(r"sk-(?:proj|live|svcacct)-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bapi[_-]?key\s*[:=]", re.IGNORECASE),
    re.compile(r"\bauth[_-]?token\s*[:=]", re.IGNORECASE),
    re.compile(r"\b[A-Za-z]:\\"),
    re.compile(r"(^|[\"' ])/(home|Users|var|etc|root)/"),
    re.compile(r"\b\S+\.(exe|msi|dmg|pkg|deb|rpm|zip|tar\.gz)\b", re.IGNORECASE),
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Eureka Track A view-model policy index.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_view_model_policy_index(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_view_model_policy_index(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors, root)
    index = _load_json(root / POLICY_INDEX_PATH, errors, root)
    example = _load_json(root / EXAMPLE_INDEX_PATH, errors, root)
    representations = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY, errors, root)
    route_matrix = _load_json(root / ROUTE_MATRIX_INVENTORY, errors, root)

    if isinstance(contract, Mapping):
        _validate_schema(CONTRACT_PATH, contract, errors)
    if all(isinstance(payload, Mapping) for payload in (index, representations, semantic, route_matrix)):
        errors.extend(validate_payloads(index, representations, semantic, route_matrix, root, source_label="inventory", require_full=True))
    if all(isinstance(payload, Mapping) for payload in (example, representations, semantic, route_matrix)):
        errors.extend(validate_payloads(example, representations, semantic, route_matrix, root, source_label="example", require_full=False))

    errors = sorted(set(errors))
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": sorted(set(warnings)),
        "view_model_family_count": _family_count(index),
        "validation_group_count": _group_count(index),
        "example_view_model_family_count": _family_count(example),
    }


def validate_payloads(
    index: Mapping[str, Any],
    representations: Mapping[str, Any],
    semantic: Mapping[str, Any],
    route_matrix: Mapping[str, Any],
    repo_root: Path = REPO_ROOT,
    *,
    source_label: str = "payload",
    require_full: bool = True,
) -> list[str]:
    errors: list[str] = []
    root = repo_root.resolve()
    representation_ids = _representation_ids(representations)
    semantic_ids = _semantic_policy_ids(semantic)
    route_records = _route_records(route_matrix)

    missing_top = TOP_LEVEL_FIELDS - set(index)
    if missing_top:
        errors.append(f"{source_label}: missing top-level fields {sorted(missing_top)}")
    if index.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source_label}: schema_version must be {SCHEMA_VERSION}")
    if index.get("track") != "A":
        errors.append(f"{source_label}: track must be 'A'")

    product_boundary = _mapping(index.get("product_boundary"))
    missing_boundary = PRODUCT_BOUNDARY_FIELDS - set(product_boundary)
    if missing_boundary:
        errors.append(f"{source_label}: product_boundary missing {sorted(missing_boundary)}")
    for field in sorted(PRODUCT_BOUNDARY_FIELDS):
        if product_boundary.get(field) is not False:
            errors.append(f"{source_label}: product_boundary.{field} must be false")
    errors.extend(_validate_no_forbidden_true_fields(source_label, index))
    errors.extend(_validate_unsafe_patterns(source_label, index))

    for path_key in (
        "route_matrix_ref", "semantic_parity_policy_ref", "representation_profile_inventory_ref",
        "host_profile_inventory_ref", "capability_negotiation_policy_ref",
    ):
        path = index.get(path_key)
        if isinstance(path, str):
            _require_existing_path(f"{source_label}: {path_key}", root, path, errors, must_be_file=True)

    for key, must_be_file in (
        ("policy_files", True),
        ("schema_files", True),
        ("documentation_files", True),
        ("validator_files", True),
        ("example_roots", False),
    ):
        for path in _string_items(index.get(key)):
            _require_existing_path(f"{source_label}: {key}", root, path, errors, must_be_file=must_be_file)

    if require_full:
        missing_policies = EXPECTED_POLICY_FILES - set(_string_items(index.get("policy_files")))
        if missing_policies:
            errors.append(f"{source_label}: policy_files missing {sorted(missing_policies)}")

    families = index.get("view_model_families")
    if not isinstance(families, Sequence) or isinstance(families, (str, bytes)):
        errors.append(f"{source_label}: view_model_families must be an array")
        families = []
    family_ids = [family.get("view_family") for family in families if isinstance(family, Mapping)]
    duplicate_families = sorted({item for item in family_ids if family_ids.count(item) > 1})
    if duplicate_families:
        errors.append(f"{source_label}: duplicate view families {duplicate_families}")
    if require_full:
        missing_families = EXPECTED_VIEW_FAMILIES - set(str(item) for item in family_ids)
        if missing_families:
            errors.append(f"{source_label}: view_model_families missing {sorted(missing_families)}")

    for index_number, family in enumerate(families):
        if not isinstance(family, Mapping):
            errors.append(f"{source_label}: view_model_families[{index_number}] must be an object")
            continue
        errors.extend(_validate_family(f"{source_label}: {family.get('view_family', index_number)}", family, root, representation_ids, semantic_ids, route_records))

    groups = index.get("validation_groups")
    if not isinstance(groups, Sequence) or isinstance(groups, (str, bytes)):
        errors.append(f"{source_label}: validation_groups must be an array")
        groups = []
    group_ids = [group.get("group_id") for group in groups if isinstance(group, Mapping)]
    duplicate_groups = sorted({item for item in group_ids if group_ids.count(item) > 1})
    if duplicate_groups:
        errors.append(f"{source_label}: duplicate validation groups {duplicate_groups}")
    if require_full:
        missing_groups = EXPECTED_VALIDATION_GROUPS - set(str(item) for item in group_ids)
        if missing_groups:
            errors.append(f"{source_label}: validation_groups missing {sorted(missing_groups)}")
    for group in groups:
        if isinstance(group, Mapping):
            errors.extend(_validate_validation_group(f"{source_label}: group {group.get('group_id')}", group, root))

    return sorted(errors)


def _validate_schema(path: str, schema: Mapping[str, Any], errors: list[str]) -> None:
    missing = REQUIRED_SCHEMA_FIELDS - set(schema)
    if missing:
        errors.append(f"{path}: schema missing top-level fields {sorted(missing)}")
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, Mapping):
        errors.append(f"{path}: properties must be an object")
        return
    if not isinstance(required, Sequence) or isinstance(required, (str, bytes)):
        errors.append(f"{path}: required must be an array")
        return
    required_set = {item for item in required if isinstance(item, str)}
    missing_required = TOP_LEVEL_FIELDS - required_set
    missing_properties = TOP_LEVEL_FIELDS - set(properties)
    if missing_required:
        errors.append(f"{path}: required missing {sorted(missing_required)}")
    if missing_properties:
        errors.append(f"{path}: properties missing {sorted(missing_properties)}")
    if _mapping(properties.get("schema_version")).get("const") != SCHEMA_VERSION:
        errors.append(f"{path}: schema_version const must be {SCHEMA_VERSION!r}")


def _validate_family(
    label: str,
    family: Mapping[str, Any],
    root: Path,
    representation_ids: set[str],
    semantic_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = FAMILY_FIELDS - set(family)
    if missing:
        errors.append(f"{label}: missing fields {sorted(missing)}")
    for key in ("schema_path", "policy_inventory_path", "documentation_path", "validator_path", "test_path"):
        path = family.get(key)
        if isinstance(path, str):
            _require_existing_path(f"{label}: {key}", root, path, errors, must_be_file=True)
    for path in _string_items(family.get("example_paths")):
        _require_existing_path(f"{label}: example_paths", root, path, errors, must_be_file=True)

    policy = _load_json(root / str(family.get("policy_inventory_path", "")), errors, root)
    if isinstance(policy, Mapping):
        if policy.get("canonical_view_family") != family.get("view_family"):
            errors.append(f"{label}: policy canonical_view_family does not match index view_family")
        policy_routes = set(_string_items(policy.get("supported_route_families")))
        missing_policy_routes = set(_string_items(family.get("route_families"))) - policy_routes
        if missing_policy_routes:
            errors.append(f"{label}: route_families not present in policy {sorted(missing_policy_routes)}")
        policy_profiles = set(_string_items(policy.get("allowed_representation_profiles")))
        missing_policy_profiles = set(_string_items(family.get("allowed_representation_profiles"))) - policy_profiles
        if missing_policy_profiles:
            errors.append(f"{label}: allowed profiles not present in policy {sorted(missing_policy_profiles)}")
        policy_semantic = policy.get("required_semantic_parity_policy")
        if isinstance(policy_semantic, str) and policy_semantic not in set(_string_items(family.get("semantic_parity_policy_ids"))):
            errors.append(f"{label}: semantic_parity_policy_ids must include policy required_semantic_parity_policy")

    for route_id in _string_items(family.get("route_families")):
        if route_id not in route_records:
            errors.append(f"{label}: route_family {route_id!r} is missing from route matrix")
    missing_profiles = set(_string_items(family.get("allowed_representation_profiles"))) - representation_ids
    if missing_profiles:
        errors.append(f"{label}: unknown representation profiles {sorted(missing_profiles)}")
    missing_semantic = set(_string_items(family.get("semantic_parity_policy_ids"))) - semantic_ids
    if missing_semantic:
        errors.append(f"{label}: unknown semantic parity policy ids {sorted(missing_semantic)}")
    if not _string_items(family.get("blocked_claims")):
        errors.append(f"{label}: blocked_claims must be non-empty")
    return errors


def _validate_validation_group(label: str, group: Mapping[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    missing = VALIDATION_GROUP_FIELDS - set(group)
    if missing:
        errors.append(f"{label}: missing fields {sorted(missing)}")
    for path in _string_items(group.get("validators")):
        _require_existing_path(f"{label}: validators", root, path, errors, must_be_file=True)
    for path in _string_items(group.get("policy_files")):
        _require_existing_path(f"{label}: policy_files", root, path, errors, must_be_file=True)
    for path in _string_items(group.get("example_roots")):
        _require_existing_path(f"{label}: example_roots", root, path, errors, must_be_file=False)
    return errors


def _validate_no_forbidden_true_fields(label: str, value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FIELDS and child is not False:
                errors.append(f"{label}: {child_path} must be false")
            errors.extend(_validate_no_forbidden_true_fields(label, child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            errors.extend(_validate_no_forbidden_true_fields(label, child, f"{path}[{index}]"))
    return errors


def _validate_unsafe_patterns(label: str, payload: Mapping[str, Any]) -> list[str]:
    raw = json.dumps(payload, sort_keys=True)
    return [
        f"{label}: contains unsafe/private pattern {pattern.pattern}"
        for pattern in UNSAFE_PATTERNS
        if pattern.search(raw)
    ]


def _require_existing_path(label: str, root: Path, path: str, errors: list[str], *, must_be_file: bool) -> None:
    target = root / path
    if must_be_file and not target.is_file():
        errors.append(f"{label}: file does not exist {path!r}")
    elif not must_be_file and not target.exists():
        errors.append(f"{label}: path does not exist {path!r}")


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file not found")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _representation_ids(inventory: Mapping[str, Any]) -> set[str]:
    profiles = inventory.get("profiles")
    if not isinstance(profiles, Sequence) or isinstance(profiles, (str, bytes)):
        return set()
    return {
        str(profile["representation_profile_id"])
        for profile in profiles
        if isinstance(profile, Mapping) and isinstance(profile.get("representation_profile_id"), str)
    }


def _semantic_policy_ids(inventory: Mapping[str, Any]) -> set[str]:
    policies = inventory.get("policies")
    if not isinstance(policies, Sequence) or isinstance(policies, (str, bytes)):
        return set()
    return {
        str(policy["parity_policy_id"])
        for policy in policies
        if isinstance(policy, Mapping) and isinstance(policy.get("parity_policy_id"), str)
    }


def _route_records(matrix: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    routes = matrix.get("route_families")
    if not isinstance(routes, Sequence) or isinstance(routes, (str, bytes)):
        return {}
    return {
        str(route["route_family_id"]): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("route_family_id"), str)
    }


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _family_count(payload: Any) -> int:
    if not isinstance(payload, Mapping):
        return 0
    families = payload.get("view_model_families")
    return len(families) if isinstance(families, Sequence) and not isinstance(families, (str, bytes)) else 0


def _group_count(payload: Any) -> int:
    if not isinstance(payload, Mapping):
        return 0
    groups = payload.get("validation_groups")
    return len(groups) if isinstance(groups, Sequence) and not isinstance(groups, (str, bytes)) else 0


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_view_model_policy_index: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"view_model_families: {report['view_model_family_count']}",
        f"validation_groups: {report['validation_group_count']}",
        f"example_view_model_families: {report['example_view_model_family_count']}",
    ]
    errors = report.get("errors", [])
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

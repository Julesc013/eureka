from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/representations/route_view_representation_matrix.v0.json"
MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"
HOST_INVENTORY = "control/inventory/publication/host_profiles.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
EXAMPLE_PATHS = [
    "examples/representations/route_view_matrix/minimal_route_view_matrix_v0.json",
]

REQUIRED_SCHEMA_FIELDS = {
    "$schema",
    "$id",
    "title",
    "description",
    "type",
    "required",
    "properties",
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "matrix_id",
    "label",
    "description",
    "route_families",
    "view_families",
    "representation_bindings",
    "host_profile_bindings",
    "semantic_parity_policy_bindings",
    "status_vocabulary",
    "default_fallbacks",
    "forbidden_route_splits",
    "public_alpha_policy",
    "no_product_runtime_behavior",
    "no_public_routes_changed",
    "no_hosting_enabled",
    "no_live_probes_enabled",
    "no_downloads_enabled",
    "no_uploads_enabled",
    "no_accounts_enabled",
    "no_telemetry_enabled",
    "no_native_project_created",
    "no_master_index_mutation",
    "notes",
}
ROUTE_FIELDS = {
    "route_family_id",
    "label",
    "description",
    "canonical_path_pattern",
    "route_status",
    "current_surface_status",
    "canonical_view_family",
    "route_identity_policy",
    "route_safety_class",
    "implemented_now",
    "dynamic_runtime_required",
    "hosted_runtime_active",
    "hosted_public_alpha_status",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "accounts_enabled",
    "telemetry_enabled",
    "allowed_host_profiles",
    "forbidden_host_profiles",
    "allowed_representation_profiles",
    "default_representation_profile",
    "required_semantic_parity_policy",
    "current_artifacts",
    "future_artifacts",
    "no_goals",
    "notes",
}
VIEW_FIELDS = {
    "view_family_id",
    "label",
    "description",
    "view_status",
    "canonical_route_families",
    "notes",
}
BINDING_FIELDS = {
    "route_family_id",
    "default_representation_profile",
    "allowed_representation_profiles",
}
HOST_BINDING_FIELDS = {
    "route_family_id",
    "default_host_profile",
    "allowed_host_profiles",
    "exposure_status",
}
SEMANTIC_BINDING_FIELDS = {
    "route_family_id",
    "parity_policy_id",
    "binding_status",
    "notes",
}
NO_BEHAVIOR_FLAGS = {
    "no_accounts_enabled",
    "no_downloads_enabled",
    "no_hosting_enabled",
    "no_live_probes_enabled",
    "no_master_index_mutation",
    "no_native_project_created",
    "no_product_runtime_behavior",
    "no_public_routes_changed",
    "no_telemetry_enabled",
    "no_uploads_enabled",
}
ROUTE_DISABLED_FLAGS = {
    "accounts_enabled",
    "downloads_enabled",
    "hosted_runtime_active",
    "live_probes_enabled",
    "telemetry_enabled",
    "uploads_enabled",
}
ALLOWED_STATUSES = {
    "approval_gated",
    "blocked",
    "contract_only",
    "deferred",
    "future",
    "human_operated",
    "implemented_local_runtime",
    "implemented_static",
    "operator_gated",
    "planned",
}
FUTURE_OR_DEFERRED_STATUSES = {
    "approval_gated",
    "blocked",
    "contract_only",
    "deferred",
    "future",
    "human_operated",
    "operator_gated",
    "planned",
}
REQUIRED_ROUTE_FAMILIES = {
    "absence_page_future",
    "api_search",
    "candidate_page_future",
    "compare_page_future",
    "data_static",
    "demo_static",
    "download_manifest_future",
    "evidence_page_future",
    "files_static",
    "home",
    "lite_static",
    "native_card_future",
    "need_page_future",
    "object_page_future",
    "pack_page_future",
    "query_plan",
    "relay_future",
    "review_page_future",
    "search",
    "snapshot_future",
    "source_detail",
    "sources",
    "status",
    "task_page_future",
    "text_static",
}
REQUIRED_VIEW_FAMILIES = {
    "AbsencePageView",
    "CandidatePageView",
    "ComparePageView",
    "DemoResolverView",
    "DownloadManifestView",
    "EvidencePageView",
    "FileTreeView",
    "HomePageView",
    "LitePageView",
    "NativeCardView",
    "NeedPageView",
    "ObjectPageView",
    "PackPageView",
    "QueryPlanView",
    "RelayView",
    "ReviewPageView",
    "SearchApiView",
    "SearchPageView",
    "SnapshotView",
    "SourceListView",
    "SourcePageView",
    "StaticDataView",
    "StatusView",
    "TaskPageView",
    "TextPageView",
}
FORBIDDEN_ROUTE_SPLITS = {
    "/classic/object",
    "/desktop/search",
    "/legacy/object",
    "/mobile/search",
    "/modern/search",
    "/old/search",
    "/retro/search",
}
API_ALIAS_ALLOWED_ROUTES = {
    "api_search",
    "data_static",
    "query_plan",
    "source_detail",
    "sources",
    "status",
}
UNSAFE_EXAMPLE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bapi[_-]?key\s*[:=]", re.IGNORECASE),
    re.compile(r"\bauth[_-]?token\s*[:=]", re.IGNORECASE),
    re.compile(r"\b[A-Za-z]:\\"),
    re.compile(r"(^|[\"' ])/(home|Users|var|etc|root)/"),
    re.compile(r"\b\S+\.(exe|msi|dmg|pkg|deb|rpm|zip|tar\.gz)\b", re.IGNORECASE),
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka route/view/representation matrix schema, inventory, and examples."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_route_view_representation_matrix(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_route_view_representation_matrix(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors, root)
    if isinstance(contract, Mapping):
        _validate_schema(CONTRACT_PATH, contract, errors)

    matrix = _load_json(root / MATRIX_INVENTORY, errors, root)
    hosts = _load_json(root / HOST_INVENTORY, errors, root)
    representations = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY, errors, root)
    examples: list[Mapping[str, Any]] = []
    for relative in EXAMPLE_PATHS:
        payload = _load_json(root / relative, errors, root)
        if isinstance(payload, Mapping):
            examples.append(payload)

    if (
        isinstance(matrix, Mapping)
        and isinstance(hosts, Mapping)
        and isinstance(representations, Mapping)
        and isinstance(semantic, Mapping)
    ):
        errors.extend(
            validate_payloads(
                matrix,
                hosts,
                representations,
                semantic,
                examples,
                source_label="route_view_matrix",
                require_required_route_families=True,
            )
        )

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_route_view_representation_matrix",
        "schema_version": SCHEMA_VERSION,
        "contract_checked": CONTRACT_PATH,
        "inventory_checked": MATRIX_INVENTORY,
        "host_inventory_checked": HOST_INVENTORY,
        "representation_inventory_checked": REPRESENTATION_INVENTORY,
        "semantic_parity_inventory_checked": SEMANTIC_PARITY_INVENTORY,
        "examples_checked": sorted(EXAMPLE_PATHS),
        "route_family_count": _count(matrix, "route_families"),
        "view_family_count": _count(matrix, "view_families"),
        "example_count": len(examples),
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }


def validate_payloads(
    matrix: Mapping[str, Any],
    host_inventory: Mapping[str, Any],
    representation_inventory: Mapping[str, Any],
    semantic_parity_inventory: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] | None = None,
    *,
    source_label: str,
    require_required_route_families: bool,
) -> list[str]:
    errors: list[str] = []
    host_ids, legacy_host_ids = _host_ids(host_inventory, errors, source_label)
    representation_ids = _representation_ids(representation_inventory, errors, source_label)
    semantic_policy_ids = _semantic_policy_ids(semantic_parity_inventory, errors, source_label)
    _validate_matrix(
        source_label,
        matrix,
        host_ids,
        legacy_host_ids,
        representation_ids,
        semantic_policy_ids,
        errors,
        require_required_route_families=require_required_route_families,
    )
    if examples is not None:
        for index, example in enumerate(examples):
            _validate_matrix(
                f"{source_label}: example[{index}]",
                example,
                host_ids,
                legacy_host_ids,
                representation_ids,
                semantic_policy_ids,
                errors,
                require_required_route_families=False,
                is_example=True,
            )
            for bad_path, value in _iter_strings(example):
                for pattern in UNSAFE_EXAMPLE_PATTERNS:
                    if pattern.search(value):
                        errors.append(f"{source_label}: example[{index}]: unsafe value at {bad_path}.")
    return errors


def _validate_schema(relative: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_SCHEMA_FIELDS - set(payload))
    if missing:
        errors.append(f"{relative}: schema missing top-level fields {missing}.")
    if payload.get("type") != "object":
        errors.append(f"{relative}: schema type must be object.")
    required = payload.get("required")
    if not isinstance(required, list) or not required:
        errors.append(f"{relative}: schema required must be a non-empty list.")
        required_fields: set[str] = set()
    else:
        required_fields = {item for item in required if isinstance(item, str)}
    missing_required = sorted(TOP_LEVEL_FIELDS - required_fields)
    if missing_required:
        errors.append(f"{relative}: required list missing {missing_required}.")
    schema_version = _mapping(_mapping(payload.get("properties")).get("schema_version"))
    if schema_version.get("const") != SCHEMA_VERSION:
        errors.append(f"{relative}: schema_version const must be {SCHEMA_VERSION}.")


def _validate_matrix(
    source_label: str,
    matrix: Mapping[str, Any],
    host_ids: set[str],
    legacy_host_ids: set[str],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    errors: list[str],
    *,
    require_required_route_families: bool,
    is_example: bool = False,
) -> None:
    _require_fields(source_label, matrix, TOP_LEVEL_FIELDS, errors)
    if matrix.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source_label}: schema_version must be {SCHEMA_VERSION}.")
    _validate_no_behavior_flags(source_label, matrix, errors)
    _validate_public_alpha_policy(source_label, matrix, errors)

    declared_statuses = set(_string_list(matrix.get("status_vocabulary")))
    invalid_statuses = sorted(declared_statuses - ALLOWED_STATUSES)
    if invalid_statuses:
        errors.append(f"{source_label}: status_vocabulary contains invalid statuses {invalid_statuses}.")
    if require_required_route_families:
        missing_statuses = sorted(ALLOWED_STATUSES - declared_statuses)
        if missing_statuses:
            errors.append(f"{source_label}: status_vocabulary missing {missing_statuses}.")

    declared_splits = set(_string_list(matrix.get("forbidden_route_splits")))
    missing_splits = sorted(FORBIDDEN_ROUTE_SPLITS - declared_splits)
    if missing_splits:
        errors.append(f"{source_label}: forbidden_route_splits missing {missing_splits}.")

    route_records = _object_list(matrix.get("route_families"))
    view_records = _object_list(matrix.get("view_families"))
    route_ids = _unique_ids(source_label, route_records, "route_family_id", errors)
    view_ids = _unique_ids(source_label, view_records, "view_family_id", errors)

    if require_required_route_families:
        missing_routes = sorted(REQUIRED_ROUTE_FAMILIES - route_ids)
        if missing_routes:
            errors.append(f"{source_label}: missing route families {missing_routes}.")
        missing_views = sorted(REQUIRED_VIEW_FAMILIES - view_ids)
        if missing_views:
            errors.append(f"{source_label}: missing view families {missing_views}.")

    routes_by_id = {
        route["route_family_id"]: route
        for route in route_records
        if isinstance(route.get("route_family_id"), str)
    }
    for index, route in enumerate(route_records):
        label = f"{source_label}: route[{index}]"
        route_id = route.get("route_family_id")
        if isinstance(route_id, str):
            label = f"{source_label}: route {route_id}"
        _validate_route(
            label,
            route,
            route_ids,
            view_ids,
            host_ids,
            legacy_host_ids,
            representation_ids,
            semantic_policy_ids,
            errors,
        )

    for index, view in enumerate(view_records):
        label = f"{source_label}: view[{index}]"
        view_id = view.get("view_family_id")
        if isinstance(view_id, str):
            label = f"{source_label}: view {view_id}"
        _validate_view(label, view, route_ids, errors)

    _validate_representation_bindings(
        source_label,
        matrix.get("representation_bindings"),
        routes_by_id,
        representation_ids,
        errors,
    )
    _validate_host_bindings(source_label, matrix.get("host_profile_bindings"), routes_by_id, host_ids, errors)
    _validate_semantic_bindings(
        source_label,
        matrix.get("semantic_parity_policy_bindings"),
        routes_by_id,
        semantic_policy_ids,
        errors,
    )
    if is_example:
        _validate_example_coverage(source_label, route_records, errors)


def _validate_route(
    label: str,
    route: Mapping[str, Any],
    route_ids: set[str],
    view_ids: set[str],
    host_ids: set[str],
    legacy_host_ids: set[str],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    errors: list[str],
) -> None:
    _require_fields(label, route, ROUTE_FIELDS, errors)
    route_id = route.get("route_family_id")
    status = route.get("route_status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{label}: route_status {status!r} is invalid.")
    if route.get("canonical_view_family") not in view_ids:
        errors.append(f"{label}: canonical_view_family is not registered.")
    if route.get("route_identity_policy") != "one_route_meaning_profile_negotiation_only":
        errors.append(f"{label}: route_identity_policy must preserve one route meaning.")

    allowed_representations = set(_string_list(route.get("allowed_representation_profiles")))
    if not allowed_representations:
        errors.append(f"{label}: allowed_representation_profiles must be non-empty.")
    for profile_id in sorted(allowed_representations):
        if profile_id not in representation_ids:
            errors.append(f"{label}: representation profile {profile_id} is not registered.")
    default_representation = route.get("default_representation_profile")
    if default_representation not in allowed_representations:
        errors.append(f"{label}: default_representation_profile must be allowed.")
    if default_representation not in representation_ids:
        errors.append(f"{label}: default_representation_profile {default_representation!r} is not registered.")

    allowed_hosts = set(_string_list(route.get("allowed_host_profiles")))
    if not allowed_hosts:
        errors.append(f"{label}: allowed_host_profiles must be non-empty.")
    for host_id in sorted(allowed_hosts):
        if host_id not in host_ids:
            errors.append(f"{label}: host profile {host_id} is not registered.")

    semantic_policy = route.get("required_semantic_parity_policy")
    if semantic_policy not in semantic_policy_ids:
        errors.append(f"{label}: semantic parity policy {semantic_policy!r} is not registered.")

    for flag in sorted(ROUTE_DISABLED_FLAGS):
        if route.get(flag) is not False:
            errors.append(f"{label}: {flag} must be false.")
    if route.get("live_probes_enabled") is not False:
        errors.append(f"{label}: live_probes_enabled must be false.")

    if status in FUTURE_OR_DEFERRED_STATUSES and route.get("implemented_now") is True:
        errors.append(f"{label}: future/deferred route must not claim current runtime behavior.")
    if status != "implemented_local_runtime" and route.get("dynamic_runtime_required") is True:
        errors.append(f"{label}: dynamic_runtime_required is allowed only for implemented_local_runtime routes.")
    if status == "implemented_local_runtime" and route.get("hosted_public_alpha_status") != "operator_gated":
        errors.append(f"{label}: local runtime routes must keep hosted public alpha operator-gated.")

    path = route.get("canonical_path_pattern")
    if isinstance(path, str):
        for forbidden in sorted(FORBIDDEN_ROUTE_SPLITS):
            if forbidden in path:
                errors.append(f"{label}: forbidden route split appears in canonical_path_pattern.")

    route_safety = route.get("route_safety_class")
    route_text = " ".join(
        [
            str(route_id or ""),
            str(path or ""),
            " ".join(_string_list(route.get("no_goals"))),
            " ".join(_string_list(route.get("notes"))),
        ]
    ).lower()
    dangerous = route_safety == "account_write_admin" or any(
        token in route_text for token in ("account route", "write route", "admin route")
    )
    if dangerous and allowed_hosts & legacy_host_ids:
        errors.append(f"{label}: legacy/read-only hosts must not expose account/write/admin route families.")

    if "files_static" in allowed_hosts and (
        route.get("dynamic_runtime_required") is True or status == "implemented_local_runtime"
    ):
        errors.append(f"{label}: static files host must not expose dynamic runtime route families.")

    if "api_alias" in allowed_hosts and route_id not in API_ALIAS_ALLOWED_ROUTES:
        errors.append(f"{label}: api_alias may expose API-like route families only.")

    if "localhost_relay_future" in allowed_hosts and status not in FUTURE_OR_DEFERRED_STATUSES:
        errors.append(f"{label}: localhost relay exposure must remain future/deferred unless runtime exists.")


def _validate_view(label: str, view: Mapping[str, Any], route_ids: set[str], errors: list[str]) -> None:
    _require_fields(label, view, VIEW_FIELDS, errors)
    if view.get("view_status") not in ALLOWED_STATUSES:
        errors.append(f"{label}: view_status {view.get('view_status')!r} is invalid.")
    canonical_routes = _string_list(view.get("canonical_route_families"))
    if not canonical_routes:
        errors.append(f"{label}: canonical_route_families must be non-empty.")
    for route_id in canonical_routes:
        if route_id not in route_ids:
            errors.append(f"{label}: canonical route family {route_id} is not registered.")


def _validate_representation_bindings(
    source_label: str,
    raw_bindings: Any,
    routes_by_id: Mapping[str, Mapping[str, Any]],
    representation_ids: set[str],
    errors: list[str],
) -> None:
    bindings = _object_list(raw_bindings)
    binding_route_ids = _unique_ids(source_label, bindings, "route_family_id", errors)
    missing = sorted(set(routes_by_id) - binding_route_ids)
    if missing:
        errors.append(f"{source_label}: representation_bindings missing routes {missing}.")
    for binding in bindings:
        label = f"{source_label}: representation binding {binding.get('route_family_id', '<unknown>')}"
        _require_fields(label, binding, BINDING_FIELDS, errors)
        route = routes_by_id.get(binding.get("route_family_id"))
        if route is None:
            errors.append(f"{label}: route_family_id is not registered.")
            continue
        allowed = set(_string_list(binding.get("allowed_representation_profiles")))
        if allowed != set(_string_list(route.get("allowed_representation_profiles"))):
            errors.append(f"{label}: allowed_representation_profiles must match route record.")
        default = binding.get("default_representation_profile")
        if default != route.get("default_representation_profile"):
            errors.append(f"{label}: default_representation_profile must match route record.")
        if default not in representation_ids:
            errors.append(f"{label}: default representation profile is not registered.")


def _validate_host_bindings(
    source_label: str,
    raw_bindings: Any,
    routes_by_id: Mapping[str, Mapping[str, Any]],
    host_ids: set[str],
    errors: list[str],
) -> None:
    bindings = _object_list(raw_bindings)
    binding_route_ids = _unique_ids(source_label, bindings, "route_family_id", errors)
    missing = sorted(set(routes_by_id) - binding_route_ids)
    if missing:
        errors.append(f"{source_label}: host_profile_bindings missing routes {missing}.")
    for binding in bindings:
        label = f"{source_label}: host binding {binding.get('route_family_id', '<unknown>')}"
        _require_fields(label, binding, HOST_BINDING_FIELDS, errors)
        route = routes_by_id.get(binding.get("route_family_id"))
        if route is None:
            errors.append(f"{label}: route_family_id is not registered.")
            continue
        allowed = set(_string_list(binding.get("allowed_host_profiles")))
        if allowed != set(_string_list(route.get("allowed_host_profiles"))):
            errors.append(f"{label}: allowed_host_profiles must match route record.")
        default = binding.get("default_host_profile")
        if default not in allowed:
            errors.append(f"{label}: default_host_profile must be allowed.")
        if default not in host_ids:
            errors.append(f"{label}: default_host_profile is not registered.")
        if binding.get("exposure_status") not in ALLOWED_STATUSES:
            errors.append(f"{label}: exposure_status is invalid.")


def _validate_semantic_bindings(
    source_label: str,
    raw_bindings: Any,
    routes_by_id: Mapping[str, Mapping[str, Any]],
    semantic_policy_ids: set[str],
    errors: list[str],
) -> None:
    bindings = _object_list(raw_bindings)
    binding_route_ids = _unique_ids(source_label, bindings, "route_family_id", errors)
    missing = sorted(set(routes_by_id) - binding_route_ids)
    if missing:
        errors.append(f"{source_label}: semantic_parity_policy_bindings missing routes {missing}.")
    for binding in bindings:
        label = f"{source_label}: semantic binding {binding.get('route_family_id', '<unknown>')}"
        _require_fields(label, binding, SEMANTIC_BINDING_FIELDS, errors)
        route = routes_by_id.get(binding.get("route_family_id"))
        if route is None:
            errors.append(f"{label}: route_family_id is not registered.")
            continue
        policy_id = binding.get("parity_policy_id")
        if policy_id != route.get("required_semantic_parity_policy"):
            errors.append(f"{label}: parity_policy_id must match route record.")
        if policy_id not in semantic_policy_ids:
            errors.append(f"{label}: parity_policy_id is not registered.")
        if binding.get("binding_status") not in {
            "direct",
            "future_deferred",
            "inherited_until_specific_policy",
        }:
            errors.append(f"{label}: binding_status is invalid.")


def _validate_example_coverage(
    source_label: str,
    route_records: Sequence[Mapping[str, Any]],
    errors: list[str],
) -> None:
    statuses = {route.get("route_status") for route in route_records}
    if "implemented_static" not in statuses:
        errors.append(f"{source_label}: example must include an implemented static route family.")
    if "implemented_local_runtime" not in statuses:
        errors.append(f"{source_label}: example must include an implemented local runtime route family.")
    if not any(route.get("route_status") in FUTURE_OR_DEFERRED_STATUSES for route in route_records):
        errors.append(f"{source_label}: example must include a future/deferred route family.")
    covered_representations = set()
    for route in route_records:
        covered_representations.update(_string_list(route.get("allowed_representation_profiles")))
    if not (covered_representations & {"native_card_future", "relay_future", "snapshot_future"}):
        errors.append(f"{source_label}: example must include a future snapshot/relay/native projection.")


def _validate_no_behavior_flags(label: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    for flag in sorted(NO_BEHAVIOR_FLAGS):
        if payload.get(flag) is not True:
            errors.append(f"{label}: {flag} must be true.")


def _validate_public_alpha_policy(label: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    policy = _mapping(payload.get("public_alpha_policy"))
    if policy.get("actual_hosted_public_alpha") != "Track E only":
        errors.append(f"{label}: actual hosted public alpha must remain Track E only.")
    if policy.get("dynamic_hosted_search_active") is not False:
        errors.append(f"{label}: dynamic hosted search must remain inactive.")
    if policy.get("hosted_public_alpha_status") != "operator_gated":
        errors.append(f"{label}: hosted public alpha status must remain operator_gated.")


def _host_ids(
    host_inventory: Mapping[str, Any],
    errors: list[str],
    source_label: str,
) -> tuple[set[str], set[str]]:
    profiles = host_inventory.get("profiles")
    if not isinstance(profiles, list):
        errors.append(f"{source_label}: host_profiles profiles must be a list.")
        return set(), set()
    ids: set[str] = set()
    legacy_ids: set[str] = set()
    for index, profile in enumerate(profiles):
        if not isinstance(profile, Mapping):
            errors.append(f"{source_label}: host_profiles[{index}] must be an object.")
            continue
        host_id = profile.get("host_profile_id")
        if not isinstance(host_id, str):
            continue
        ids.add(host_id)
        if (
            profile.get("legacy_http_compatible") is True
            or profile.get("http_allowed") is True
            or profile.get("host_role") in {"legacy_web", "local_relay_future", "static_files", "status"}
        ):
            legacy_ids.add(host_id)
    return ids, legacy_ids


def _representation_ids(
    representation_inventory: Mapping[str, Any],
    errors: list[str],
    source_label: str,
) -> set[str]:
    profiles = representation_inventory.get("profiles")
    if not isinstance(profiles, list):
        errors.append(f"{source_label}: representation_profiles profiles must be a list.")
        return set()
    ids: set[str] = set()
    for index, profile in enumerate(profiles):
        if not isinstance(profile, Mapping):
            errors.append(f"{source_label}: representation_profiles[{index}] must be an object.")
            continue
        profile_id = profile.get("representation_profile_id")
        if isinstance(profile_id, str):
            ids.add(profile_id)
    return ids


def _semantic_policy_ids(
    semantic_parity_inventory: Mapping[str, Any],
    errors: list[str],
    source_label: str,
) -> set[str]:
    policies = semantic_parity_inventory.get("policies")
    if not isinstance(policies, list):
        errors.append(f"{source_label}: semantic parity policies must be a list.")
        return set()
    ids: set[str] = set()
    for index, policy in enumerate(policies):
        if not isinstance(policy, Mapping):
            errors.append(f"{source_label}: semantic policy[{index}] must be an object.")
            continue
        policy_id = policy.get("parity_policy_id")
        if isinstance(policy_id, str):
            ids.add(policy_id)
    return ids


def _require_fields(
    label: str, payload: Mapping[str, Any], required: set[str], errors: list[str]
) -> None:
    missing = sorted(required - set(payload))
    if missing:
        errors.append(f"{label}: missing required fields {missing}.")


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: required JSON file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {exc.msg}.")
    return None


def _unique_ids(
    label: str,
    records: Sequence[Mapping[str, Any]],
    field_name: str,
    errors: list[str],
) -> set[str]:
    ids: set[str] = set()
    for index, record in enumerate(records):
        value = record.get(field_name)
        if not isinstance(value, str):
            errors.append(f"{label}: record[{index}] {field_name} must be a string.")
            continue
        if value in ids:
            errors.append(f"{label}: duplicate {field_name} {value}.")
        ids.add(value)
    return ids


def _object_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _iter_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    if isinstance(value, str):
        strings.append((path, value))
    elif isinstance(value, Mapping):
        for key, item in sorted(value.items()):
            strings.extend(_iter_strings(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            strings.extend(_iter_strings(item, f"{path}[{index}]"))
    return strings


def _count(payload: Any, field_name: str) -> int:
    if isinstance(payload, Mapping) and isinstance(payload.get(field_name), list):
        return len(payload[field_name])
    return 0


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Route/view/representation matrix validation",
        f"status: {report['status']}",
        f"route_families: {report['route_family_count']}",
        f"view_families: {report['view_family_count']}",
        f"examples: {report['example_count']}",
    ]
    for error in report.get("errors", []):
        lines.append(f"ERROR: {error}")
    for warning in report.get("warnings", []):
        lines.append(f"WARN: {warning}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

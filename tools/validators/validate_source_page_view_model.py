from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/view/pages/source_page.v0.json"
POLICY_INVENTORY = "control/inventory/publication/source_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"
EXAMPLE_PATHS = [
    "examples/view_models/source_page/minimal_source_page_v0.json",
    "examples/view_models/source_page/placeholder_source_page_v0.json",
    "examples/view_models/source_page/recorded_fixture_source_page_v0.json",
    "examples/view_models/source_page/source_gap_page_v0.json",
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
VIEW_MODEL_FIELDS = {
    "schema_version",
    "view_model_id",
    "view_family",
    "route_family",
    "canonical_route",
    "page_title",
    "page_status",
    "source",
    "source_identity",
    "source_type",
    "source_authority_posture",
    "source_policy",
    "source_access_policy",
    "source_capability_summary",
    "source_coverage_summary",
    "source_cache_summary",
    "evidence_ledger_summary",
    "connector_summary",
    "observed_records_summary",
    "example_records",
    "related_packs",
    "related_objects",
    "known_limitations",
    "known_gaps",
    "rights_summary",
    "risk_summary",
    "privacy_summary",
    "action_summary",
    "actions",
    "blocked_actions",
    "candidate_review_state",
    "representation_hints",
    "semantic_requirements",
    "generated_from",
    "no_goals",
    "notes",
}
POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "contract_ref",
    "label",
    "description",
    "status",
    "stability",
    "created_by_slice",
    "canonical_view_family",
    "supported_route_families",
    "required_semantic_parity_policy",
    "allowed_representation_profiles",
    "allowed_source_statuses",
    "allowed_source_kinds",
    "allowed_connector_modes",
    "allowed_access_modes",
    "allowed_coverage_depth_values",
    "allowed_action_names",
    "required_blocked_actions",
    "required_product_boundary_booleans",
    "required_safety_claim_booleans",
    "required_representation_hints",
    "required_semantic_requirements",
    "current_no_goals",
    "future_deferred_fields",
    "notes",
}
SOURCE_IDENTITY_FIELDS = {
    "source_id",
    "source_label",
    "source_slug",
    "canonical_route",
    "source_family",
    "source_kind",
    "source_scope",
    "authority_class",
    "source_status",
    "source_url_or_reference",
    "source_url_public_safe",
    "source_identifiers",
    "source_owner_or_operator",
    "source_contact_policy",
    "source_limitations",
    "notes",
}
SOURCE_POLICY_FIELDS = {
    "source_policy_status",
    "allowed_access_modes",
    "forbidden_access_modes",
    "robots_or_terms_posture",
    "rate_limit_posture",
    "cache_policy",
    "attribution_policy",
    "manual_observation_policy",
    "permission_required",
    "review_required",
    "operator_approval_required",
    "notes",
}
CONNECTOR_FIELDS = {
    "connector_mode",
    "connector_status",
    "implementation_status",
    "live_probe_status",
    "source_sync_status",
    "source_cache_write_status",
    "evidence_candidate_status",
    "health_or_quota_status",
    "circuit_breaker_status",
    "operator_gate_status",
    "notes",
}
PRODUCT_BOUNDARY_FLAGS = {
    "accounts_enabled",
    "downloads_enabled",
    "hosted_backend_claimed",
    "hosted_connector_enabled",
    "live_probes_enabled",
    "source_sync_runtime_enabled",
    "telemetry_enabled",
    "uploads_enabled",
}
FLAG_TO_BLOCKED_ACTION = {
    "accounts_enabled": "account_unavailable",
    "downloads_enabled": "download_unavailable",
    "hosted_backend_claimed": "hosted_backend_unavailable",
    "hosted_connector_enabled": "hosted_backend_unavailable",
    "live_probes_enabled": "live_probe_unavailable",
    "source_sync_runtime_enabled": "source_sync_unavailable",
    "telemetry_enabled": "telemetry_unavailable",
    "uploads_enabled": "upload_unavailable",
}
REQUIRED_BLOCKED_ACTIONS = {
    "account_unavailable",
    "arbitrary_url_fetch_unavailable",
    "crawling_unavailable",
    "download_unavailable",
    "hosted_backend_unavailable",
    "install_unavailable",
    "live_probe_unavailable",
    "malware_safety_unavailable",
    "master_index_mutation_unavailable",
    "rights_clearance_unavailable",
    "scraping_unavailable",
    "source_sync_unavailable",
    "telemetry_unavailable",
    "upload_unavailable",
}
REQUIRED_REPRESENTATION_HINTS = {
    "api_json",
    "file_tree",
    "html32",
    "lite_html",
    "manifest_json",
    "native_card_future",
    "print",
    "relay_future",
    "snapshot_future",
    "standard_html",
    "terminal_future",
    "text",
}
ALLOWED_ACTIONS = {
    "copy_citation_hint",
    "copy_source_id",
    "open_local_runtime_route_future",
    "open_static_demo",
    "view_evidence",
    "view_limitations",
    "view_manual_observation_instructions",
    "view_related_packs",
    "view_related_records",
    "view_source_coverage",
    "view_source_policy",
    "view_source_summary",
}
SOURCE_COMPATIBLE_ROUTE_FAMILIES = {
    "source_detail",
}
ALLOWED_SOURCE_STATUSES = {
    "approval_gated_source",
    "deprecated_source",
    "future_source",
    "implemented_fixture_source",
    "manual_only_source",
    "operator_gated_source",
    "placeholder_source",
    "policy_blocked_source",
    "recorded_fixture_source",
}
NON_LIVE_SOURCE_STATUSES = {
    "future_source",
    "manual_only_source",
    "placeholder_source",
}
ALLOWED_SOURCE_KINDS = {
    "archive_metadata",
    "documentation_site",
    "local_fixture",
    "manual_observation_target",
    "package_registry",
    "placeholder",
    "recorded_fixture",
    "software_repository",
    "source_pack",
    "unknown",
    "web_archive",
}
ALLOWED_CONNECTOR_MODES = {
    "approved_api_future",
    "approved_metadata_probe_future",
    "common_crawl_or_archive_future",
    "disabled",
    "manual_observation_only",
    "no_autonomous_access",
    "operator_gated",
    "permission_needed",
    "policy_blocked",
    "recorded_fixture_only",
    "restricted_demand_signal_only",
    "robots_blocked",
    "sitemap_or_rss_future",
    "static_metadata_only",
    "terms_blocked",
}
ALLOWED_ACCESS_MODES = {
    "approved_api_future",
    "approved_metadata_probe_future",
    "common_crawl_or_archive_future",
    "manual_observation_only",
    "no_autonomous_access",
    "permission_needed",
    "recorded_fixture_only",
    "restricted_demand_signal_only",
    "robots_blocked",
    "sitemap_or_rss_future",
    "static_metadata_only",
    "terms_blocked",
}
ALLOWED_COVERAGE_DEPTHS = {
    "fixture_only",
    "future",
    "gap_report_only",
    "manual_only",
    "partial",
    "placeholder",
    "recorded_fixture",
    "static_metadata_only",
    "unknown",
}
REQUIRED_SAFETY_CLAIM_BOOLEANS = {
    "authorized_bulk_access_claimed",
    "authorized_downloads_claimed",
    "legal_mirroring_claimed",
    "malware_safety_claimed",
    "rights_clearance_claimed",
    "safe_execution_claimed",
    "unrestricted_crawling_claimed",
}
REQUIRED_SEMANTIC_REQUIREMENTS = {
    "actions_and_blocked_actions_preserved",
    "canonical_source_identity_preserved",
    "candidate_review_state_preserved",
    "connector_status_preserved",
    "limitations_and_gaps_visible",
    "no_live_source_or_bulk_access_claims",
    "rights_risk_privacy_posture_preserved",
    "source_access_gates_preserved",
    "source_cache_evidence_ledger_posture_preserved",
    "source_capability_coverage_posture_preserved",
    "source_observation_not_truth_preserved",
    "source_policy_posture_preserved",
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
        description="Validate Eureka SourcePage view-model schema, policy, and examples."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_source_page_view_model(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_source_page_view_model(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors, root)
    if isinstance(contract, Mapping):
        _validate_schema(CONTRACT_PATH, contract, errors)

    policy = _load_json(root / POLICY_INVENTORY, errors, root)
    representations = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY, errors, root)
    route_matrix = _load_json(root / ROUTE_MATRIX_INVENTORY, errors, root)
    examples: list[Mapping[str, Any]] = []
    for relative in EXAMPLE_PATHS:
        payload = _load_json(root / relative, errors, root)
        if isinstance(payload, Mapping):
            examples.append(payload)

    if (
        isinstance(policy, Mapping)
        and isinstance(representations, Mapping)
        and isinstance(semantic, Mapping)
        and isinstance(route_matrix, Mapping)
    ):
        errors.extend(
            validate_payloads(
                policy,
                representations,
                semantic,
                route_matrix,
                examples,
                source_label="source_page_view_model",
            )
        )

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_source_page_view_model",
        "schema_version": SCHEMA_VERSION,
        "contract_checked": CONTRACT_PATH,
        "policy_checked": POLICY_INVENTORY,
        "representation_inventory_checked": REPRESENTATION_INVENTORY,
        "semantic_parity_inventory_checked": SEMANTIC_PARITY_INVENTORY,
        "route_matrix_checked": ROUTE_MATRIX_INVENTORY,
        "examples_checked": sorted(EXAMPLE_PATHS),
        "example_count": len(examples),
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }


def validate_payloads(
    policy: Mapping[str, Any],
    representation_inventory: Mapping[str, Any],
    semantic_inventory: Mapping[str, Any],
    route_matrix: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]],
    *,
    source_label: str,
) -> list[str]:
    errors: list[str] = []
    representation_ids = _representation_ids(representation_inventory)
    semantic_policy_ids = _semantic_policy_ids(semantic_inventory)
    route_records = _route_records(route_matrix)

    errors.extend(_validate_policy(policy, representation_ids, semantic_policy_ids, route_records))

    policy_route_families = set(_string_items(policy.get("supported_route_families")))
    policy_representations = set(_string_items(policy.get("allowed_representation_profiles")))
    policy_source_statuses = set(_string_items(policy.get("allowed_source_statuses")))
    policy_source_kinds = set(_string_items(policy.get("allowed_source_kinds")))
    policy_connector_modes = set(_string_items(policy.get("allowed_connector_modes")))
    policy_access_modes = set(_string_items(policy.get("allowed_access_modes")))
    policy_coverage_depths = set(_string_items(policy.get("allowed_coverage_depth_values")))
    policy_actions = set(_string_items(policy.get("allowed_action_names")))
    policy_required_hints = set(_string_items(policy.get("required_representation_hints")))
    policy_required_semantics = set(_string_items(policy.get("required_semantic_requirements")))
    policy_blocked = set(_string_items(policy.get("required_blocked_actions")))
    semantic_policy_ref = policy.get("required_semantic_parity_policy")

    for index, example in enumerate(examples):
        label = str(example.get("view_model_id") or f"example[{index}]")
        errors.extend(
            _validate_example(
                label,
                example,
                policy_route_families,
                policy_representations,
                policy_source_statuses,
                policy_source_kinds,
                policy_connector_modes,
                policy_access_modes,
                policy_coverage_depths,
                policy_actions,
                policy_required_hints,
                policy_required_semantics,
                policy_blocked,
                semantic_policy_ref if isinstance(semantic_policy_ref, str) else "",
                representation_ids,
                route_records,
            )
        )

    if not examples:
        errors.append(f"{source_label}: at least one SourcePageView example is required")

    return sorted(errors)


def _validate_schema(path: str, contract: Mapping[str, Any], errors: list[str]) -> None:
    missing = REQUIRED_SCHEMA_FIELDS - set(contract)
    if missing:
        errors.append(f"{path}: missing schema fields {sorted(missing)}")
    if contract.get("type") != "object":
        errors.append(f"{path}: schema type must be object")
    if contract.get("properties", {}).get("schema_version", {}).get("const") != SCHEMA_VERSION:
        errors.append(f"{path}: schema_version const must be {SCHEMA_VERSION}")
    required = set(_string_items(contract.get("required")))
    missing_required = VIEW_MODEL_FIELDS - required
    if missing_required:
        errors.append(f"{path}: required list missing {sorted(missing_required)}")
    properties = contract.get("properties")
    if isinstance(properties, Mapping):
        missing_properties = VIEW_MODEL_FIELDS - set(properties)
        if missing_properties:
            errors.append(f"{path}: properties missing {sorted(missing_properties)}")
    else:
        errors.append(f"{path}: properties must be an object")


def _validate_policy(
    policy: Mapping[str, Any],
    representation_ids: set[str],
    semantic_policy_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = POLICY_FIELDS - set(policy)
    if missing:
        errors.append(f"{POLICY_INVENTORY}: missing policy fields {sorted(missing)}")
    if policy.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{POLICY_INVENTORY}: schema_version must be {SCHEMA_VERSION}")
    if policy.get("contract_ref") != CONTRACT_PATH:
        errors.append(f"{POLICY_INVENTORY}: contract_ref must be {CONTRACT_PATH}")
    if policy.get("canonical_view_family") != "SourcePageView":
        errors.append(f"{POLICY_INVENTORY}: canonical_view_family must be SourcePageView")

    supported_routes = set(_string_items(policy.get("supported_route_families")))
    missing_routes = supported_routes - set(route_records)
    if missing_routes:
        errors.append(f"{POLICY_INVENTORY}: unsupported route family refs {sorted(missing_routes)}")
    non_source_routes = supported_routes - SOURCE_COMPATIBLE_ROUTE_FAMILIES
    if non_source_routes:
        errors.append(
            f"{POLICY_INVENTORY}: route families are not source-page-compatible {sorted(non_source_routes)}"
        )
    for route_id in sorted(supported_routes & set(route_records)):
        route = route_records[route_id]
        if route.get("canonical_view_family") != "SourcePageView":
            errors.append(f"{POLICY_INVENTORY}: {route_id} does not bind to SourcePageView")
    if "source_detail" not in supported_routes:
        errors.append(f"{POLICY_INVENTORY}: supported_route_families must include source_detail")

    policy_representations = set(_string_items(policy.get("allowed_representation_profiles")))
    missing_representations = policy_representations - representation_ids
    if missing_representations:
        errors.append(
            f"{POLICY_INVENTORY}: unknown representation profile refs {sorted(missing_representations)}"
        )
    if not REQUIRED_REPRESENTATION_HINTS <= policy_representations:
        errors.append(
            f"{POLICY_INVENTORY}: allowed_representation_profiles missing {sorted(REQUIRED_REPRESENTATION_HINTS - policy_representations)}"
        )

    required_hints = set(_string_items(policy.get("required_representation_hints")))
    if not REQUIRED_REPRESENTATION_HINTS <= required_hints:
        errors.append(
            f"{POLICY_INVENTORY}: required_representation_hints missing {sorted(REQUIRED_REPRESENTATION_HINTS - required_hints)}"
        )

    semantic_ref = policy.get("required_semantic_parity_policy")
    if semantic_ref not in semantic_policy_ids:
        errors.append(f"{POLICY_INVENTORY}: semantic parity policy ref {semantic_ref!r} does not exist")

    source_statuses = set(_string_items(policy.get("allowed_source_statuses")))
    if not ALLOWED_SOURCE_STATUSES <= source_statuses:
        errors.append(
            f"{POLICY_INVENTORY}: allowed_source_statuses missing {sorted(ALLOWED_SOURCE_STATUSES - source_statuses)}"
        )
    source_kinds = set(_string_items(policy.get("allowed_source_kinds")))
    if not ALLOWED_SOURCE_KINDS <= source_kinds:
        errors.append(f"{POLICY_INVENTORY}: allowed_source_kinds missing {sorted(ALLOWED_SOURCE_KINDS - source_kinds)}")
    connector_modes = set(_string_items(policy.get("allowed_connector_modes")))
    if not ALLOWED_CONNECTOR_MODES <= connector_modes:
        errors.append(
            f"{POLICY_INVENTORY}: allowed_connector_modes missing {sorted(ALLOWED_CONNECTOR_MODES - connector_modes)}"
        )
    access_modes = set(_string_items(policy.get("allowed_access_modes")))
    if not ALLOWED_ACCESS_MODES <= access_modes:
        errors.append(f"{POLICY_INVENTORY}: allowed_access_modes missing {sorted(ALLOWED_ACCESS_MODES - access_modes)}")
    coverage_depths = set(_string_items(policy.get("allowed_coverage_depth_values")))
    if not ALLOWED_COVERAGE_DEPTHS <= coverage_depths:
        errors.append(
            f"{POLICY_INVENTORY}: allowed_coverage_depth_values missing {sorted(ALLOWED_COVERAGE_DEPTHS - coverage_depths)}"
        )
    actions = set(_string_items(policy.get("allowed_action_names")))
    if not ALLOWED_ACTIONS <= actions:
        errors.append(f"{POLICY_INVENTORY}: allowed_action_names missing {sorted(ALLOWED_ACTIONS - actions)}")
    blocked = set(_string_items(policy.get("required_blocked_actions")))
    if not REQUIRED_BLOCKED_ACTIONS <= blocked:
        errors.append(f"{POLICY_INVENTORY}: required_blocked_actions missing {sorted(REQUIRED_BLOCKED_ACTIONS - blocked)}")
    flags = set(_string_items(policy.get("required_product_boundary_booleans")))
    if not PRODUCT_BOUNDARY_FLAGS <= flags:
        errors.append(
            f"{POLICY_INVENTORY}: required_product_boundary_booleans missing {sorted(PRODUCT_BOUNDARY_FLAGS - flags)}"
        )
    claim_flags = set(_string_items(policy.get("required_safety_claim_booleans")))
    if not REQUIRED_SAFETY_CLAIM_BOOLEANS <= claim_flags:
        errors.append(
            f"{POLICY_INVENTORY}: required_safety_claim_booleans missing {sorted(REQUIRED_SAFETY_CLAIM_BOOLEANS - claim_flags)}"
        )
    semantic_requirements = set(_string_items(policy.get("required_semantic_requirements")))
    if not REQUIRED_SEMANTIC_REQUIREMENTS <= semantic_requirements:
        errors.append(
            f"{POLICY_INVENTORY}: required_semantic_requirements missing {sorted(REQUIRED_SEMANTIC_REQUIREMENTS - semantic_requirements)}"
        )
    return errors


def _validate_example(
    label: str,
    example: Mapping[str, Any],
    policy_route_families: set[str],
    policy_representations: set[str],
    policy_source_statuses: set[str],
    policy_source_kinds: set[str],
    policy_connector_modes: set[str],
    policy_access_modes: set[str],
    policy_coverage_depths: set[str],
    policy_actions: set[str],
    policy_required_hints: set[str],
    policy_required_semantics: set[str],
    policy_blocked: set[str],
    semantic_policy_ref: str,
    representation_ids: set[str],
    route_records: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    missing = VIEW_MODEL_FIELDS - set(example)
    if missing:
        errors.append(f"{label}: missing required top-level fields {sorted(missing)}")
        return errors

    if example.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if example.get("view_family") != "SourcePageView":
        errors.append(f"{label}: view_family must be SourcePageView")

    route_family = example.get("route_family")
    if route_family not in policy_route_families:
        errors.append(f"{label}: route_family {route_family!r} is not allowed by policy")
    if route_family not in route_records:
        errors.append(f"{label}: route_family {route_family!r} is not in route matrix")
    elif route_records[route_family].get("canonical_view_family") != "SourcePageView":
        errors.append(f"{label}: route_family {route_family!r} does not bind to SourcePageView")

    blocked_actions = _blocked_action_ids(example.get("blocked_actions"))
    connector = _mapping(example.get("connector_summary"))
    errors.extend(_validate_connector_flags(label, connector, blocked_actions))

    missing_required_blocked = (policy_blocked | REQUIRED_BLOCKED_ACTIONS) - blocked_actions
    if missing_required_blocked:
        errors.append(f"{label}: blocked_actions missing {sorted(missing_required_blocked)}")

    identity = example.get("source_identity")
    source_status = ""
    if not isinstance(identity, Mapping):
        errors.append(f"{label}: source_identity must be an object")
    else:
        missing_identity = SOURCE_IDENTITY_FIELDS - set(identity)
        if missing_identity:
            errors.append(f"{label}: source_identity missing {sorted(missing_identity)}")
        if not identity.get("source_id"):
            errors.append(f"{label}: canonical source identity source_id is required")
        if not identity.get("canonical_route"):
            errors.append(f"{label}: canonical source identity canonical_route is required")
        source_status = str(identity.get("source_status") or "")
        if source_status not in policy_source_statuses:
            errors.append(f"{label}: source_status {identity.get('source_status')!r} is not allowed")
        if identity.get("source_kind") not in policy_source_kinds:
            errors.append(f"{label}: source_kind {identity.get('source_kind')!r} is not allowed")

    source_policy = example.get("source_policy")
    if not isinstance(source_policy, Mapping):
        errors.append(f"{label}: source_policy must be an object")
    else:
        missing_policy_fields = SOURCE_POLICY_FIELDS - set(source_policy)
        if missing_policy_fields:
            errors.append(f"{label}: source_policy missing {sorted(missing_policy_fields)}")
        errors.extend(
            _validate_access_modes(
                label,
                "source_policy.allowed_access_modes",
                source_policy.get("allowed_access_modes"),
                policy_access_modes,
            )
        )
        errors.extend(
            _validate_access_modes(
                label,
                "source_policy.forbidden_access_modes",
                source_policy.get("forbidden_access_modes"),
                policy_access_modes,
            )
        )

    source_access = example.get("source_access_policy")
    if not isinstance(source_access, Mapping):
        errors.append(f"{label}: source_access_policy must be an object")
    else:
        errors.extend(
            _validate_access_modes(
                label,
                "source_access_policy.allowed_access_modes",
                source_access.get("allowed_access_modes"),
                policy_access_modes,
            )
        )
        errors.extend(
            _validate_access_modes(
                label,
                "source_access_policy.forbidden_access_modes",
                source_access.get("forbidden_access_modes"),
                policy_access_modes,
            )
        )

    connector_mode = connector.get("connector_mode")
    if connector_mode not in policy_connector_modes:
        errors.append(f"{label}: connector_mode {connector_mode!r} is not allowed")
    missing_connector_fields = CONNECTOR_FIELDS - set(connector)
    if missing_connector_fields:
        errors.append(f"{label}: connector_summary missing {sorted(missing_connector_fields)}")

    coverage = _mapping(example.get("source_capability_summary"))
    coverage_depth = coverage.get("coverage_depth")
    if coverage_depth not in policy_coverage_depths:
        errors.append(f"{label}: coverage_depth {coverage_depth!r} is not allowed")
    coverage_summary = _mapping(example.get("source_coverage_summary"))
    summary_depth = coverage_summary.get("coverage_depth")
    if summary_depth not in policy_coverage_depths:
        errors.append(f"{label}: source_coverage_summary.coverage_depth {summary_depth!r} is not allowed")
    if coverage_summary.get("coverage_not_exhaustive") is not True:
        errors.append(f"{label}: source coverage must be explicitly non-exhaustive")

    errors.extend(_validate_truth_boundaries(label, example, source_status, connector))
    errors.extend(_validate_actions(label, example, policy_actions))
    errors.extend(_validate_hints(label, example, representation_ids, policy_representations, policy_required_hints))
    errors.extend(_validate_semantics(label, example, policy_required_semantics))

    generated_from = example.get("generated_from")
    if not isinstance(generated_from, Mapping):
        errors.append(f"{label}: generated_from must be an object")
    elif generated_from.get("semantic_parity_policy") != semantic_policy_ref:
        errors.append(f"{label}: generated_from semantic_parity_policy must be {semantic_policy_ref!r}")

    raw = json.dumps(example, sort_keys=True)
    for pattern in UNSAFE_EXAMPLE_PATTERNS:
        if pattern.search(raw):
            errors.append(f"{label}: example contains unsafe/private pattern {pattern.pattern}")

    return errors


def _validate_connector_flags(
    label: str,
    connector: Mapping[str, Any],
    blocked_actions: set[str],
) -> list[str]:
    errors: list[str] = []
    if not connector:
        return [f"{label}: connector_summary must be an object"]
    missing_flags = PRODUCT_BOUNDARY_FLAGS - set(connector)
    if missing_flags:
        errors.append(f"{label}: connector_summary missing {sorted(missing_flags)}")
    for flag in sorted(PRODUCT_BOUNDARY_FLAGS):
        if connector.get(flag) is not False:
            errors.append(f"{label}: {flag} must be false for current examples")
        blocked_action = FLAG_TO_BLOCKED_ACTION[flag]
        if connector.get(flag) is False and blocked_action not in blocked_actions:
            errors.append(f"{label}: missing blocked action {blocked_action} for false {flag}")
    return errors


def _validate_access_modes(
    label: str,
    field_name: str,
    value: Any,
    policy_access_modes: set[str],
) -> list[str]:
    modes = set(_string_items(value))
    if not modes:
        return [f"{label}: {field_name} must be non-empty"]
    unknown = modes - policy_access_modes
    if unknown:
        return [f"{label}: {field_name} contains unknown access modes {sorted(unknown)}"]
    return []


def _validate_truth_boundaries(
    label: str,
    example: Mapping[str, Any],
    source_status: str,
    connector: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    connector_mode = str(connector.get("connector_mode") or "")
    connector_status = str(connector.get("connector_status") or "")
    implementation_status = str(connector.get("implementation_status") or "")

    if source_status in NON_LIVE_SOURCE_STATUSES:
        if connector.get("hosted_connector_enabled") is not False:
            errors.append(f"{label}: placeholder/future/manual-only source must not enable hosted connector")
        if "live" in connector_mode or connector_status == "live_connector" or implementation_status == "live":
            errors.append(f"{label}: placeholder/future/manual-only source must not be marked live")

    if source_status == "recorded_fixture_source":
        if connector_mode != "recorded_fixture_only":
            errors.append(f"{label}: recorded fixture source must use recorded_fixture_only connector mode")
        if connector_status == "live_connector" or implementation_status == "live":
            errors.append(f"{label}: recorded fixture source must not be marked live connector")

    source_cache = _mapping(example.get("source_cache_summary"))
    if source_cache.get("source_cache_record_accepted_as_truth") is not False:
        errors.append(f"{label}: source cache record must not be marked accepted truth")
    if source_cache.get("source_observation_accepted_as_truth") is not False:
        errors.append(f"{label}: source observation must not be marked accepted truth")

    observed = _mapping(example.get("observed_records_summary"))
    if observed.get("source_observation_accepted_as_truth") is not False:
        errors.append(f"{label}: source observation must not be marked accepted truth")
    if observed.get("manual_observation_placeholder") is True:
        if observed.get("manual_observation_completed") is not False:
            errors.append(f"{label}: manual observation placeholder must not be marked completed")
        if observed.get("completed_external_baseline_claimed") is not False:
            errors.append(f"{label}: manual observation placeholder must not claim completed external baseline")

    evidence = _mapping(example.get("evidence_ledger_summary"))
    if evidence.get("evidence_candidate_accepted_as_truth") is not False:
        errors.append(f"{label}: evidence candidate must not be marked accepted truth")
    if evidence.get("ai_draft_marked_evidence_truth") is not False:
        errors.append(f"{label}: AI draft must not be marked evidence truth")

    source_access = _mapping(example.get("source_access_policy"))
    if source_access.get("unrestricted_crawling_claimed") is not False:
        errors.append(f"{label}: unrestricted crawling must not be claimed")
    if source_access.get("authorized_bulk_access_claimed") is not False:
        errors.append(f"{label}: authorized bulk access must not be claimed")
    if source_access.get("legal_mirroring_claimed") is not False:
        errors.append(f"{label}: legal mirroring must not be claimed")

    rights = _mapping(example.get("rights_summary"))
    if rights.get("rights_clearance_claimed") is not False:
        errors.append(f"{label}: rights clearance must not be claimed")
    if rights.get("legal_mirroring_claimed") is not False:
        errors.append(f"{label}: legal mirroring must not be claimed")
    if rights.get("authorized_bulk_access_claimed") is not False:
        errors.append(f"{label}: authorized bulk access must not be claimed")

    risk = _mapping(example.get("risk_summary"))
    if risk.get("malware_safety_claimed") is not False:
        errors.append(f"{label}: malware safety must not be claimed")
    if risk.get("safe_execution_claimed") is not False:
        errors.append(f"{label}: safe execution must not be claimed")

    action_summary = _mapping(example.get("action_summary"))
    for key in (
        "downloads_enabled",
        "installs_enabled",
        "execution_enabled",
        "source_sync_enabled",
        "authorized_downloads_claimed",
        "authorized_bulk_access_claimed",
    ):
        if action_summary.get(key) is not False:
            errors.append(f"{label}: action_summary.{key} must be false")

    return errors


def _validate_actions(label: str, example: Mapping[str, Any], policy_actions: set[str]) -> list[str]:
    errors: list[str] = []
    actions = _action_ids(example.get("actions"))
    unknown_actions = actions - policy_actions
    if unknown_actions:
        errors.append(f"{label}: actions contain unknown action ids {sorted(unknown_actions)}")
    action_summary = _mapping(example.get("action_summary"))
    summary_actions = set(_string_items(action_summary.get("allowed_actions")))
    unknown_summary_actions = summary_actions - policy_actions
    if unknown_summary_actions:
        errors.append(f"{label}: action_summary contains unknown actions {sorted(unknown_summary_actions)}")
    summary_blocked = set(_string_items(action_summary.get("blocked_actions")))
    if not REQUIRED_BLOCKED_ACTIONS <= summary_blocked:
        errors.append(f"{label}: action_summary.blocked_actions missing {sorted(REQUIRED_BLOCKED_ACTIONS - summary_blocked)}")
    return errors


def _validate_hints(
    label: str,
    example: Mapping[str, Any],
    representation_ids: set[str],
    policy_representations: set[str],
    policy_required_hints: set[str],
) -> list[str]:
    errors: list[str] = []
    hints = example.get("representation_hints")
    if not isinstance(hints, Mapping):
        return [f"{label}: representation_hints must be an object"]
    hint_ids = set(hints)
    unknown_hints = hint_ids - representation_ids
    if unknown_hints:
        errors.append(f"{label}: representation_hints reference unknown profiles {sorted(unknown_hints)}")
    missing_hints = (policy_required_hints | REQUIRED_REPRESENTATION_HINTS) - hint_ids
    if missing_hints:
        errors.append(f"{label}: representation_hints missing {sorted(missing_hints)}")
    disallowed_hints = hint_ids - policy_representations
    if disallowed_hints:
        errors.append(f"{label}: representation_hints include profiles outside policy {sorted(disallowed_hints)}")
    for hint_id in sorted(hint_ids):
        hint = hints[hint_id]
        if isinstance(hint, Mapping):
            if hint.get("semantic_meaning_changes_allowed") is not False:
                errors.append(f"{label}: {hint_id} must not allow semantic meaning changes")
        else:
            errors.append(f"{label}: representation hint {hint_id} must be an object")
    return errors


def _validate_semantics(
    label: str,
    example: Mapping[str, Any],
    policy_required_semantics: set[str],
) -> list[str]:
    semantics = set(_string_items(example.get("semantic_requirements")))
    errors: list[str] = []
    if not semantics:
        errors.append(f"{label}: semantic_requirements must be non-empty")
    missing = (policy_required_semantics | REQUIRED_SEMANTIC_REQUIREMENTS) - semantics
    if missing:
        errors.append(f"{label}: semantic_requirements missing {sorted(missing)}")
    return errors


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


def _action_ids(actions: Any) -> set[str]:
    if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
        return set()
    return {
        action["action_id"]
        for action in actions
        if isinstance(action, Mapping) and isinstance(action.get("action_id"), str)
    }


def _blocked_action_ids(actions: Any) -> set[str]:
    return _action_ids(actions)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_source_page_view_model: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"contract: {report['contract_checked']}",
        f"policy: {report['policy_checked']}",
        f"examples: {report['example_count']}",
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

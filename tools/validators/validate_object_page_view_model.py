from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/view/pages/object_page.v0.json"
POLICY_INVENTORY = "control/inventory/publication/object_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"
EXAMPLE_PATHS = [
    "examples/view_models/object_page/candidate_object_page_v0.json",
    "examples/view_models/object_page/member_object_page_v0.json",
    "examples/view_models/object_page/minimal_object_page_v0.json",
    "examples/view_models/object_page/software_object_page_v0.json",
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
    "object",
    "object_identity",
    "object_state",
    "public_runtime_posture",
    "representation_summary",
    "file_and_member_summary",
    "source_summary",
    "evidence_summary",
    "provenance_summary",
    "compatibility_summary",
    "rights_summary",
    "risk_summary",
    "action_summary",
    "actions",
    "blocked_actions",
    "related_records",
    "candidate_review_state",
    "absence_or_gap_summary",
    "limitations",
    "warnings",
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
    "allowed_object_states",
    "allowed_object_types",
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
IDENTITY_FIELDS = {
    "object_id",
    "object_type",
    "identity_state",
    "title",
    "subtitle",
    "aliases",
    "canonical_route",
    "stable_ids",
    "external_identifiers",
    "source_specific_identifiers",
    "identity_confidence",
    "identity_limitations",
    "notes",
}
OBJECT_STATE_FIELDS = {
    "version",
    "release_date",
    "platform",
    "architecture",
    "format",
    "language",
    "edition",
    "capture_date",
    "temporal_state",
    "state_confidence",
    "state_limitations",
    "notes",
}
PUBLIC_RUNTIME_FLAGS = {
    "accounts_enabled",
    "downloads_enabled",
    "hosted_backend_claimed",
    "live_probes_enabled",
    "telemetry_enabled",
    "uploads_enabled",
}
FLAG_TO_BLOCKED_ACTION = {
    "accounts_enabled": "account_unavailable",
    "downloads_enabled": "download_unavailable",
    "hosted_backend_claimed": "hosted_backend_unavailable",
    "live_probes_enabled": "live_probe_unavailable",
    "telemetry_enabled": "telemetry_unavailable",
    "uploads_enabled": "upload_unavailable",
}
REQUIRED_BLOCKED_ACTIONS = {
    "account_unavailable",
    "download_unavailable",
    "execute_unavailable",
    "hosted_backend_unavailable",
    "install_unavailable",
    "live_probe_unavailable",
    "malware_safety_unavailable",
    "rights_clearance_unavailable",
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
    "compare_versions",
    "copy_canonical_id",
    "copy_citation_hint",
    "export_manifest_future",
    "open_relay_future",
    "open_snapshot_future",
    "open_static_demo",
    "view_evidence",
    "view_members",
    "view_parent",
    "view_source",
}
OBJECT_COMPATIBLE_ROUTE_FAMILIES = {
    "object_page_future",
}
ALLOWED_OBJECT_STATES = {
    "absence_unknown_placeholder",
    "candidate_object",
    "known_object",
    "member_inner_object",
    "provisional_object",
    "source_observed_object",
}
ALLOWED_OBJECT_TYPES = {
    "article_or_scan_segment",
    "collection",
    "compatibility_evidence",
    "documentation",
    "driver",
    "file_inside_container",
    "package_metadata",
    "software",
    "software_version",
    "source_code_release",
    "source_identity",
    "unknown",
    "web_capture",
}
REQUIRED_SAFETY_CLAIM_BOOLEANS = {
    "authorized_downloads_claimed",
    "malware_safety_claimed",
    "rights_clearance_claimed",
    "safe_execution_claimed",
    "verified_installability_claimed",
}
REQUIRED_SEMANTIC_REQUIREMENTS = {
    "actions_and_blocked_actions_preserved",
    "canonical_object_identity_preserved",
    "candidate_review_state_preserved",
    "compatibility_posture_preserved",
    "limitations_and_gaps_visible",
    "member_parent_lineage_preserved",
    "object_state_version_unknowns_preserved",
    "provenance_or_lineage_preserved",
    "representation_and_member_posture_preserved",
    "rights_and_risk_posture_preserved",
    "source_evidence_status_meaning_preserved",
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
        description="Validate Eureka ObjectPage view-model schema, policy, and examples."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_object_page_view_model(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_object_page_view_model(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
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
                source_label="object_page_view_model",
            )
        )

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_object_page_view_model",
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
    policy_object_states = set(_string_items(policy.get("allowed_object_states")))
    policy_object_types = set(_string_items(policy.get("allowed_object_types")))
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
                policy_object_states,
                policy_object_types,
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
        errors.append(f"{source_label}: at least one ObjectPageView example is required")

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
    if policy.get("canonical_view_family") != "ObjectPageView":
        errors.append(f"{POLICY_INVENTORY}: canonical_view_family must be ObjectPageView")

    supported_routes = set(_string_items(policy.get("supported_route_families")))
    missing_routes = supported_routes - set(route_records)
    if missing_routes:
        errors.append(f"{POLICY_INVENTORY}: unsupported route family refs {sorted(missing_routes)}")
    non_object_routes = supported_routes - OBJECT_COMPATIBLE_ROUTE_FAMILIES
    if non_object_routes:
        errors.append(
            f"{POLICY_INVENTORY}: route families are not object-page-compatible {sorted(non_object_routes)}"
        )
    for route_id in sorted(supported_routes & set(route_records)):
        route = route_records[route_id]
        if route.get("canonical_view_family") != "ObjectPageView":
            errors.append(f"{POLICY_INVENTORY}: {route_id} does not bind to ObjectPageView")
    if "object_page_future" not in supported_routes:
        errors.append(f"{POLICY_INVENTORY}: supported_route_families must include object_page_future")

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

    object_states = set(_string_items(policy.get("allowed_object_states")))
    if not ALLOWED_OBJECT_STATES <= object_states:
        errors.append(f"{POLICY_INVENTORY}: allowed_object_states missing {sorted(ALLOWED_OBJECT_STATES - object_states)}")
    object_types = set(_string_items(policy.get("allowed_object_types")))
    if not ALLOWED_OBJECT_TYPES <= object_types:
        errors.append(f"{POLICY_INVENTORY}: allowed_object_types missing {sorted(ALLOWED_OBJECT_TYPES - object_types)}")
    actions = set(_string_items(policy.get("allowed_action_names")))
    if not ALLOWED_ACTIONS <= actions:
        errors.append(f"{POLICY_INVENTORY}: allowed_action_names missing {sorted(ALLOWED_ACTIONS - actions)}")
    blocked = set(_string_items(policy.get("required_blocked_actions")))
    if not REQUIRED_BLOCKED_ACTIONS <= blocked:
        errors.append(f"{POLICY_INVENTORY}: required_blocked_actions missing {sorted(REQUIRED_BLOCKED_ACTIONS - blocked)}")
    flags = set(_string_items(policy.get("required_product_boundary_booleans")))
    if not PUBLIC_RUNTIME_FLAGS <= flags:
        errors.append(
            f"{POLICY_INVENTORY}: required_product_boundary_booleans missing {sorted(PUBLIC_RUNTIME_FLAGS - flags)}"
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
    policy_object_states: set[str],
    policy_object_types: set[str],
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
    if example.get("view_family") != "ObjectPageView":
        errors.append(f"{label}: view_family must be ObjectPageView")

    route_family = example.get("route_family")
    if route_family not in policy_route_families:
        errors.append(f"{label}: route_family {route_family!r} is not allowed by policy")
    if route_family not in route_records:
        errors.append(f"{label}: route_family {route_family!r} is not in route matrix")
    elif route_records[route_family].get("canonical_view_family") != "ObjectPageView":
        errors.append(f"{label}: route_family {route_family!r} does not bind to ObjectPageView")

    blocked_actions = _blocked_action_ids(example.get("blocked_actions"))
    runtime = example.get("public_runtime_posture")
    if not isinstance(runtime, Mapping):
        errors.append(f"{label}: public_runtime_posture must be an object")
    else:
        missing_flags = PUBLIC_RUNTIME_FLAGS - set(runtime)
        if missing_flags:
            errors.append(f"{label}: public_runtime_posture missing {sorted(missing_flags)}")
        for flag in sorted(PUBLIC_RUNTIME_FLAGS):
            if runtime.get(flag) is not False:
                errors.append(f"{label}: {flag} must be false for current examples")
            blocked_action = FLAG_TO_BLOCKED_ACTION[flag]
            if runtime.get(flag) is False and blocked_action not in blocked_actions:
                errors.append(f"{label}: missing blocked action {blocked_action} for false {flag}")

    missing_required_blocked = (policy_blocked | REQUIRED_BLOCKED_ACTIONS) - blocked_actions
    if missing_required_blocked:
        errors.append(f"{label}: blocked_actions missing {sorted(missing_required_blocked)}")

    identity = example.get("object_identity")
    if not isinstance(identity, Mapping):
        errors.append(f"{label}: object_identity must be an object")
    else:
        missing_identity = IDENTITY_FIELDS - set(identity)
        if missing_identity:
            errors.append(f"{label}: object_identity missing {sorted(missing_identity)}")
        if not identity.get("object_id"):
            errors.append(f"{label}: canonical object identity object_id is required")
        if identity.get("identity_state") not in policy_object_states:
            errors.append(f"{label}: identity_state {identity.get('identity_state')!r} is not allowed")
        if identity.get("object_type") not in policy_object_types:
            errors.append(f"{label}: object_type {identity.get('object_type')!r} is not allowed")

    object_state = example.get("object_state")
    if not isinstance(object_state, Mapping):
        errors.append(f"{label}: object_state must be an object")
    else:
        missing_state = OBJECT_STATE_FIELDS - set(object_state)
        if missing_state:
            errors.append(f"{label}: object_state missing {sorted(missing_state)}")

    errors.extend(_validate_truth_boundaries(label, example))
    errors.extend(_validate_member_lineage(label, example))
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


def _validate_truth_boundaries(label: str, example: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = _mapping(example.get("object_identity"))
    review = _mapping(example.get("candidate_review_state"))
    identity_state = identity.get("identity_state")
    if identity_state in {"candidate_object", "provisional_object"}:
        if review.get("review_status") == "verified":
            errors.append(f"{label}: candidate/provisional object must not be marked verified")
        if review.get("candidate_or_provisional_not_verified") is not True:
            errors.append(f"{label}: candidate/provisional object must record not-verified state")
        if identity.get("identity_confidence") == "reviewed":
            errors.append(f"{label}: candidate/provisional object must not use reviewed identity confidence")

    source = _mapping(example.get("source_summary"))
    if source.get("source_observation_accepted_as_truth") is not False:
        errors.append(f"{label}: source observation must not be marked accepted truth")

    evidence = _mapping(example.get("evidence_summary"))
    if evidence.get("evidence_candidate_accepted_as_truth") is not False:
        errors.append(f"{label}: evidence candidate must not be marked accepted truth")
    if evidence.get("ai_draft_marked_evidence_truth") is not False:
        errors.append(f"{label}: AI draft must not be marked evidence truth")

    compatibility = _mapping(example.get("compatibility_summary"))
    if compatibility.get("verified_installability_claimed") is not False:
        errors.append(f"{label}: verified installability must not be claimed")
    rights = _mapping(example.get("rights_summary"))
    if rights.get("rights_clearance_claimed") is not False:
        errors.append(f"{label}: rights clearance must not be claimed")
    risk = _mapping(example.get("risk_summary"))
    if risk.get("malware_safety_claimed") is not False:
        errors.append(f"{label}: malware safety must not be claimed")
    if risk.get("safe_execution_claimed") is not False:
        errors.append(f"{label}: safe execution must not be claimed")
    action_summary = _mapping(example.get("action_summary"))
    for key in ("downloads_enabled", "installs_enabled", "execution_enabled", "authorized_downloads_claimed"):
        if action_summary.get(key) is not False:
            errors.append(f"{label}: action_summary.{key} must be false")
    absence = _mapping(example.get("absence_or_gap_summary"))
    if absence.get("global_absence_claimed") is not False:
        errors.append(f"{label}: global absence must not be claimed")
    return errors


def _validate_member_lineage(label: str, example: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = _mapping(example.get("object_identity"))
    file_members = _mapping(example.get("file_and_member_summary"))
    provenance = _mapping(example.get("provenance_summary"))
    is_member = identity.get("identity_state") == "member_inner_object" or identity.get("object_type") == "file_inside_container"
    if not is_member:
        return errors
    if not file_members.get("parent_object_ref"):
        errors.append(f"{label}: member object must include parent_object_ref")
    if not file_members.get("parent_representation_ref"):
        errors.append(f"{label}: member object must include parent_representation_ref")
    if not _string_items(file_members.get("containment_path")):
        errors.append(f"{label}: member object must include containment_path")
    if provenance.get("parent_lineage_visible") is not True:
        errors.append(f"{label}: member object must keep parent lineage visible")
    if not _string_items(provenance.get("provenance_or_lineage")):
        errors.append(f"{label}: member object must include provenance_or_lineage")
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
        f"validate_object_page_view_model: {report['status']}",
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

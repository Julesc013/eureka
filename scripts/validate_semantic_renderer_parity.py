from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/representations/semantic_renderer_parity.v0.json"
POLICY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
EXAMPLE_PATHS = [
    "examples/representations/semantic_renderer_parity/minimal_absence_page_parity_v0.json",
    "examples/representations/semantic_renderer_parity/minimal_object_page_parity_v0.json",
    "examples/representations/semantic_renderer_parity/minimal_search_card_parity_v0.json",
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
INVENTORY_FIELDS = {
    "schema_version",
    "registry_id",
    "contract_ref",
    "status",
    "stability",
    "created_by_slice",
    "required_view_families",
    "required_semantic_categories",
    "required_representation_profiles",
    "allowed_degradation_examples",
    "forbidden_omission_examples",
    "policies",
    "notes",
}
POLICY_FIELDS = {
    "schema_version",
    "parity_policy_id",
    "label",
    "description",
    "applies_to_view_family",
    "applies_to_route_family",
    "source_contracts",
    "allowed_representation_profiles",
    "required_semantic_fields",
    "required_action_fields",
    "required_status_fields",
    "required_warning_fields",
    "required_link_fields",
    "required_absence_fields",
    "allowed_degradations",
    "forbidden_omissions",
    "forbidden_transformations",
    "representation_specific_requirements",
    "parity_check_strategy",
    "review_required",
    "no_product_runtime_behavior",
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
EXAMPLE_FIELDS = {
    "schema_version",
    "example_id",
    "parity_policy_ref",
    "applies_to_view_family",
    "applies_to_route_family",
    "covered_representation_profiles",
    "required_semantic_fields_demonstrated",
    "allowed_degradation_demo",
    "forbidden_omission_demo",
    "sample_semantic_payload",
    "no_product_runtime_behavior",
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
REQUIRED_VIEW_FAMILIES = {
    "absence_page",
    "candidate_page_future",
    "download_manifest_page",
    "need_page_future",
    "object_page",
    "pack_page_future",
    "review_page_future",
    "search_page",
    "search_result_card",
    "source_page",
    "task_page_future",
}
REQUIRED_REPRESENTATION_PROFILES = {
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
STANDARD_SEMANTIC_FIELDS = {
    "absence_scope",
    "allowed_actions",
    "blocked_actions",
    "candidate_review_state",
    "canonical_id",
    "canonical_route",
    "compatibility_summary",
    "confidence_or_uncertainty",
    "evidence_links",
    "evidence_summary",
    "gaps",
    "generated_or_observed_status",
    "identity",
    "last_updated_or_observed_when_available",
    "limitations",
    "object_type",
    "provenance_or_lineage",
    "result_state",
    "rights_posture",
    "risk_posture",
    "source_posture",
    "title_or_label",
}
NO_BEHAVIOR_FLAGS = {
    "no_accounts_enabled",
    "no_downloads_enabled",
    "no_hosting_enabled",
    "no_live_probes_enabled",
    "no_master_index_mutation",
    "no_native_project_created",
    "no_product_runtime_behavior",
    "no_telemetry_enabled",
    "no_uploads_enabled",
}
ENABLED_CLAIM_FIELDS = {
    "accounts_enabled",
    "downloads_enabled",
    "hosting_enabled",
    "live_probes_enabled",
    "master_index_mutated",
    "native_project_created",
    "product_runtime_behavior_changed",
    "telemetry_enabled",
    "uploads_enabled",
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
        description="Validate Eureka semantic renderer parity schema, inventory, and examples."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_semantic_renderer_parity(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_semantic_renderer_parity(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors, root)
    if isinstance(contract, Mapping):
        _validate_schema(CONTRACT_PATH, contract, errors)

    policy_inventory = _load_json(root / POLICY_INVENTORY, errors, root)
    representation_inventory = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    examples: list[Mapping[str, Any]] = []
    for relative in EXAMPLE_PATHS:
        payload = _load_json(root / relative, errors, root)
        if isinstance(payload, Mapping):
            examples.append(payload)

    if isinstance(policy_inventory, Mapping) and isinstance(representation_inventory, Mapping):
        errors.extend(
            validate_payloads(
                policy_inventory,
                representation_inventory,
                examples,
                source_label="semantic_renderer_parity",
                require_required_view_families=True,
            )
        )

    policy_count = _policy_count(policy_inventory)
    example_count = len(examples)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_semantic_renderer_parity",
        "schema_version": SCHEMA_VERSION,
        "contract_checked": CONTRACT_PATH,
        "inventory_checked": POLICY_INVENTORY,
        "representation_inventory_checked": REPRESENTATION_INVENTORY,
        "examples_checked": sorted(EXAMPLE_PATHS),
        "policy_count": policy_count,
        "example_count": example_count,
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }


def validate_payloads(
    policy_inventory: Mapping[str, Any],
    representation_inventory: Mapping[str, Any],
    examples: Sequence[Mapping[str, Any]] | None = None,
    *,
    source_label: str,
    require_required_view_families: bool,
) -> list[str]:
    errors: list[str] = []
    representation_ids = _representation_ids(representation_inventory, errors, source_label)
    policies = _validate_policy_inventory(
        source_label,
        policy_inventory,
        representation_ids,
        errors,
        require_required_view_families=require_required_view_families,
    )
    if examples is not None:
        _validate_examples(source_label, examples, policies, representation_ids, errors)
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
    missing_required = sorted(POLICY_FIELDS - required_fields)
    if missing_required:
        errors.append(f"{relative}: required list missing {missing_required}.")

    schema_version = _mapping(_mapping(payload.get("properties")).get("schema_version"))
    if schema_version.get("const") != SCHEMA_VERSION:
        errors.append(f"{relative}: schema_version const must be {SCHEMA_VERSION}.")


def _validate_policy_inventory(
    source_label: str,
    payload: Mapping[str, Any],
    representation_ids: set[str],
    errors: list[str],
    *,
    require_required_view_families: bool,
) -> dict[str, Mapping[str, Any]]:
    label = f"{source_label}: policy_inventory"
    _require_fields(label, payload, INVENTORY_FIELDS, errors)
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}.")
    if payload.get("contract_ref") != CONTRACT_PATH:
        errors.append(f"{label}: contract_ref must be {CONTRACT_PATH}.")

    declared_views = set(_string_list(payload.get("required_view_families")))
    missing_declared_views = sorted(REQUIRED_VIEW_FAMILIES - declared_views)
    if missing_declared_views:
        errors.append(f"{label}: required_view_families missing {missing_declared_views}.")

    declared_semantics = set(_string_list(payload.get("required_semantic_categories")))
    missing_semantics = sorted(STANDARD_SEMANTIC_FIELDS - declared_semantics)
    if missing_semantics:
        errors.append(f"{label}: required_semantic_categories missing {missing_semantics}.")

    declared_profiles = set(_string_list(payload.get("required_representation_profiles")))
    missing_profiles = sorted(REQUIRED_REPRESENTATION_PROFILES - declared_profiles)
    if missing_profiles:
        errors.append(f"{label}: required_representation_profiles missing {missing_profiles}.")
    for profile_id in sorted(declared_profiles):
        if profile_id not in representation_ids:
            errors.append(f"{label}: required_representation_profiles references unknown profile {profile_id}.")

    if not _non_empty_string_list(payload.get("allowed_degradation_examples")):
        errors.append(f"{label}: allowed_degradation_examples must be a non-empty list.")
    if not _non_empty_string_list(payload.get("forbidden_omission_examples")):
        errors.append(f"{label}: forbidden_omission_examples must be a non-empty list.")

    raw_policies = payload.get("policies")
    if not isinstance(raw_policies, list) or not raw_policies:
        errors.append(f"{label}: policies must be a non-empty list.")
        return {}

    policy_ids: set[str] = set()
    view_families: set[str] = set()
    policies_by_id: dict[str, Mapping[str, Any]] = {}
    for index, policy in enumerate(raw_policies):
        item_label = f"{source_label}: policies[{index}]"
        if not isinstance(policy, Mapping):
            errors.append(f"{item_label}: policy must be an object.")
            continue
        policy_id = policy.get("parity_policy_id")
        if isinstance(policy_id, str):
            if policy_id in policy_ids:
                errors.append(f"{item_label}: duplicate parity_policy_id {policy_id}.")
            policy_ids.add(policy_id)
            policies_by_id[policy_id] = policy
            item_label = f"{source_label}: policy {policy_id}"
        _validate_policy(item_label, policy, representation_ids, errors)
        view_family = policy.get("applies_to_view_family")
        if isinstance(view_family, str):
            view_families.add(view_family)

    if require_required_view_families:
        missing_view_families = sorted(REQUIRED_VIEW_FAMILIES - view_families)
        if missing_view_families:
            errors.append(f"{label}: missing policies for view families {missing_view_families}.")
    return policies_by_id


def _validate_policy(
    label: str,
    policy: Mapping[str, Any],
    representation_ids: set[str],
    errors: list[str],
) -> None:
    _require_fields(label, policy, POLICY_FIELDS, errors)
    if policy.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}.")
    if not isinstance(policy.get("parity_policy_id"), str):
        errors.append(f"{label}: parity_policy_id must be a string.")
    _validate_no_behavior_flags(label, policy, errors)

    allowed = set(_string_list(policy.get("allowed_representation_profiles")))
    if not allowed:
        errors.append(f"{label}: allowed_representation_profiles must be a non-empty list.")
    for profile_id in sorted(allowed):
        if profile_id not in representation_ids:
            errors.append(f"{label}: allowed representation profile {profile_id} is not registered.")

    missing_required_allowed = sorted(REQUIRED_REPRESENTATION_PROFILES - allowed)
    if missing_required_allowed:
        errors.append(
            f"{label}: allowed_representation_profiles missing required coverage {missing_required_allowed}."
        )

    required_semantics = set(_string_list(policy.get("required_semantic_fields")))
    if not required_semantics:
        errors.append(f"{label}: required_semantic_fields must be a non-empty list.")
    unknown_semantics = sorted(required_semantics - STANDARD_SEMANTIC_FIELDS)
    if unknown_semantics:
        errors.append(f"{label}: unknown required_semantic_fields {unknown_semantics}.")

    for field_name in (
        "required_action_fields",
        "required_status_fields",
        "required_warning_fields",
        "required_link_fields",
        "required_absence_fields",
        "allowed_degradations",
        "forbidden_omissions",
        "forbidden_transformations",
        "source_contracts",
    ):
        if not _non_empty_string_list(policy.get(field_name)):
            errors.append(f"{label}: {field_name} must be a non-empty list.")

    representation_requirements = policy.get("representation_specific_requirements")
    if not isinstance(representation_requirements, Mapping):
        errors.append(f"{label}: representation_specific_requirements must be an object.")
    else:
        missing_requirements = sorted(REQUIRED_REPRESENTATION_PROFILES - set(representation_requirements))
        if missing_requirements:
            errors.append(
                f"{label}: representation_specific_requirements missing {missing_requirements}."
            )
        for profile_id, requirements in sorted(representation_requirements.items()):
            if profile_id not in representation_ids:
                errors.append(
                    f"{label}: representation_specific_requirements references unknown profile {profile_id}."
                )
            if not _non_empty_string_list(requirements):
                errors.append(
                    f"{label}: representation_specific_requirements.{profile_id} must be a non-empty list."
                )

    strategy = _mapping(policy.get("parity_check_strategy"))
    if strategy.get("reference_view_model_required") is not True:
        errors.append(f"{label}: parity_check_strategy.reference_view_model_required must be true.")
    if strategy.get("compare_required_fields") is not True:
        errors.append(f"{label}: parity_check_strategy.compare_required_fields must be true.")
    if strategy.get("check_mode") not in {
        "contract_inventory",
        "future_fixture_diff",
        "future_renderer_snapshot_diff",
    }:
        errors.append(f"{label}: parity_check_strategy.check_mode is invalid.")


def _validate_examples(
    source_label: str,
    examples: Sequence[Mapping[str, Any]],
    policies: Mapping[str, Mapping[str, Any]],
    representation_ids: set[str],
    errors: list[str],
) -> None:
    example_ids: set[str] = set()
    for index, example in enumerate(examples):
        label = f"{source_label}: examples[{index}]"
        example_id = example.get("example_id")
        if isinstance(example_id, str):
            if example_id in example_ids:
                errors.append(f"{label}: duplicate example_id {example_id}.")
            example_ids.add(example_id)
            label = f"{source_label}: example {example_id}"
        _require_fields(label, example, EXAMPLE_FIELDS, errors)
        if example.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}.")
        _validate_no_behavior_flags(label, example, errors)

        policy_ref = example.get("parity_policy_ref")
        policy = policies.get(policy_ref) if isinstance(policy_ref, str) else None
        if policy is None:
            errors.append(f"{label}: parity_policy_ref {policy_ref!r} is not registered.")
        else:
            if example.get("applies_to_view_family") != policy.get("applies_to_view_family"):
                errors.append(f"{label}: applies_to_view_family must match referenced policy.")
            if example.get("applies_to_route_family") != policy.get("applies_to_route_family"):
                errors.append(f"{label}: applies_to_route_family must match referenced policy.")
            demonstrated = set(_string_list(example.get("required_semantic_fields_demonstrated")))
            required = set(_string_list(policy.get("required_semantic_fields")))
            missing_from_policy = sorted(demonstrated - required)
            if missing_from_policy:
                errors.append(
                    f"{label}: demonstrated semantic fields not required by policy {missing_from_policy}."
                )

        covered = set(_string_list(example.get("covered_representation_profiles")))
        if not covered:
            errors.append(f"{label}: covered_representation_profiles must be a non-empty list.")
        for profile_id in sorted(covered):
            if profile_id not in representation_ids:
                errors.append(f"{label}: covered representation profile {profile_id} is not registered.")

        if not _non_empty_string_list(example.get("required_semantic_fields_demonstrated")):
            errors.append(f"{label}: required_semantic_fields_demonstrated must be non-empty.")
        if not _mapping(example.get("allowed_degradation_demo")).get("meaning_preserved") is True:
            errors.append(f"{label}: allowed_degradation_demo.meaning_preserved must be true.")
        if not isinstance(example.get("forbidden_omission_demo"), Mapping):
            errors.append(f"{label}: forbidden_omission_demo must be an object.")
        if not isinstance(example.get("sample_semantic_payload"), Mapping):
            errors.append(f"{label}: sample_semantic_payload must be an object.")

        for bad_path, value in _iter_strings(example):
            for pattern in UNSAFE_EXAMPLE_PATTERNS:
                if pattern.search(value):
                    errors.append(f"{label}: unsafe example value at {bad_path}.")


def _validate_no_behavior_flags(label: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    for flag in sorted(NO_BEHAVIOR_FLAGS):
        if payload.get(flag) is not True:
            errors.append(f"{label}: {flag} must be true.")
    for key in sorted(ENABLED_CLAIM_FIELDS):
        if payload.get(key):
            errors.append(f"{label}: must not claim {key}.")


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


def _policy_count(payload: Any) -> int:
    if isinstance(payload, Mapping) and isinstance(payload.get("policies"), list):
        return len(payload["policies"])
    return 0


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _non_empty_string_list(value: Any) -> bool:
    return bool(_string_list(value))


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


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Semantic renderer parity validation",
        f"status: {report['status']}",
        f"policies: {report['policy_count']}",
        f"examples: {report['example_count']}",
    ]
    for error in report.get("errors", []):
        lines.append(f"ERROR: {error}")
    for warning in report.get("warnings", []):
        lines.append(f"WARN: {warning}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

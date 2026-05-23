from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/view/pages/search_page.v0.json"
POLICY_INVENTORY = "control/inventory/publication/search_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX_INVENTORY = "control/inventory/publication/route_view_representation_matrix.json"
EXAMPLE_PATHS = [
    "examples/view_models/search_page/absence_search_page_v0.json",
    "examples/view_models/search_page/empty_search_page_v0.json",
    "examples/view_models/search_page/minimal_search_page_v0.json",
    "examples/view_models/search_page/result_card_search_page_v0.json",
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
    "search_mode",
    "public_runtime_posture",
    "query",
    "interpreted_intent",
    "controls",
    "result_summary",
    "results",
    "result_sections",
    "source_summary",
    "evidence_summary",
    "absence",
    "limitations",
    "warnings",
    "actions",
    "blocked_actions",
    "pagination",
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
    "allowed_result_section_names",
    "allowed_search_modes",
    "allowed_action_names",
    "required_blocked_actions",
    "required_product_boundary_booleans",
    "required_semantic_requirements",
    "required_representation_hints",
    "current_no_goals",
    "future_deferred_fields",
    "notes",
}
QUERY_FIELDS = {
    "raw_query",
    "normalized_query",
    "query_id_or_hash",
    "submitted_via",
    "query_status",
    "interpreted_intent",
    "query_plan_ref",
    "privacy_posture",
    "poisoning_guard_posture",
    "notes",
}
RESULT_FIELDS = {
    "result_id",
    "result_card_ref",
    "embedded_result_card",
    "canonical_object_id",
    "title",
    "route",
    "result_state",
    "source_posture",
    "evidence_posture",
    "compatibility_posture",
    "rights_posture",
    "risk_posture",
    "allowed_actions",
    "blocked_actions",
    "limitations",
    "gaps",
    "confidence_or_uncertainty",
    "candidate_review_state",
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
    "hosted_backend_unavailable",
    "install_unavailable",
    "live_probe_unavailable",
    "telemetry_unavailable",
    "upload_unavailable",
}
REQUIRED_REPRESENTATION_HINTS = {
    "api_json",
    "file_tree",
    "html32",
    "lite_html",
    "native_card_future",
    "relay_future",
    "snapshot_future",
    "standard_html",
    "terminal_future",
    "text",
}
ALLOWED_SEARCH_MODES = {
    "fixture_backed",
    "future_hosted",
    "future_live_probe_disabled",
    "future_node_task",
    "future_source_cache",
    "local_index_only",
    "static_demo",
    "static_handoff",
}
ALLOWED_RESULT_SECTIONS = {
    "known_absence",
    "near_misses",
    "policy_blocked",
    "private_local_only_future",
    "provisional_candidates",
    "source_leads",
    "verified_or_reviewed_results",
}
ALLOWED_ACTIONS = {
    "copy_query",
    "export_manifest_future",
    "open_local_runtime_route",
    "open_static_demo",
    "refine_query",
    "submit_search_get",
    "view_absence",
    "view_evidence",
    "view_result",
    "view_source",
}
SEARCH_COMPATIBLE_ROUTE_FAMILIES = {
    "api_search",
    "demo_static",
    "files_static",
    "lite_static",
    "search",
    "text_static",
}
REQUIRED_SEMANTIC_REQUIREMENTS = {
    "absence_scope_preserved",
    "allowed_and_blocked_actions_preserved",
    "canonical_route_preserved",
    "candidate_state_preserved",
    "limitations_and_gaps_visible",
    "query_identity_preserved",
    "result_state_preserved",
    "rights_and_risk_posture_preserved",
    "source_evidence_status_meaning_preserved",
}
CURRENT_OR_EXAMPLE_MODES = {
    "fixture_backed",
    "local_index_only",
    "static_demo",
    "static_handoff",
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
        description="Validate Eureka SearchPage view-model schema, policy, and examples."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_search_page_view_model(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_search_page_view_model(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
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
                source_label="search_page_view_model",
            )
        )

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_search_page_view_model",
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
    route_ids = _route_ids(route_matrix)

    errors.extend(_validate_policy(policy, representation_ids, semantic_policy_ids, route_ids))

    policy_route_families = set(_string_items(policy.get("supported_route_families")))
    policy_representations = set(_string_items(policy.get("allowed_representation_profiles")))
    policy_search_modes = set(_string_items(policy.get("allowed_search_modes")))
    policy_actions = set(_string_items(policy.get("allowed_action_names")))
    policy_sections = set(_string_items(policy.get("allowed_result_section_names")))
    policy_required_semantics = set(_string_items(policy.get("required_semantic_requirements")))
    policy_required_hints = set(_string_items(policy.get("required_representation_hints")))
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
                policy_search_modes,
                policy_actions,
                policy_sections,
                policy_required_semantics,
                policy_required_hints,
                policy_blocked,
                semantic_policy_ref if isinstance(semantic_policy_ref, str) else "",
                representation_ids,
                route_ids,
            )
        )

    if not examples:
        errors.append(f"{source_label}: at least one SearchPageView example is required")

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
    route_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    missing = POLICY_FIELDS - set(policy)
    if missing:
        errors.append(f"{POLICY_INVENTORY}: missing policy fields {sorted(missing)}")
    if policy.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{POLICY_INVENTORY}: schema_version must be {SCHEMA_VERSION}")
    if policy.get("contract_ref") != CONTRACT_PATH:
        errors.append(f"{POLICY_INVENTORY}: contract_ref must be {CONTRACT_PATH}")
    if policy.get("canonical_view_family") != "SearchPageView":
        errors.append(f"{POLICY_INVENTORY}: canonical_view_family must be SearchPageView")

    supported_routes = set(_string_items(policy.get("supported_route_families")))
    missing_routes = supported_routes - route_ids
    if missing_routes:
        errors.append(f"{POLICY_INVENTORY}: unsupported route family refs {sorted(missing_routes)}")
    non_search_routes = supported_routes - SEARCH_COMPATIBLE_ROUTE_FAMILIES
    if non_search_routes:
        errors.append(
            f"{POLICY_INVENTORY}: route families are not search/static-compatible {sorted(non_search_routes)}"
        )
    if "search" not in supported_routes:
        errors.append(f"{POLICY_INVENTORY}: supported_route_families must include search")

    policy_representations = set(_string_items(policy.get("allowed_representation_profiles")))
    missing_representations = policy_representations - representation_ids
    if missing_representations:
        errors.append(
            f"{POLICY_INVENTORY}: unknown representation profile refs {sorted(missing_representations)}"
        )
    missing_required_representations = REQUIRED_REPRESENTATION_HINTS - policy_representations
    if missing_required_representations:
        errors.append(
            f"{POLICY_INVENTORY}: allowed_representation_profiles missing {sorted(missing_required_representations)}"
        )

    required_hints = set(_string_items(policy.get("required_representation_hints")))
    missing_required_hints = REQUIRED_REPRESENTATION_HINTS - required_hints
    if missing_required_hints:
        errors.append(
            f"{POLICY_INVENTORY}: required_representation_hints missing {sorted(missing_required_hints)}"
        )

    semantic_ref = policy.get("required_semantic_parity_policy")
    if semantic_ref not in semantic_policy_ids:
        errors.append(f"{POLICY_INVENTORY}: semantic parity policy ref {semantic_ref!r} does not exist")

    allowed_sections = set(_string_items(policy.get("allowed_result_section_names")))
    if not ALLOWED_RESULT_SECTIONS <= allowed_sections:
        errors.append(
            f"{POLICY_INVENTORY}: allowed_result_section_names missing {sorted(ALLOWED_RESULT_SECTIONS - allowed_sections)}"
        )

    search_modes = set(_string_items(policy.get("allowed_search_modes")))
    if not ALLOWED_SEARCH_MODES <= search_modes:
        errors.append(
            f"{POLICY_INVENTORY}: allowed_search_modes missing {sorted(ALLOWED_SEARCH_MODES - search_modes)}"
        )

    actions = set(_string_items(policy.get("allowed_action_names")))
    if not ALLOWED_ACTIONS <= actions:
        errors.append(f"{POLICY_INVENTORY}: allowed_action_names missing {sorted(ALLOWED_ACTIONS - actions)}")

    blocked = set(_string_items(policy.get("required_blocked_actions")))
    if not REQUIRED_BLOCKED_ACTIONS <= blocked:
        errors.append(
            f"{POLICY_INVENTORY}: required_blocked_actions missing {sorted(REQUIRED_BLOCKED_ACTIONS - blocked)}"
        )

    flags = set(_string_items(policy.get("required_product_boundary_booleans")))
    if not PUBLIC_RUNTIME_FLAGS <= flags:
        errors.append(
            f"{POLICY_INVENTORY}: required_product_boundary_booleans missing {sorted(PUBLIC_RUNTIME_FLAGS - flags)}"
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
    policy_search_modes: set[str],
    policy_actions: set[str],
    policy_sections: set[str],
    policy_required_semantics: set[str],
    policy_required_hints: set[str],
    policy_blocked: set[str],
    semantic_policy_ref: str,
    representation_ids: set[str],
    route_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    missing = VIEW_MODEL_FIELDS - set(example)
    if missing:
        errors.append(f"{label}: missing required top-level fields {sorted(missing)}")
        return errors

    if example.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if example.get("view_family") != "SearchPageView":
        errors.append(f"{label}: view_family must be SearchPageView")

    route_family = example.get("route_family")
    if route_family not in policy_route_families:
        errors.append(f"{label}: route_family {route_family!r} is not allowed by policy")
    if route_family not in route_ids:
        errors.append(f"{label}: route_family {route_family!r} is not in route matrix")
    if route_family not in SEARCH_COMPATIBLE_ROUTE_FAMILIES:
        errors.append(f"{label}: route_family {route_family!r} is not search/static-compatible")

    search_mode = example.get("search_mode")
    if search_mode not in policy_search_modes:
        errors.append(f"{label}: search_mode {search_mode!r} is not allowed by policy")
    if search_mode not in ALLOWED_SEARCH_MODES:
        errors.append(f"{label}: search_mode {search_mode!r} is invalid")

    query = example.get("query")
    if not isinstance(query, Mapping):
        errors.append(f"{label}: query must be an object")
    else:
        missing_query = QUERY_FIELDS - set(query)
        if missing_query:
            errors.append(f"{label}: query missing {sorted(missing_query)}")
        if query.get("privacy_posture") not in {
            "anonymous_no_retention",
            "anonymous_transient",
            "fixture_public",
            "future_account_preference_disabled",
        }:
            errors.append(f"{label}: query privacy_posture must permit anonymous/no-retention posture")

    runtime = example.get("public_runtime_posture")
    blocked_actions = _blocked_action_ids(example.get("blocked_actions"))
    if not isinstance(runtime, Mapping):
        errors.append(f"{label}: public_runtime_posture must be an object")
    else:
        missing_flags = PUBLIC_RUNTIME_FLAGS - set(runtime)
        if missing_flags:
            errors.append(f"{label}: public_runtime_posture missing {sorted(missing_flags)}")
        for flag in sorted(PUBLIC_RUNTIME_FLAGS):
            if runtime.get(flag) is not False:
                errors.append(f"{label}: {flag} must be false for current static/local examples")
            blocked_action = FLAG_TO_BLOCKED_ACTION[flag]
            if runtime.get(flag) is False and blocked_action not in blocked_actions:
                errors.append(f"{label}: missing blocked action {blocked_action} for false {flag}")

    missing_required_blocked = (policy_blocked | REQUIRED_BLOCKED_ACTIONS) - blocked_actions
    if missing_required_blocked:
        errors.append(f"{label}: blocked_actions missing {sorted(missing_required_blocked)}")

    actions = _action_ids(example.get("actions"))
    unknown_actions = actions - policy_actions
    if unknown_actions:
        errors.append(f"{label}: actions contain unknown action ids {sorted(unknown_actions)}")
    controls = example.get("controls")
    if isinstance(controls, Sequence) and not isinstance(controls, (str, bytes)):
        control_actions = {
            item.get("allowed_action")
            for item in controls
            if isinstance(item, Mapping) and isinstance(item.get("allowed_action"), str)
        }
        unknown_control_actions = control_actions - policy_actions
        if unknown_control_actions:
            errors.append(f"{label}: controls contain unknown actions {sorted(unknown_control_actions)}")
    else:
        errors.append(f"{label}: controls must be an array")

    section_names = set(example.get("result_sections", {}).keys()) if isinstance(example.get("result_sections"), Mapping) else set()
    unknown_sections = section_names - policy_sections
    if unknown_sections:
        errors.append(f"{label}: result_sections contain unknown names {sorted(unknown_sections)}")

    result_ids = _result_ids(example.get("results"))
    if isinstance(example.get("result_sections"), Mapping):
        for section_name, section in example["result_sections"].items():
            if isinstance(section, Mapping):
                missing_result_ids = set(_string_items(section.get("result_ids"))) - result_ids
                if missing_result_ids:
                    errors.append(
                        f"{label}: result section {section_name} references missing result ids {sorted(missing_result_ids)}"
                    )

    errors.extend(_validate_results(label, example.get("results")))
    errors.extend(_validate_absence(label, example.get("absence")))

    hints = example.get("representation_hints")
    if not isinstance(hints, Mapping):
        errors.append(f"{label}: representation_hints must be an object")
    else:
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

    semantics = set(_string_items(example.get("semantic_requirements")))
    if not semantics:
        errors.append(f"{label}: semantic_requirements must be non-empty")
    missing_semantics = (policy_required_semantics | REQUIRED_SEMANTIC_REQUIREMENTS) - semantics
    if missing_semantics:
        errors.append(f"{label}: semantic_requirements missing {sorted(missing_semantics)}")

    generated_from = example.get("generated_from")
    if not isinstance(generated_from, Mapping):
        errors.append(f"{label}: generated_from must be an object")
    elif generated_from.get("semantic_parity_policy") != semantic_policy_ref:
        errors.append(
            f"{label}: generated_from semantic_parity_policy must be {semantic_policy_ref!r}"
        )

    raw = json.dumps(example, sort_keys=True)
    for pattern in UNSAFE_EXAMPLE_PATTERNS:
        if pattern.search(raw):
            errors.append(f"{label}: example contains unsafe/private pattern {pattern.pattern}")

    return errors


def _validate_results(label: str, results: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
        return [f"{label}: results must be an array"]

    for index, result in enumerate(results):
        result_label = f"{label}: result[{index}]"
        if not isinstance(result, Mapping):
            errors.append(f"{result_label}: result must be an object")
            continue
        missing = RESULT_FIELDS - set(result)
        if missing:
            errors.append(f"{result_label}: missing result fields {sorted(missing)}")
        result_state = result.get("result_state")
        review_state = result.get("candidate_review_state")
        if review_state in {"candidate", "provisional", "review_required"} and result_state == "verified":
            errors.append(f"{result_label}: candidate/provisional record must not be marked verified")
        if result_state in {"candidate", "provisional"} and review_state == "verified":
            errors.append(f"{result_label}: candidate/provisional result must not use verified review state")
        if result_state in {"candidate", "provisional"}:
            blocked = set(_string_items(result.get("blocked_actions")))
            if "download_unavailable" not in blocked or "install_unavailable" not in blocked:
                errors.append(f"{result_label}: candidate/provisional results must block download and install")
    return errors


def _validate_absence(label: str, absence: Any) -> list[str]:
    errors: list[str] = []
    if absence is None:
        return errors
    if not isinstance(absence, Mapping):
        return [f"{label}: absence must be null or an object"]
    required = {
        "absence_status",
        "searched_scope",
        "sources_checked",
        "sources_not_checked",
        "near_matches",
        "known_gaps",
        "next_safe_actions",
        "work_unit_refs_future",
        "need_refs_future",
        "limitations",
        "exhaustive_global_search",
        "notes",
    }
    missing = required - set(absence)
    if missing:
        errors.append(f"{label}: absence missing {sorted(missing)}")
    if absence.get("exhaustive_global_search") is True and not absence.get(
        "global_exhaustive_evidence_refs"
    ):
        errors.append(f"{label}: absence must not claim exhaustive global search without explicit evidence")
    if absence.get("absence_status") in {"scoped_no_verified_result", "weak_result_only"}:
        if not _string_items(absence.get("sources_not_checked")):
            errors.append(f"{label}: absence must name sources_not_checked for scoped absence")
        if not _string_items(absence.get("known_gaps")):
            errors.append(f"{label}: absence must name known_gaps for scoped absence")
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


def _route_ids(matrix: Mapping[str, Any]) -> set[str]:
    routes = matrix.get("route_families")
    if not isinstance(routes, Sequence) or isinstance(routes, (str, bytes)):
        return set()
    return {
        str(route["route_family_id"])
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


def _result_ids(results: Any) -> set[str]:
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
        return set()
    return {
        result["result_id"]
        for result in results
        if isinstance(result, Mapping) and isinstance(result.get("result_id"), str)
    }


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_search_page_view_model: {report['status']}",
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

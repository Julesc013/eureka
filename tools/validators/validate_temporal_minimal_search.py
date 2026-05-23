"""Validate Temporal Minimal Search doctrine, profiles, and token bindings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_design_tokens import (
    SCHEMA_VERSION,
    TOKEN_INVENTORY_PATH,
    validate_design_token_payload,
)


CONTRACT_PATH = "contracts/surface/ui/temporal_minimal_search.v0.json"
DESIGN_LANGUAGE_EXAMPLE = "examples/design_tokens/temporal_minimal_search_v0.json"
TOKEN_INVENTORY = TOKEN_INVENTORY_PATH
PROFILE_MATRIX = "control/inventory/publication/design_profile_matrix.json"
REPRESENTATION_PROFILES = "control/inventory/publication/representation_profiles.json"

TEMPORAL_REQUIRED_FIELDS = {
    "schema_version",
    "design_language_id",
    "label",
    "description",
    "design_doctrine",
    "visual_principles",
    "layout_principles",
    "search_surface_principles",
    "result_card_principles",
    "object_page_principles",
    "source_page_principles",
    "need_candidate_principles",
    "evidence_absence_compare_principles",
    "old_client_principles",
    "text_file_tree_principles",
    "terminal_future_principles",
    "native_card_future_principles",
    "print_principles",
    "accessibility_principles",
    "forbidden_branding_or_trade_dress",
    "forbidden_product_claims",
    "allowed_degradations",
    "required_semantic_visibility",
    "token_refs",
    "no_goals",
    "notes",
}
REQUIRED_DOCTRINE = {
    "fast",
    "link_first",
    "no_js_baseline",
    "old_browser_tolerant",
    "sparse",
    "text_first",
}
REQUIRED_VISUAL_PRINCIPLES = {
    "blue_primary_links",
    "compact_metadata",
    "dark_readable_body_text",
    "green_grey_source_status_lines",
    "high_contrast",
    "minimal_borders",
    "no_external_assets_baseline",
    "no_js_baseline",
    "no_required_custom_fonts",
    "normal_links_get_forms",
    "obvious_search_form",
    "plain_text_fallback",
    "print_output",
    "readable_tables",
    "simple_result_lists",
    "small_page_weight",
    "stable_urls",
    "visited_link_posture",
    "visible_semantic_labels",
    "white_or_low_noise_background",
}
REQUIRED_ACCESSIBILITY = {
    "high_contrast_projection",
    "keyboard_friendly_navigation",
    "labels_for_forms",
    "no_required_cookies_for_search",
    "no_required_custom_fonts",
    "no_required_javascript",
    "plain_text_projection",
    "print_projection",
    "readable_link_distinction",
    "semantic_headings",
    "sufficient_contrast",
    "text_equivalents_for_badges",
}
REQUIRED_OLD_CLIENT = {
    "file_tree_readme_profile",
    "html32_profile_future",
    "low_page_weight",
    "minimal_css",
    "no_external_asset_dependency_baseline",
    "no_required_javascript",
    "no_js_baseline",
    "simple_get_forms",
    "small_result_count_default",
    "table_safe_layouts",
    "text_only_profile",
}
REQUIRED_SEMANTIC_VISIBILITY = {
    "absence_scope",
    "blocked_actions",
    "candidate_provisional_review_state",
    "compatibility_caveats",
    "evidence_posture",
    "limitations",
    "object_source_result_identity",
    "public_static_hosted_limitations",
    "rights_posture",
    "risk_posture",
    "source_posture",
    "unresolved_gaps",
}
REQUIRED_BRANDING_RULES = {
    "no_deceptive_source_labels",
    "no_google_exact_css_html",
    "no_google_exact_page_identity",
    "no_google_like_branding_names",
    "no_google_logos",
    "no_google_or_search_engine_affiliation_claim",
    "no_misleading_official_labels_without_evidence",
    "no_protected_trade_dress_copy",
}
REQUIRED_FORBIDDEN_PRODUCT_CLAIMS = {
    "accounts_enabled",
    "automatic_merge_or_promotion",
    "downloads_enabled",
    "exhaustive_global_search",
    "hosted_backend_active",
    "live_probes_enabled",
    "malware_safety",
    "rights_clearance",
    "source_connectors_active",
    "telemetry_enabled",
    "uploads_enabled",
}
ALLOWED_DESIGN_PROFILES = {
    "classic_search_1998",
    "classic_search_2004",
    "classic_search_2010",
    "eureka_default",
    "high_contrast",
    "print",
    "terminal",
    "text_only",
}
BRANDING_AFFILIATION_PATTERNS = (
    re.compile(r"\baffiliated with google\b", re.IGNORECASE),
    re.compile(r"\bgoogle search affiliated\b", re.IGNORECASE),
    re.compile(r"\bpowered by google\b", re.IGNORECASE),
    re.compile(r"\bcopy google (?:logo|branding|page|css|html)\b", re.IGNORECASE),
)
PRODUCT_CLAIM_PATTERNS = (
    re.compile(r"\bhosted backend (?:is )?(?:active|enabled|live|deployed)\b", re.IGNORECASE),
    re.compile(r"\blive probes? (?:are )?enabled\b", re.IGNORECASE),
    re.compile(r"\bdownloads? (?:are )?enabled\b", re.IGNORECASE),
    re.compile(r"\buploads? (?:are )?enabled\b", re.IGNORECASE),
    re.compile(r"\baccounts? (?:are )?enabled\b", re.IGNORECASE),
    re.compile(r"\btelemetry (?:is )?enabled\b", re.IGNORECASE),
    re.compile(r"\brights clearance (?:is )?(?:granted|verified|claimed)\b", re.IGNORECASE),
    re.compile(r"\bmalware safety (?:is )?(?:verified|claimed)\b", re.IGNORECASE),
    re.compile(r"\bexhaustive global search\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Temporal Minimal Search contracts and examples.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_temporal_minimal_search(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_temporal_minimal_search(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors)
    example = _load_json(root / DESIGN_LANGUAGE_EXAMPLE, errors)
    token_inventory = _load_json(root / TOKEN_INVENTORY, errors)
    profile_matrix = _load_json(root / PROFILE_MATRIX, errors)
    representation_profiles = _load_json(root / REPRESENTATION_PROFILES, errors)

    errors.extend(validate_temporal_contract(contract, CONTRACT_PATH))
    errors.extend(validate_temporal_payload(example, DESIGN_LANGUAGE_EXAMPLE))
    errors.extend(validate_design_token_payload(token_inventory, TOKEN_INVENTORY))
    representation_ids = _representation_ids(representation_profiles)
    errors.extend(validate_design_profile_matrix(profile_matrix, PROFILE_MATRIX, representation_ids))

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "contract": CONTRACT_PATH,
        "design_language_example": DESIGN_LANGUAGE_EXAMPLE,
        "token_inventory": TOKEN_INVENTORY,
        "profile_matrix": PROFILE_MATRIX,
    }


def validate_temporal_contract(payload: Any, source: str) -> list[str]:
    errors: list[str] = []
    data = _mapping(payload)
    for field in {"$schema", "$id", "title", "description", "type", "required", "properties"}:
        if field not in data:
            errors.append(f"{source}: missing schema field {field}")
    required = set(_string_items(data.get("required")))
    for field in sorted(TEMPORAL_REQUIRED_FIELDS):
        if field not in required:
            errors.append(f"{source}: schema required list missing {field}")
    return errors


def validate_temporal_payload(payload: Any, source: str) -> list[str]:
    errors: list[str] = []
    data = _mapping(payload)
    if not data:
        return [f"{source}: expected JSON object"]
    for field in sorted(TEMPORAL_REQUIRED_FIELDS):
        if field not in data:
            errors.append(f"{source}: missing required field {field}")
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source}: schema_version must be {SCHEMA_VERSION}")
    if data.get("design_language_id") != "temporal_minimal_search":
        errors.append(f"{source}: design_language_id must be temporal_minimal_search")
    errors.extend(_missing_members(data, "design_doctrine", REQUIRED_DOCTRINE, source))
    errors.extend(_missing_members(data, "visual_principles", REQUIRED_VISUAL_PRINCIPLES, source))
    errors.extend(_missing_members(data, "accessibility_principles", REQUIRED_ACCESSIBILITY, source))
    errors.extend(_missing_members(data, "old_client_principles", REQUIRED_OLD_CLIENT, source))
    errors.extend(_missing_members(data, "required_semantic_visibility", REQUIRED_SEMANTIC_VISIBILITY, source))
    errors.extend(_missing_members(data, "forbidden_branding_or_trade_dress", REQUIRED_BRANDING_RULES, source))
    errors.extend(_missing_members(data, "forbidden_product_claims", REQUIRED_FORBIDDEN_PRODUCT_CLAIMS, source))
    errors.extend(_unsafe_branding_claims(data, source))
    errors.extend(_unsafe_product_claims(data, source))
    return errors


def validate_design_profile_matrix(payload: Any, source: str, representation_ids: set[str]) -> list[str]:
    errors: list[str] = []
    data = _mapping(payload)
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source}: schema_version must be {SCHEMA_VERSION}")
    profiles = data.get("profiles")
    if not isinstance(profiles, Sequence) or isinstance(profiles, (str, bytes)) or not profiles:
        return errors + [f"{source}: profiles must be a non-empty array"]
    seen: set[str] = set()
    for index, item in enumerate(profiles):
        profile = _mapping(item)
        prefix = f"{source}: profiles[{index}]"
        profile_id = profile.get("profile_id")
        if not isinstance(profile_id, str):
            errors.append(f"{prefix}: profile_id is required")
        elif profile_id in seen:
            errors.append(f"{prefix}: duplicate profile_id {profile_id}")
        else:
            seen.add(profile_id)
            if profile_id not in ALLOWED_DESIGN_PROFILES:
                errors.append(f"{prefix}: unknown design profile {profile_id}")
        for field in (
            "label",
            "intended_representation_profiles",
            "token_set_ref",
            "css_dependency",
            "javascript_dependency",
            "old_client_fit",
            "page_weight_budget_kb",
            "semantic_visibility_requirements",
            "forbidden_claims",
            "notes",
        ):
            if field not in profile:
                errors.append(f"{prefix}: missing {field}")
        for representation in _string_items(profile.get("intended_representation_profiles")):
            if representation not in representation_ids:
                errors.append(f"{prefix}: unknown representation profile {representation}")
        if profile.get("javascript_dependency") != "none":
            errors.append(f"{prefix}: javascript_dependency must be none")
        if not _string_items(profile.get("semantic_visibility_requirements")):
            errors.append(f"{prefix}: semantic_visibility_requirements must be non-empty")
        if not isinstance(profile.get("page_weight_budget_kb"), int):
            errors.append(f"{prefix}: page_weight_budget_kb must be an integer")
    errors.extend(_product_boundary_errors(_mapping(data.get("product_boundary")), source))
    return errors


def _missing_members(data: Mapping[str, Any], field: str, required: set[str], source: str) -> list[str]:
    present = set(_string_items(data.get(field)))
    return [f"{source}: {field} missing {item}" for item in sorted(required - present)]


def _unsafe_branding_claims(value: Any, source: str) -> list[str]:
    text = json.dumps(value, sort_keys=True)
    errors: list[str] = []
    for pattern in BRANDING_AFFILIATION_PATTERNS:
        for match in pattern.finditer(text):
            if not _match_is_negated(text, match):
                errors.append(f"{source}: unsafe branding or affiliation claim matched {pattern.pattern}")
                break
    return errors


def _unsafe_product_claims(value: Any, source: str) -> list[str]:
    text = json.dumps(value, sort_keys=True)
    errors: list[str] = []
    for pattern in PRODUCT_CLAIM_PATTERNS:
        for match in pattern.finditer(text):
            if not _match_is_negated(text, match):
                errors.append(f"{source}: unsafe product claim matched {pattern.pattern}")
                break
    return errors


def _match_is_negated(text: str, match: re.Match[str]) -> bool:
    prefix = text[max(0, match.start() - 48):match.start()].lower()
    return (
        "no_" in prefix[-24:]
        or "no " in prefix[-16:]
        or "not " in prefix[-16:]
        or "forbidden" in prefix[-32:]
        or "claim" in prefix[-24:]
        or "without" in prefix[-24:]
    )


def _product_boundary_errors(boundary: Mapping[str, Any], source: str) -> list[str]:
    required = {
        "changed_generated_site_artifacts",
        "changed_product_behavior",
        "changed_public_routes",
        "claimed_automatic_merge_or_promotion",
        "claimed_exhaustive_global_search",
        "claimed_malware_safety",
        "claimed_rights_clearance",
        "claimed_search_engine_affiliation",
        "claimed_verified_installability",
        "copied_google_branding",
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
    errors = []
    for field in sorted(required):
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
        str(profile["representation_profile_id"])
        for profile in profiles
        if isinstance(profile, Mapping) and isinstance(profile.get("representation_profile_id"), str)
    }


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_temporal_minimal_search: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"profile_matrix: {report['profile_matrix']}",
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

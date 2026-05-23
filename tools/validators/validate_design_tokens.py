"""Validate Eureka design token contracts without invoking renderers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATH = "contracts/surface/ui/design_tokens.v0.json"
POLICY_PATH = "control/inventory/publication/design_token_policy.json"
TOKEN_INVENTORY_PATH = "control/inventory/publication/temporal_minimal_search_tokens.json"
EXAMPLE_PATHS = [
    "examples/design_tokens/minimal_design_tokens_v0.json",
    "examples/design_tokens/high_contrast_temporal_minimal_search_v0.json",
    "examples/design_tokens/text_only_temporal_minimal_search_v0.json",
]

TOKEN_REQUIRED_FIELDS = {
    "schema_version",
    "token_set_id",
    "label",
    "description",
    "token_status",
    "intended_profiles",
    "color_tokens",
    "typography_tokens",
    "spacing_tokens",
    "density_tokens",
    "border_tokens",
    "layout_tokens",
    "link_tokens",
    "form_tokens",
    "table_tokens",
    "badge_tokens",
    "warning_tokens",
    "action_tokens",
    "compatibility_tokens",
    "risk_rights_tokens",
    "evidence_source_tokens",
    "accessibility_tokens",
    "degradation_tokens",
    "forbidden_visual_claims",
    "product_boundary",
    "no_goals",
    "notes",
}
REQUIRED_TOKEN_FAMILIES = {
    "accessibility_tokens",
    "action_tokens",
    "badge_tokens",
    "border_tokens",
    "color_tokens",
    "compatibility_tokens",
    "degradation_tokens",
    "density_tokens",
    "evidence_source_tokens",
    "form_tokens",
    "layout_tokens",
    "link_tokens",
    "risk_rights_tokens",
    "spacing_tokens",
    "table_tokens",
    "typography_tokens",
    "warning_tokens",
}
REQUIRED_PRODUCT_BOUNDARY = {
    "changed_product_behavior",
    "changed_public_routes",
    "changed_generated_site_artifacts",
    "regenerated_site_dist",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "created_native_projects",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_automatic_merge_or_promotion",
    "copied_google_branding",
    "claimed_search_engine_affiliation",
}
REQUIRED_FORBIDDEN_PRODUCT_CLAIMS = {
    "accepted_public_truth",
    "accounts_enabled",
    "automatic_merge_dedup_promotion",
    "downloads_enabled",
    "exhaustive_global_search",
    "hosted_backend_active",
    "live_probes_enabled",
    "malware_safety",
    "rights_clearance",
    "source_connectors_active",
    "telemetry_enabled",
    "uploads_enabled",
    "verified_installability",
}
BOOLEAN_BOUNDARY_FIELDS = {
    "accounts_enabled": "enabled_accounts",
    "automatic_merge_enabled": "claimed_automatic_merge_or_promotion",
    "automatic_promotion_enabled": "claimed_automatic_merge_or_promotion",
    "copied_google_branding": "copied_google_branding",
    "direct_download_enabled": "enabled_downloads",
    "downloads_enabled": "enabled_downloads",
    "enabled_accounts": "enabled_accounts",
    "enabled_downloads": "enabled_downloads",
    "enabled_execution": "enabled_execution",
    "enabled_hosting": "enabled_hosting",
    "enabled_live_probes": "enabled_live_probes",
    "enabled_source_connectors": "enabled_source_connectors",
    "enabled_source_sync": "enabled_source_sync",
    "enabled_telemetry": "enabled_telemetry",
    "enabled_uploads": "enabled_uploads",
    "execution_enabled": "enabled_execution",
    "hosted_backend_active": "enabled_hosting",
    "hosted_backend_claimed": "enabled_hosting",
    "live_probes_enabled": "enabled_live_probes",
    "malware_safety_claimed": "claimed_malware_safety",
    "master_index_mutation_allowed": "mutated_master_index",
    "native_runtime_active": "created_native_projects",
    "rights_clearance_claimed": "claimed_rights_clearance",
    "telemetry_enabled": "enabled_telemetry",
    "uploads_enabled": "enabled_uploads",
    "verified_installability_claimed": "claimed_verified_installability",
}
UNSAFE_TEXT_PATTERNS = {
    "enabled_hosting": re.compile(r"\bhosted backend (?:is )?(?:active|enabled|live|deployed)\b", re.IGNORECASE),
    "enabled_live_probes": re.compile(r"\blive probes? (?:are )?enabled\b", re.IGNORECASE),
    "enabled_downloads": re.compile(r"\bdownloads? (?:are )?enabled\b", re.IGNORECASE),
    "enabled_uploads": re.compile(r"\buploads? (?:are )?enabled\b", re.IGNORECASE),
    "enabled_accounts": re.compile(r"\baccounts? (?:are )?enabled\b", re.IGNORECASE),
    "enabled_telemetry": re.compile(r"\btelemetry (?:is )?enabled\b", re.IGNORECASE),
    "claimed_rights_clearance": re.compile(r"\brights clearance (?:is )?(?:granted|verified|claimed)\b", re.IGNORECASE),
    "claimed_malware_safety": re.compile(r"\bmalware safety (?:is )?(?:verified|claimed)\b", re.IGNORECASE),
    "claimed_exhaustive_global_search": re.compile(r"\bexhaustive global search\b", re.IGNORECASE),
    "claimed_automatic_merge_or_promotion": re.compile(
        r"\bautomatic (?:merge|dedup|promotion) (?:is )?(?:enabled|allowed)\b", re.IGNORECASE
    ),
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka design token contracts and examples.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_design_tokens(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_design_tokens(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contract = _load_json(root / CONTRACT_PATH, errors)
    policy = _load_json(root / POLICY_PATH, errors)
    inventory = _load_json(root / TOKEN_INVENTORY_PATH, errors)

    errors.extend(validate_design_token_contract(contract, CONTRACT_PATH))
    errors.extend(validate_design_token_policy(policy, POLICY_PATH))
    errors.extend(validate_design_token_payload(inventory, TOKEN_INVENTORY_PATH))

    for example_path in EXAMPLE_PATHS:
        payload = _load_json(root / example_path, errors)
        errors.extend(validate_design_token_payload(payload, example_path))

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "contract": CONTRACT_PATH,
        "policy": POLICY_PATH,
        "token_inventory": TOKEN_INVENTORY_PATH,
        "examples": list(EXAMPLE_PATHS),
    }


def validate_design_token_contract(payload: Any, source: str) -> list[str]:
    errors: list[str] = []
    data = _mapping(payload)
    for field in {"$schema", "$id", "title", "description", "type", "required", "properties"}:
        if field not in data:
            errors.append(f"{source}: missing schema field {field}")
    required = set(_string_items(data.get("required")))
    for field in sorted(TOKEN_REQUIRED_FIELDS):
        if field not in required:
            errors.append(f"{source}: schema required list missing {field}")
    return errors


def validate_design_token_policy(payload: Any, source: str) -> list[str]:
    errors: list[str] = []
    data = _mapping(payload)
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source}: schema_version must be {SCHEMA_VERSION}")
    required_families = set(_string_items(data.get("required_token_families")))
    for family in sorted(REQUIRED_TOKEN_FAMILIES):
        if family not in required_families:
            errors.append(f"{source}: required_token_families missing {family}")
    product_fields = set(_string_items(data.get("required_product_boundary_booleans")))
    for field in sorted(REQUIRED_PRODUCT_BOUNDARY):
        if field not in product_fields:
            errors.append(f"{source}: required_product_boundary_booleans missing {field}")
    claims = set(_string_items(data.get("forbidden_product_claims")))
    for claim in sorted(REQUIRED_FORBIDDEN_PRODUCT_CLAIMS):
        if claim not in claims:
            errors.append(f"{source}: forbidden_product_claims missing {claim}")
    if not _string_items(data.get("accessibility_requirements")):
        errors.append(f"{source}: accessibility_requirements must be non-empty")
    if not _string_items(data.get("old_client_requirements")):
        errors.append(f"{source}: old_client_requirements must be non-empty")
    return errors


def validate_design_token_payload(payload: Any, source: str) -> list[str]:
    errors: list[str] = []
    data = _mapping(payload)
    if not data:
        return [f"{source}: expected JSON object"]
    for field in sorted(TOKEN_REQUIRED_FIELDS):
        if field not in data:
            errors.append(f"{source}: missing required field {field}")
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source}: schema_version must be {SCHEMA_VERSION}")
    for family in sorted(REQUIRED_TOKEN_FAMILIES):
        value = data.get(family)
        if not isinstance(value, Mapping) or not value:
            errors.append(f"{source}: token family {family} must be a non-empty object")
    product_boundary = _mapping(data.get("product_boundary"))
    errors.extend(_validate_product_boundary(product_boundary, source))
    errors.extend(_json_boundary_violations(data, source))
    errors.extend(_text_boundary_violations(data, source))
    if not _string_items(data.get("forbidden_visual_claims")):
        errors.append(f"{source}: forbidden_visual_claims must be non-empty")
    return errors


def _validate_product_boundary(product_boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED_PRODUCT_BOUNDARY):
        if field not in product_boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif product_boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _json_boundary_violations(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            boundary = BOOLEAN_BOUNDARY_FIELDS.get(str(key))
            if boundary and child is True:
                errors.append(f"{source}: {child_path} implies {boundary}")
            errors.extend(_json_boundary_violations(child, source, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            errors.extend(_json_boundary_violations(child, source, f"{path}[{index}]"))
    return errors


def _text_boundary_violations(value: Any, source: str) -> list[str]:
    text = json.dumps(value, sort_keys=True)
    errors: list[str] = []
    for boundary, pattern in UNSAFE_TEXT_PATTERNS.items():
        for match in pattern.finditer(text):
            if not _match_is_negated(text, match):
                errors.append(f"{source}: unsafe product claim implies {boundary}")
                break
    return errors


def _match_is_negated(text: str, match: re.Match[str]) -> bool:
    prefix = text[max(0, match.start() - 40):match.start()].lower()
    return (
        "no " in prefix[-12:]
        or "not " in prefix[-16:]
        or "forbidden" in prefix[-24:]
        or "claim" in prefix[-20:]
        or "disabled" in prefix[-24:]
        or "unavailable" in prefix[-24:]
    )


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
        f"validate_design_tokens: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"examples: {len(report['examples'])}",
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

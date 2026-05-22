from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1.0"

CONTRACT_PATHS = [
    "contracts/representations/capability_negotiation.v0.json",
    "contracts/representations/host_profile.v0.json",
    "contracts/representations/representation_profile.v0.json",
]
HOST_INVENTORY = "control/inventory/publication/host_profiles.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
CAPABILITY_POLICY = "control/inventory/publication/capability_negotiation_policy.json"
EXAMPLE_HOSTS = "examples/representations/host_profiles/minimal_host_profiles_v0.json"
EXAMPLE_REPRESENTATIONS = "examples/representations/representation_profiles/minimal_representation_profiles_v0.json"
EXAMPLE_CAPABILITY = "examples/representations/capability_negotiation/minimal_capability_negotiation_v0.json"

REQUIRED_SCHEMA_FIELDS = {
    "$schema",
    "$id",
    "title",
    "description",
    "type",
    "required",
    "properties",
}
HOST_INVENTORY_FIELDS = {
    "schema_version",
    "registry_id",
    "contract_ref",
    "profiles",
}
REPRESENTATION_INVENTORY_FIELDS = {
    "schema_version",
    "registry_id",
    "contract_ref",
    "profiles",
}
CAPABILITY_POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "label",
    "description",
    "negotiation_order",
    "allowed_selector_fields",
    "allowed_explicit_params",
    "host_profile_defaults",
    "fallback_profile",
    "forbidden_downgrades",
    "blocked_behaviors",
    "private_state_policy",
    "old_client_safety_policy",
    "no_product_runtime_behavior",
    "notes",
}
HOST_PROFILE_FIELDS = {
    "schema_version",
    "host_profile_id",
    "host_role",
    "label",
    "description",
    "canonical",
    "public_read_only",
    "auth_allowed",
    "default_representation_profile",
    "allowed_representation_profiles",
    "allowed_route_families",
    "forbidden_route_families",
    "https_required",
    "http_allowed",
    "legacy_http_compatible",
    "hsts_allowed",
    "include_subdomains_hsts_allowed",
    "cookie_allowed",
    "credential_allowed",
    "write_actions_allowed",
    "private_data_allowed",
    "api_tokens_allowed",
    "unsafe_actions_allowed",
    "route_identity_policy",
    "no_product_runtime_behavior",
    "notes",
}
REPRESENTATION_PROFILE_FIELDS = {
    "schema_version",
    "representation_profile_id",
    "representation_family",
    "label",
    "media_type",
    "route_usage",
    "javascript_required",
    "css_required",
    "cookie_required",
    "auth_allowed",
    "public_read_only",
    "max_page_weight_kb",
    "supports_forms",
    "supports_tables",
    "supports_images",
    "supports_json",
    "supports_download_manifests",
    "supports_interactive_preview",
    "renderer_status",
    "first_class_projection",
    "future_only",
    "source_evidence_status_meaning_preserved",
    "route_identity_changes_allowed",
    "semantic_requirements",
    "forbidden_omissions",
    "degradation_policy",
    "no_product_runtime_behavior",
    "notes",
}
REQUIRED_HOST_IDS = {
    "api_alias",
    "files_static",
    "localhost_relay_future",
    "nodes_future",
    "old_legacy_read_only",
    "status_static",
    "www_auto",
}
REQUIRED_REPRESENTATION_IDS = {
    "api_json",
    "file_tree",
    "html32",
    "lite_html",
    "manifest_json",
    "native_card_future",
    "relay_future",
    "snapshot_future",
    "standard_html",
    "terminal_future",
    "text",
}
FIRST_CLASS_REQUIRED = {
    "file_tree",
    "lite_html",
    "text",
}
EXPECTED_NEGOTIATION_ORDER = [
    "explicit_url_parameter",
    "user_account_device_preference_future",
    "native_app_relay_capability_manifest_future",
    "host_profile",
    "accept_header",
    "client_hints_future_optional",
    "conservative_user_agent_inference",
    "safest_default",
]
REQUIRED_SELECTOR_FIELDS = {
    "format",
    "profile",
    "skin",
    "density",
    "client",
    "caps",
}
REQUIRED_FORBIDDEN_DOWNGRADES = {
    "automatic_download_installer_execution",
    "automatic_live_source_behavior",
    "auth_on_public_read_only_legacy_host",
    "risk_rights_limitations_hidden",
    "route_identity_change",
    "source_evidence_status_meaning_change",
}
REQUIRED_BLOCKED_BEHAVIORS = {
    "no automatic downloads/installers/execution",
    "no automatic live-source behavior",
    "no auth on public-read-only legacy hosts",
    "no hiding risk/rights/limitations",
    "no route identity changes",
    "no source/evidence/status meaning changes",
}
LEGACY_FALSE_FLAGS = {
    "api_tokens_allowed",
    "auth_allowed",
    "cookie_allowed",
    "credential_allowed",
    "private_data_allowed",
    "unsafe_actions_allowed",
    "write_actions_allowed",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka representation contract schemas, inventories, and examples."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_representation_contracts(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_representation_contracts(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    contracts_checked: list[str] = []
    for relative in CONTRACT_PATHS:
        payload = _load_json(root / relative, errors, root)
        if isinstance(payload, Mapping):
            contracts_checked.append(relative)
            _validate_schema(relative, payload, errors)

    host_inventory = _load_json(root / HOST_INVENTORY, errors, root)
    representation_inventory = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    capability_policy = _load_json(root / CAPABILITY_POLICY, errors, root)
    if (
        isinstance(host_inventory, Mapping)
        and isinstance(representation_inventory, Mapping)
        and isinstance(capability_policy, Mapping)
    ):
        errors.extend(
            validate_payloads(
                host_inventory,
                representation_inventory,
                capability_policy,
                source_label="inventories",
                require_inventory_ids=True,
            )
        )

    example_hosts = _load_json(root / EXAMPLE_HOSTS, errors, root)
    example_representations = _load_json(root / EXAMPLE_REPRESENTATIONS, errors, root)
    example_capability = _load_json(root / EXAMPLE_CAPABILITY, errors, root)
    if (
        isinstance(example_hosts, Mapping)
        and isinstance(example_representations, Mapping)
        and isinstance(example_capability, Mapping)
    ):
        errors.extend(
            validate_payloads(
                example_hosts,
                example_representations,
                example_capability,
                source_label="examples",
                require_inventory_ids=False,
            )
        )

    inventory_host_count = _profile_count(host_inventory)
    inventory_representation_count = _profile_count(representation_inventory)
    example_host_count = _profile_count(example_hosts)
    example_representation_count = _profile_count(example_representations)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "validate_representation_contracts",
        "schema_version": SCHEMA_VERSION,
        "contracts_checked": sorted(contracts_checked),
        "inventories_checked": sorted(
            [HOST_INVENTORY, REPRESENTATION_INVENTORY, CAPABILITY_POLICY]
        ),
        "examples_checked": sorted(
            [EXAMPLE_HOSTS, EXAMPLE_REPRESENTATIONS, EXAMPLE_CAPABILITY]
        ),
        "inventory_host_profile_count": inventory_host_count,
        "inventory_representation_profile_count": inventory_representation_count,
        "example_host_profile_count": example_host_count,
        "example_representation_profile_count": example_representation_count,
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }


def validate_payloads(
    host_inventory: Mapping[str, Any],
    representation_inventory: Mapping[str, Any],
    capability_policy: Mapping[str, Any],
    *,
    source_label: str,
    require_inventory_ids: bool,
) -> list[str]:
    errors: list[str] = []
    representation_ids = _validate_representation_inventory(
        source_label,
        representation_inventory,
        errors,
        require_inventory_ids=require_inventory_ids,
    )
    host_ids = _validate_host_inventory(
        source_label,
        host_inventory,
        representation_ids,
        errors,
        require_inventory_ids=require_inventory_ids,
    )
    _validate_capability_policy(
        source_label,
        capability_policy,
        host_inventory,
        host_ids,
        representation_ids,
        errors,
    )
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

    schema_version = _mapping(_mapping(payload.get("properties")).get("schema_version"))
    if schema_version.get("const") != SCHEMA_VERSION:
        errors.append(f"{relative}: schema_version const must be {SCHEMA_VERSION}.")

    required_fields = set(required) if isinstance(required, list) else set()
    if relative.endswith("host_profile.v0.json"):
        missing_required = sorted(HOST_PROFILE_FIELDS - required_fields)
    elif relative.endswith("representation_profile.v0.json"):
        missing_required = sorted(REPRESENTATION_PROFILE_FIELDS - required_fields)
    else:
        missing_required = sorted(CAPABILITY_POLICY_FIELDS - required_fields)
    if missing_required:
        errors.append(f"{relative}: required list missing {missing_required}.")


def _validate_host_inventory(
    source_label: str,
    payload: Mapping[str, Any],
    representation_ids: set[str],
    errors: list[str],
    *,
    require_inventory_ids: bool,
) -> set[str]:
    _require_fields(f"{source_label}: host_profiles", payload, HOST_INVENTORY_FIELDS, errors)
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{source_label}: host_profiles schema_version must be {SCHEMA_VERSION}.")
    profiles = payload.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        errors.append(f"{source_label}: host_profiles profiles must be a non-empty list.")
        return set()

    host_ids: set[str] = set()
    for index, profile in enumerate(profiles):
        label = f"{source_label}: host_profiles[{index}]"
        if not isinstance(profile, Mapping):
            errors.append(f"{label}: profile must be an object.")
            continue
        profile_id = profile.get("host_profile_id")
        if isinstance(profile_id, str):
            if profile_id in host_ids:
                errors.append(f"{label}: duplicate host_profile_id {profile_id}.")
            host_ids.add(profile_id)
            label = f"{source_label}: host_profile {profile_id}"
        _require_fields(label, profile, HOST_PROFILE_FIELDS, errors)
        if profile.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}.")
        if profile.get("no_product_runtime_behavior") is not True:
            errors.append(f"{label}: no_product_runtime_behavior must be true.")

        allowed = set(_string_list(profile.get("allowed_representation_profiles")))
        default = profile.get("default_representation_profile")
        if isinstance(default, str):
            if default not in allowed:
                errors.append(f"{label}: default representation profile must be allowed.")
            if default not in representation_ids:
                errors.append(f"{label}: default representation profile {default} is not registered.")
        for representation_id in sorted(allowed):
            if representation_id not in representation_ids:
                errors.append(
                    f"{label}: allowed representation profile {representation_id} is not registered."
                )

        if _is_legacy_or_http_compatible(profile):
            if profile.get("public_read_only") is not True:
                errors.append(f"{label}: legacy/http-compatible profiles must be public-read-only.")
            for flag in sorted(LEGACY_FALSE_FLAGS):
                if profile.get(flag) is not False:
                    errors.append(
                        f"{label}: legacy/http-compatible profile must not allow {flag}."
                    )
            forbidden_routes = set(_string_list(profile.get("forbidden_route_families")))
            for family in ("account", "download", "live_probe", "private_data", "write"):
                if family not in forbidden_routes:
                    errors.append(
                        f"{label}: legacy/http-compatible profile must forbid route family {family}."
                    )

    if require_inventory_ids:
        missing = sorted(REQUIRED_HOST_IDS - host_ids)
        if missing:
            errors.append(f"{source_label}: host_profiles missing required profiles {missing}.")
    return host_ids


def _validate_representation_inventory(
    source_label: str,
    payload: Mapping[str, Any],
    errors: list[str],
    *,
    require_inventory_ids: bool,
) -> set[str]:
    _require_fields(
        f"{source_label}: representation_profiles",
        payload,
        REPRESENTATION_INVENTORY_FIELDS,
        errors,
    )
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"{source_label}: representation_profiles schema_version must be {SCHEMA_VERSION}."
        )
    profiles = payload.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        errors.append(
            f"{source_label}: representation_profiles profiles must be a non-empty list."
        )
        return set()

    representation_ids: set[str] = set()
    for index, profile in enumerate(profiles):
        label = f"{source_label}: representation_profiles[{index}]"
        if not isinstance(profile, Mapping):
            errors.append(f"{label}: profile must be an object.")
            continue
        profile_id = profile.get("representation_profile_id")
        if isinstance(profile_id, str):
            if profile_id in representation_ids:
                errors.append(f"{label}: duplicate representation_profile_id {profile_id}.")
            representation_ids.add(profile_id)
            label = f"{source_label}: representation_profile {profile_id}"
        _require_fields(label, profile, REPRESENTATION_PROFILE_FIELDS, errors)
        if profile.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}.")
        if profile.get("source_evidence_status_meaning_preserved") is not True:
            errors.append(f"{label}: source/evidence/status meaning must be preserved.")
        if profile.get("route_identity_changes_allowed") is not False:
            errors.append(f"{label}: route identity changes must be forbidden.")
        if profile.get("no_product_runtime_behavior") is not True:
            errors.append(f"{label}: no_product_runtime_behavior must be true.")
        if not _non_empty_string_list(profile.get("semantic_requirements")):
            errors.append(f"{label}: semantic_requirements must be a non-empty list.")
        if not _non_empty_string_list(profile.get("forbidden_omissions")):
            errors.append(f"{label}: forbidden_omissions must be a non-empty list.")
        if profile_id in FIRST_CLASS_REQUIRED and profile.get("first_class_projection") is not True:
            errors.append(f"{label}: {profile_id} must be recorded as a first-class projection.")

    for profile in profiles:
        if not isinstance(profile, Mapping):
            continue
        label = f"{source_label}: representation_profile {profile.get('representation_profile_id', '<unknown>')}"
        degradation = _mapping(profile.get("degradation_policy"))
        if degradation.get("must_preserve_semantics") is not True:
            errors.append(f"{label}: degradation_policy.must_preserve_semantics must be true.")
        for fallback_id in sorted(_string_list(degradation.get("fallback_profile_ids"))):
            if fallback_id not in representation_ids:
                errors.append(f"{label}: fallback profile {fallback_id} is not registered.")

    if require_inventory_ids:
        missing = sorted(REQUIRED_REPRESENTATION_IDS - representation_ids)
        if missing:
            errors.append(
                f"{source_label}: representation_profiles missing required profiles {missing}."
            )
    return representation_ids


def _validate_capability_policy(
    source_label: str,
    payload: Mapping[str, Any],
    host_inventory: Mapping[str, Any],
    host_ids: set[str],
    representation_ids: set[str],
    errors: list[str],
) -> None:
    label = f"{source_label}: capability_negotiation_policy"
    _require_fields(label, payload, CAPABILITY_POLICY_FIELDS, errors)
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}.")
    if payload.get("negotiation_order") != EXPECTED_NEGOTIATION_ORDER:
        errors.append(f"{label}: negotiation_order must match the Track A priority order.")
    for field_name in ("allowed_selector_fields", "allowed_explicit_params"):
        values = set(_string_list(payload.get(field_name)))
        missing = sorted(REQUIRED_SELECTOR_FIELDS - values)
        if missing:
            errors.append(f"{label}: {field_name} missing {missing}.")
    fallback = payload.get("fallback_profile")
    if fallback not in representation_ids:
        errors.append(f"{label}: fallback profile {fallback!r} is not registered.")

    defaults = payload.get("host_profile_defaults")
    if not isinstance(defaults, Mapping):
        errors.append(f"{label}: host_profile_defaults must be an object.")
    else:
        missing_hosts = sorted(host_ids - set(defaults))
        if missing_hosts:
            errors.append(f"{label}: host_profile_defaults missing hosts {missing_hosts}.")
        host_defaults = _host_defaults(host_inventory)
        for host_id, representation_id in sorted(defaults.items()):
            if host_id not in host_ids:
                errors.append(f"{label}: host_profile_defaults references unknown host {host_id}.")
            if representation_id not in representation_ids:
                errors.append(
                    f"{label}: host_profile_defaults.{host_id} references unknown representation {representation_id}."
                )
            expected = host_defaults.get(host_id)
            if expected and representation_id != expected:
                errors.append(
                    f"{label}: host_profile_defaults.{host_id} must match host default {expected}."
                )

    forbidden = set(_string_list(payload.get("forbidden_downgrades")))
    missing_forbidden = sorted(REQUIRED_FORBIDDEN_DOWNGRADES - forbidden)
    if missing_forbidden:
        errors.append(f"{label}: forbidden_downgrades missing {missing_forbidden}.")

    blocked = set(_string_list(payload.get("blocked_behaviors")))
    missing_blocked = sorted(REQUIRED_BLOCKED_BEHAVIORS - blocked)
    if missing_blocked:
        errors.append(f"{label}: blocked_behaviors missing {missing_blocked}.")

    private_state = _mapping(payload.get("private_state_policy"))
    for key in (
        "enabled_now",
        "user_account_preferences_enabled",
        "device_preferences_enabled",
        "private_data_allowed",
        "cookies_required",
    ):
        if private_state.get(key) is not False:
            errors.append(f"{label}: private_state_policy.{key} must be false.")

    old_client = _mapping(payload.get("old_client_safety_policy"))
    if old_client.get("public_read_only_only") is not True:
        errors.append(f"{label}: old_client_safety_policy.public_read_only_only must be true.")
    for key in (
        "auth_allowed",
        "cookies_allowed",
        "credentials_allowed",
        "account_actions_allowed",
        "writes_allowed",
        "private_data_allowed",
        "api_tokens_allowed",
        "unsafe_actions_allowed",
    ):
        if old_client.get(key) is not False:
            errors.append(f"{label}: old_client_safety_policy.{key} must be false.")

    if payload.get("no_product_runtime_behavior") is not True:
        errors.append(f"{label}: no_product_runtime_behavior must be true.")


def _host_defaults(host_inventory: Mapping[str, Any]) -> dict[str, str]:
    defaults: dict[str, str] = {}
    profiles = host_inventory.get("profiles")
    if not isinstance(profiles, list):
        return defaults
    for profile in profiles:
        if not isinstance(profile, Mapping):
            continue
        host_id = profile.get("host_profile_id")
        default = profile.get("default_representation_profile")
        if isinstance(host_id, str) and isinstance(default, str):
            defaults[host_id] = default
    return defaults


def _is_legacy_or_http_compatible(profile: Mapping[str, Any]) -> bool:
    return bool(
        profile.get("legacy_http_compatible") is True
        or profile.get("http_allowed") is True
        or profile.get("host_role") in {"legacy_web", "local_relay_future"}
    )


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


def _profile_count(payload: Any) -> int:
    if isinstance(payload, Mapping) and isinstance(payload.get("profiles"), list):
        return len(payload["profiles"])
    return 0


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _non_empty_string_list(value: Any) -> bool:
    return bool(_string_list(value))


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Representation contract validation",
        f"status: {report['status']}",
        f"contracts_checked: {len(report['contracts_checked'])}",
        f"inventory_host_profiles: {report['inventory_host_profile_count']}",
        f"inventory_representation_profiles: {report['inventory_representation_profile_count']}",
        f"example_host_profiles: {report['example_host_profile_count']}",
        f"example_representation_profiles: {report['example_representation_profile_count']}",
    ]
    for error in report.get("errors", []):
        lines.append(f"ERROR: {error}")
    for warning in report.get("warnings", []):
        lines.append(f"WARN: {warning}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

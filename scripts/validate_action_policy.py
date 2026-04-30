from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
POLICY = PUBLICATION_DIR / "action_policy.json"
NATIVE_CONTRACT = PUBLICATION_DIR / "native_client_contract.json"
SNAPSHOT_CONSUMER_CONTRACT = PUBLICATION_DIR / "snapshot_consumer_contract.json"
RELAY_SURFACE = PUBLICATION_DIR / "relay_surface.json"
PUBLIC_SITE_LIMITATIONS = REPO_ROOT / "site/dist" / "limitations.html"

REQUIRED_FIELDS = {
    "schema_version",
    "action_policy_id",
    "status",
    "stability",
    "no_install_automation_implemented",
    "no_download_surface_implemented",
    "no_malware_scanning_claim",
    "no_rights_clearance_claim",
    "current_safe_actions",
    "current_bounded_actions",
    "future_gated_actions",
    "prohibited_until_policy",
    "action_classes",
    "required_evidence_fields",
    "required_user_confirmations",
    "required_warning_classes",
    "public_alpha_defaults",
    "static_site_defaults",
    "native_client_requirements",
    "snapshot_consumer_requirements",
    "relay_requirements",
    "rights_policy_dependency",
    "security_policy_dependency",
    "created_by_slice",
    "notes",
}
SAFE_ACTIONS = {
    "inspect",
    "preview",
    "read",
    "cite",
    "export_manifest",
    "view_provenance",
    "compare",
    "view_absence_report",
    "view_source",
}
BOUNDED_ACTIONS = {
    "fetch_fixture_payload",
    "member_preview",
    "local_export_manifest",
    "local_store_artifact_fixture",
}
FUTURE_GATED_ACTIONS = {
    "download",
    "download_member",
    "mirror",
    "install_handoff",
    "package_manager_handoff",
    "emulator_handoff",
    "vm_handoff",
    "restore_manifest_apply",
    "uninstall",
    "rollback",
    "execute",
    "scan_for_malware",
    "quarantine",
    "submit_feedback",
    "upload_local_source",
}
PROHIBITED_ACTIONS = {
    "silent_install",
    "auto_execute",
    "privileged_install",
    "destructive_restore",
    "write_to_system_paths",
    "upload_private_files",
    "send_private_inventory",
    "bypass_rights_warning",
    "bypass_hash_warning",
}
RISKY_DEFAULT_FLAGS = {
    "downloads_enabled",
    "install_handoff_enabled",
    "package_manager_handoff_enabled",
    "mirror_enabled",
    "execute_enabled",
    "malware_scanning_enabled",
    "rights_clearance_claimed",
}
REQUIRED_DOCS = {
    "docs/reference/ACTION_DOWNLOAD_INSTALL_POLICY.md": [
        "This is policy and contract work only",
        "Install automation is not implemented and remains prohibited",
        "No malware safety claim exists",
        "No rights clearance claim exists",
        "Public-alpha defaults are read-only and metadata-first",
    ],
    "docs/reference/EXECUTABLE_RISK_POLICY.md": [
        "Eureka does not scan executables",
        "hashes do not prove safety",
        "Fixture `.exe.txt` files are text fixtures",
        "No malware safety claim exists",
    ],
    "docs/reference/RIGHTS_AND_ACCESS_POLICY.md": [
        "Source metadata is not rights clearance",
        "No rights clearance claim exists",
        "not a software mirror",
    ],
    "docs/reference/INSTALL_HANDOFF_CONTRACT.md": [
        "Install handoff is user-initiated delegation",
        "not silent installation",
        "The user must explicitly confirm",
        "This contract does not implement",
    ],
}
FORBIDDEN_POSITIVE_PATTERNS = (
    re.compile(r"\bmalware[- ]safe\b", re.IGNORECASE),
    re.compile(r"\bsafe to execute\b", re.IGNORECASE),
    re.compile(r"\bclean executable\b", re.IGNORECASE),
    re.compile(r"\brights cleared\b", re.IGNORECASE),
    re.compile(r"\bcleared for distribution\b", re.IGNORECASE),
    re.compile(r"\bdownload(s)? (are|is) enabled\b", re.IGNORECASE),
    re.compile(r"\binstall automation (is )?implemented\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Native Action / Download / Install Policy v0."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_action_policy(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_action_policy(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    publication_dir = repo_root / "control" / "inventory" / "publication"

    policy = _load_json(publication_dir / "action_policy.json", repo_root, errors)
    native = _load_json(publication_dir / "native_client_contract.json", repo_root, errors)
    snapshot = _load_json(publication_dir / "snapshot_consumer_contract.json", repo_root, errors)
    relay = _load_json(publication_dir / "relay_surface.json", repo_root, errors)

    _validate_policy(policy, errors)
    _validate_related_inventories(native, snapshot, relay, errors)
    _validate_docs(repo_root, errors)
    _validate_public_static_limitations(repo_root, errors)

    action_counts = {
        "current_safe": len(_mapping_list(_mapping(policy).get("current_safe_actions"))),
        "current_bounded": len(_mapping_list(_mapping(policy).get("current_bounded_actions"))),
        "future_gated": len(_list(_mapping(policy).get("future_gated_actions"))),
        "prohibited": len(_list(_mapping(policy).get("prohibited_until_policy"))),
    }
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "action_policy_validator_v0",
        "policy": "control/inventory/publication/action_policy.json",
        "action_counts": action_counts,
        "public_alpha_risky_actions_enabled": _risky_flags_enabled(
            _mapping(_mapping(policy).get("public_alpha_defaults"))
        ),
        "static_site_risky_actions_enabled": _risky_flags_enabled(
            _mapping(_mapping(policy).get("static_site_defaults"))
        ),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_policy(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("action_policy.json: must be a JSON object.")
        return
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        errors.append(f"action_policy.json: missing fields {missing}.")
    expected = {
        "schema_version": "0.1.0",
        "action_policy_id": "eureka-native-action-download-install-policy",
        "status": "policy_only",
        "stability": "experimental",
        "no_install_automation_implemented": True,
        "no_download_surface_implemented": True,
        "no_malware_scanning_claim": True,
        "no_rights_clearance_claim": True,
        "created_by_slice": "native_action_download_install_policy_v0",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"action_policy.json: {key} must be {value!r}.")

    safe = {str(item.get("id")) for item in _mapping_list(payload.get("current_safe_actions"))}
    bounded = {str(item.get("id")) for item in _mapping_list(payload.get("current_bounded_actions"))}
    future = {str(item) for item in _list(payload.get("future_gated_actions"))}
    prohibited = {str(item) for item in _list(payload.get("prohibited_until_policy"))}
    classes = _by_id(payload.get("action_classes"))
    warnings = {str(item) for item in _list(payload.get("required_warning_classes"))}

    for label, expected_ids, actual_ids in (
        ("current_safe_actions", SAFE_ACTIONS, safe),
        ("current_bounded_actions", BOUNDED_ACTIONS, bounded),
        ("future_gated_actions", FUTURE_GATED_ACTIONS, future),
        ("prohibited_until_policy", PROHIBITED_ACTIONS, prohibited),
    ):
        missing_ids = sorted(expected_ids - actual_ids)
        if missing_ids:
            errors.append(f"action_policy.json: {label} missing {missing_ids}.")

    for class_id in (
        "safe_read_only",
        "bounded_local_artifact",
        "future_download_or_mirror",
        "future_install_or_execute",
        "future_private_or_write",
    ):
        if class_id not in classes:
            errors.append(f"action_policy.json: action_classes missing {class_id}.")
    for class_id in ("future_download_or_mirror", "future_install_or_execute", "future_private_or_write"):
        class_record = _mapping(classes.get(class_id))
        if class_record.get("allowed_now") is not False:
            errors.append(f"action_policy.json: {class_id}.allowed_now must be false.")
        if class_record.get("requires_user_confirmation") is not True:
            errors.append(f"action_policy.json: {class_id}.requires_user_confirmation must be true.")

    for defaults_name in ("public_alpha_defaults", "static_site_defaults"):
        defaults = _mapping(payload.get(defaults_name))
        for flag in sorted(RISKY_DEFAULT_FLAGS):
            if defaults.get(flag) is not False:
                errors.append(f"action_policy.json: {defaults_name}.{flag} must be false.")

    for required_warning in (
        "malware_scanning_not_available",
        "rights_clearance_not_available",
        "hash_identity_not_safety",
        "public_alpha_risky_actions_disabled",
        "static_site_no_download_or_install_surface",
    ):
        if required_warning not in warnings:
            errors.append(f"action_policy.json: required_warning_classes missing {required_warning}.")

    rights = _mapping(payload.get("rights_policy_dependency"))
    if rights.get("rights_clearance_claimed") is not False:
        errors.append("action_policy.json: rights_policy_dependency.rights_clearance_claimed must be false.")
    security = _mapping(payload.get("security_policy_dependency"))
    if security.get("malware_scanning_claimed") is not False:
        errors.append("action_policy.json: security_policy_dependency.malware_scanning_claimed must be false.")
    if security.get("executable_safety_claimed") is not False:
        errors.append("action_policy.json: security_policy_dependency.executable_safety_claimed must be false.")


def _validate_related_inventories(native: Any, snapshot: Any, relay: Any, errors: list[str]) -> None:
    native_text = json.dumps(native, sort_keys=True).casefold()
    for phrase in ("action_policy_dependency", "native action / download / install policy v0"):
        if phrase not in native_text:
            errors.append(f"native_client_contract.json: missing {phrase}.")
    dependency = _mapping(_mapping(native).get("action_policy_dependency"))
    if dependency.get("downloads_enabled") is not False:
        errors.append("native_client_contract.json: action_policy_dependency.downloads_enabled must be false.")
    if dependency.get("install_automation_enabled") is not False:
        errors.append(
            "native_client_contract.json: action_policy_dependency.install_automation_enabled must be false."
        )
    if dependency.get("malware_scanning_claimed") is not False:
        errors.append("native_client_contract.json: action_policy_dependency.malware_scanning_claimed must be false.")
    if dependency.get("rights_clearance_claimed") is not False:
        errors.append("native_client_contract.json: action_policy_dependency.rights_clearance_claimed must be false.")

    snapshot_text = json.dumps(snapshot, sort_keys=True).casefold()
    for phrase in ("action_policy_dependency", "download permission", "install permission", "rights clearance"):
        if phrase not in snapshot_text:
            errors.append(f"snapshot_consumer_contract.json: missing {phrase}.")

    relay_text = json.dumps(relay, sort_keys=True).casefold()
    for phrase in ("action_policy_dependency", "downloads_enabled", "install_automation_enabled"):
        if phrase not in relay_text:
            errors.append(f"relay_surface.json: missing {phrase}.")
    relay_dependency = _mapping(_mapping(relay).get("action_policy_dependency"))
    for flag in ("downloads_enabled", "install_automation_enabled", "mirror_enabled", "execute_enabled", "private_uploads_enabled"):
        if relay_dependency.get(flag) is not False:
            errors.append(f"relay_surface.json: action_policy_dependency.{flag} must be false.")


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    combined_parts: list[str] = []
    for relative, phrases in REQUIRED_DOCS.items():
        path = repo_root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{relative}: required action policy document is missing.")
            continue
        combined_parts.append(text)
        lowered = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in lowered:
                errors.append(f"{relative}: missing phrase {phrase!r}.")

    for relative in (
        "docs/reference/NATIVE_CLIENT_CONTRACT.md",
        "docs/reference/SNAPSHOT_CONSUMER_CONTRACT.md",
        "docs/reference/RELAY_SURFACE_CONTRACT.md",
        "docs/operations/PUBLIC_ALPHA_SAFE_MODE.md",
        "docs/architecture/ACTION_ROUTER.md",
    ):
        path = repo_root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{relative}: related policy document is missing.")
            continue
        combined_parts.append(text)
        if "Native Action / Download / Install Policy v0" not in text:
            errors.append(f"{relative}: must reference Native Action / Download / Install Policy v0.")

    combined = "\n".join(combined_parts)
    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        for match in pattern.finditer(combined):
            context = combined[max(0, match.start() - 90) : match.end() + 90].casefold()
            if any(
                token in context
                for token in (
                    "no ",
                    "not ",
                    "does not",
                    "must not",
                    "without",
                    "is not",
                    "not a",
                    "not implement",
                    "not implemented",
                )
            ):
                continue
            errors.append(f"action policy docs include forbidden positive claim {match.group(0)!r}.")


def _validate_public_static_limitations(repo_root: Path, errors: list[str]) -> None:
    path = repo_root / "site/dist" / "limitations.html"
    try:
        text = path.read_text(encoding="utf-8").casefold()
    except FileNotFoundError:
        errors.append("site/dist/limitations.html: file is missing.")
        return
    for phrase in ("no installer automation", "no", "download"):
        if phrase not in text:
            errors.append(f"site/dist/limitations.html: missing action-policy limitation phrase {phrase!r}.")
    for forbidden in ("app store workflow is available", "installer available", "downloads are enabled"):
        if forbidden in text:
            errors.append(f"site/dist/limitations.html: forbidden static-site claim {forbidden!r}.")


def _risky_flags_enabled(defaults: Mapping[str, Any]) -> list[str]:
    return sorted(flag for flag in RISKY_DEFAULT_FLAGS if defaults.get(flag) is True)


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: missing JSON file.")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {error}.")
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _by_id(value: Any) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    if not isinstance(value, list):
        return result
    for item in value:
        if isinstance(item, Mapping) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def _format_plain(report: Mapping[str, Any]) -> str:
    counts = _mapping(report.get("action_counts"))
    lines = [
        "Action policy validation",
        f"status: {report['status']}",
        f"current_safe_actions: {counts.get('current_safe')}",
        f"current_bounded_actions: {counts.get('current_bounded')}",
        f"future_gated_actions: {counts.get('future_gated')}",
        f"prohibited_actions: {counts.get('prohibited')}",
        f"public_alpha_risky_actions_enabled: {len(_list(report.get('public_alpha_risky_actions_enabled')))}",
        f"static_site_risky_actions_enabled: {len(_list(report.get('static_site_risky_actions_enabled')))}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())

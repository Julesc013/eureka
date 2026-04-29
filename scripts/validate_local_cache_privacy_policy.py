from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
POLICY = PUBLICATION_DIR / "local_cache_privacy_policy.json"
NATIVE_CONTRACT = PUBLICATION_DIR / "native_client_contract.json"
RELAY_SURFACE = PUBLICATION_DIR / "relay_surface.json"
SNAPSHOT_CONSUMER = PUBLICATION_DIR / "snapshot_consumer_contract.json"
PUBLIC_SITE_LIMITATIONS = REPO_ROOT / "public_site" / "limitations.html"

REQUIRED_FIELDS = {
    "schema_version",
    "policy_id",
    "status",
    "stability",
    "no_cache_runtime_implemented",
    "no_private_ingestion_implemented",
    "no_telemetry_implemented",
    "no_accounts_implemented",
    "no_cloud_sync_implemented",
    "privacy_default",
    "public_cache_policy",
    "private_cache_policy",
    "local_path_policy",
    "user_state_policy",
    "resolution_memory_policy",
    "telemetry_policy",
    "logging_policy",
    "diagnostics_policy",
    "credential_policy",
    "deletion_reset_policy",
    "export_policy",
    "portable_mode_policy",
    "relay_policy",
    "snapshot_policy",
    "native_client_requirements",
    "prohibited_behaviors",
    "created_by_slice",
    "notes",
}

PROHIBITED_BEHAVIORS = {
    "automatic_local_archive_scan",
    "private_file_ingestion_by_default",
    "private_uploads",
    "telemetry_by_default",
    "analytics_by_default",
    "cloud_sync_by_default",
    "public_path_leakage",
    "credential_export",
    "old_client_private_relay",
    "private_data_over_insecure_transport",
}

REQUIRED_DOCS = {
    "docs/reference/LOCAL_CACHE_PRIVACY_POLICY.md": [
        "policy and contract work only",
        "No telemetry is implemented",
        "no local archive scanning by default",
        "no private paths in public reports",
        "Deletion, Reset, Export",
    ],
    "docs/reference/NATIVE_LOCAL_CACHE_CONTRACT.md": [
        "does not create cache code",
        "Native clients must not automatically scan user directories",
        "clear public cache",
        "clear private cache",
        "future requirements, not implemented behavior",
    ],
    "docs/reference/TELEMETRY_AND_LOGGING_POLICY.md": [
        "Telemetry is not implemented",
        "Telemetry must be off by default",
        "Manual external observations are user-entered records, not telemetry",
        "No account system exists",
    ],
}

FORBIDDEN_PUBLIC_SITE_PATTERNS = (
    re.compile(r"\baccounts? (are|is) (available|enabled|implemented)\b", re.IGNORECASE),
    re.compile(r"\btelemetry (is )?(available|enabled|implemented)\b", re.IGNORECASE),
    re.compile(r"\banalytics (are|is) (available|enabled|implemented)\b", re.IGNORECASE),
    re.compile(r"\bcloud sync (is )?(available|enabled|implemented)\b", re.IGNORECASE),
    re.compile(r"\bprivate cache (is )?(available|enabled|implemented)\b", re.IGNORECASE),
    re.compile(r"\blocal cache runtime (is )?(available|enabled|implemented)\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Native Local Cache / Privacy Policy v0."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_local_cache_privacy_policy(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_local_cache_privacy_policy(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    publication_dir = repo_root / "control" / "inventory" / "publication"

    policy = _load_json(publication_dir / "local_cache_privacy_policy.json", repo_root, errors)
    native = _load_json(publication_dir / "native_client_contract.json", repo_root, errors)
    relay = _load_json(publication_dir / "relay_surface.json", repo_root, errors)
    snapshot = _load_json(publication_dir / "snapshot_consumer_contract.json", repo_root, errors)

    _validate_policy(policy, errors)
    _validate_related_inventories(native, relay, snapshot, errors)
    _validate_docs(repo_root, errors)
    _validate_public_alpha_path_safety(repo_root, errors)
    _validate_public_site_limitations(repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "local_cache_privacy_policy_validator_v0",
        "policy": "control/inventory/publication/local_cache_privacy_policy.json",
        "privacy_default": _mapping(policy).get("privacy_default"),
        "no_cache_runtime_implemented": _mapping(policy).get("no_cache_runtime_implemented"),
        "no_private_ingestion_implemented": _mapping(policy).get("no_private_ingestion_implemented"),
        "no_telemetry_implemented": _mapping(policy).get("no_telemetry_implemented"),
        "no_accounts_implemented": _mapping(policy).get("no_accounts_implemented"),
        "no_cloud_sync_implemented": _mapping(policy).get("no_cloud_sync_implemented"),
        "prohibited_behavior_count": len(_list(_mapping(policy).get("prohibited_behaviors"))),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_policy(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("local_cache_privacy_policy.json: must be a JSON object.")
        return
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        errors.append(f"local_cache_privacy_policy.json: missing fields {missing}.")
    expected = {
        "schema_version": "0.1.0",
        "policy_id": "eureka-native-local-cache-privacy-policy",
        "status": "policy_only",
        "stability": "experimental",
        "no_cache_runtime_implemented": True,
        "no_private_ingestion_implemented": True,
        "no_telemetry_implemented": True,
        "no_accounts_implemented": True,
        "no_cloud_sync_implemented": True,
        "privacy_default": "local_private_off_by_default",
        "created_by_slice": "native_local_cache_privacy_policy_v0",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"local_cache_privacy_policy.json: {key} must be {value!r}.")

    prohibited = {str(item) for item in _list(payload.get("prohibited_behaviors"))}
    missing_prohibited = sorted(PROHIBITED_BEHAVIORS - prohibited)
    if missing_prohibited:
        errors.append(
            f"local_cache_privacy_policy.json: prohibited_behaviors missing {missing_prohibited}."
        )

    if _mapping(payload.get("private_cache_policy")).get("enabled_by_default") is not False:
        errors.append("local_cache_privacy_policy.json: private_cache_policy.enabled_by_default must be false.")
    if _mapping(payload.get("local_path_policy")).get("private_paths_in_public_reports") is not False:
        errors.append("local_cache_privacy_policy.json: private paths in public reports must be false.")
    if _mapping(payload.get("telemetry_policy")).get("implemented") is not False:
        errors.append("local_cache_privacy_policy.json: telemetry_policy.implemented must be false.")
    if _mapping(payload.get("telemetry_policy")).get("default_enabled") is not False:
        errors.append("local_cache_privacy_policy.json: telemetry_policy.default_enabled must be false.")
    if _mapping(payload.get("diagnostics_policy")).get("default_upload_enabled") is not False:
        errors.append("local_cache_privacy_policy.json: diagnostics default upload must be false.")
    if _mapping(payload.get("credential_policy")).get("credential_export_allowed") is not False:
        errors.append("local_cache_privacy_policy.json: credential export must be false.")
    if _mapping(payload.get("relay_policy")).get("old_client_private_relay_allowed") is not False:
        errors.append("local_cache_privacy_policy.json: old-client private relay must be false.")
    if _mapping(payload.get("snapshot_policy")).get("snapshots_include_private_data") is not False:
        errors.append("local_cache_privacy_policy.json: snapshots_include_private_data must be false.")
    if _mapping(payload.get("deletion_reset_policy")).get("implemented_now") is not False:
        errors.append("local_cache_privacy_policy.json: deletion/reset controls must be future, not implemented.")


def _validate_related_inventories(native: Any, relay: Any, snapshot: Any, errors: list[str]) -> None:
    for label, payload in (
        ("native_client_contract.json", native),
        ("relay_surface.json", relay),
        ("snapshot_consumer_contract.json", snapshot),
    ):
        dependency = _mapping(_mapping(payload).get("local_cache_privacy_policy_dependency"))
        if dependency.get("policy") != "control/inventory/publication/local_cache_privacy_policy.json":
            errors.append(f"{label}: must reference local_cache_privacy_policy.json.")
        if dependency.get("status") != "policy_only":
            errors.append(f"{label}: local cache/privacy dependency must be policy_only.")

    native_dependency = _mapping(_mapping(native).get("local_cache_privacy_policy_dependency"))
    for flag in (
        "local_cache_runtime_implemented",
        "private_ingestion_implemented",
        "telemetry_implemented",
        "accounts_implemented",
        "cloud_sync_implemented",
    ):
        if native_dependency.get(flag) is not False:
            errors.append(f"native_client_contract.json: {flag} must be false.")

    relay_dependency = _mapping(_mapping(relay).get("local_cache_privacy_policy_dependency"))
    if relay_dependency.get("private_data_through_old_clients_by_default") is not False:
        errors.append("relay_surface.json: private data through old clients must be false.")
    if relay_dependency.get("telemetry_enabled") is not False:
        errors.append("relay_surface.json: telemetry must remain disabled.")
    if relay_dependency.get("credentials_to_old_clients") is not False:
        errors.append("relay_surface.json: credentials to old clients must be false.")

    snapshot_dependency = _mapping(_mapping(snapshot).get("local_cache_privacy_policy_dependency"))
    for flag in (
        "snapshots_include_private_data",
        "snapshots_include_secrets",
        "telemetry_enabled",
        "private_cache_runtime_implemented",
    ):
        if snapshot_dependency.get(flag) is not False:
            errors.append(f"snapshot_consumer_contract.json: {flag} must be false.")


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    for relative_path, phrases in REQUIRED_DOCS.items():
        path = repo_root / relative_path
        if not path.is_file():
            errors.append(f"{relative_path}: missing required doc.")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative_path}: missing phrase {phrase!r}.")

    related_docs = {
        "docs/reference/NATIVE_CLIENT_CONTRACT.md": [
            "Native Local Cache / Privacy Policy v0",
            "must not scan local archives",
        ],
        "docs/reference/RELAY_SECURITY_AND_PRIVACY.md": [
            "No private cache or diagnostics data to old clients by default",
            "No telemetry or analytics through relay surfaces by default",
        ],
        "docs/architecture/RELAY_SURFACE.md": [
            "must not expose private cache",
            "old or insecure clients by default",
        ],
        "docs/operations/PUBLIC_ALPHA_SAFE_MODE.md": [
            "does not enable private cache",
            "private path exposure",
        ],
    }
    for relative_path, phrases in related_docs.items():
        path = repo_root / relative_path
        if not path.is_file():
            errors.append(f"{relative_path}: missing related doc.")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative_path}: missing phrase {phrase!r}.")


def _validate_public_alpha_path_safety(repo_root: Path, errors: list[str]) -> None:
    safe_mode = repo_root / "docs" / "operations" / "PUBLIC_ALPHA_SAFE_MODE.md"
    if not safe_mode.is_file():
        errors.append("docs/operations/PUBLIC_ALPHA_SAFE_MODE.md: missing.")
        return
    text = safe_mode.read_text(encoding="utf-8")
    for phrase in (
        "blocks caller-provided local filesystem controls",
        "must not expose private local paths",
        "does not enable private cache",
        "private path exposure",
    ):
        if phrase not in text:
            errors.append(f"PUBLIC_ALPHA_SAFE_MODE.md: missing path/privacy phrase {phrase!r}.")


def _validate_public_site_limitations(repo_root: Path, errors: list[str]) -> None:
    path = repo_root / "public_site" / "limitations.html"
    if not path.is_file():
        errors.append("public_site/limitations.html: missing.")
        return
    text = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_PUBLIC_SITE_PATTERNS:
        if pattern.search(text):
            errors.append(f"public_site/limitations.html: forbidden positive claim {pattern.pattern!r}.")


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_display_path(path, repo_root)}: missing JSON file.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_display_path(path, repo_root)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
    return None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Native Local Cache / Privacy Policy validation",
        f"status: {report['status']}",
        f"privacy_default: {report.get('privacy_default')}",
        f"no_cache_runtime_implemented: {report.get('no_cache_runtime_implemented')}",
        f"no_private_ingestion_implemented: {report.get('no_private_ingestion_implemented')}",
        f"no_telemetry_implemented: {report.get('no_telemetry_implemented')}",
        f"no_accounts_implemented: {report.get('no_accounts_implemented')}",
        f"no_cloud_sync_implemented: {report.get('no_cloud_sync_implemented')}",
        f"prohibited_behaviors: {report.get('prohibited_behavior_count')}",
    ]
    for key in ("errors", "warnings"):
        values = _list(report.get(key))
        if values:
            lines.append(f"{key}:")
            lines.extend(f"- {value}" for value in values)
    return "\n".join(lines) + "\n"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

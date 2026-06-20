"""Local-only portable preview bundle manifest and validation helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

from runtime.index.preview.index import PREVIEW_INDEX_SCHEMA_VERSION
from runtime.index.preview.recovery import CURRENT_SCHEMA_VERSION as PREVIEW_SQLITE_SCHEMA_VERSION
from runtime.search.provider_policy import load_provider_policy_registry


BUNDLE_SCHEMA_VERSION = "eureka.local_preview_bundle.v0"
PRODUCT_VERSION = "0.1.0-local-preview"
REQUIRED_BUNDLE_FILES = ("bundle_manifest.json", "checksums.json", "README.md", "launch.ps1", "launch.sh")
SOURCE_REF_PATHS = (
    "README.md",
    "scripts/eureka.py",
    "runtime/local/portable_instance.py",
    "runtime/local/portable_bundle.py",
    "runtime/search/live_service.py",
    "runtime/search/hunt_engine.py",
    "runtime/search/provider_policy.py",
    "runtime/connectors/web/http_fetcher.py",
    "runtime/index/preview/store.py",
    "control/policies/discovery_provider_registry.json",
    "control/inventory/product/capability_state.json",
)
FORBIDDEN_BUNDLE_NAMES = {".env", "secrets", ".aide.local", "instances", "raw-provider-responses", "provider-cache"}


def version_payload(*, repo_root: str | Path, instance_schema_version: int) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    provider_registry = load_provider_policy_registry()
    return {
        "schema_version": "eureka.local_preview_version.v0",
        "product_version": PRODUCT_VERSION,
        "commit": _git_commit(repo),
        "python_required": ">=3.10",
        "python_runtime": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "instance_schema_version": int(instance_schema_version),
        "preview_index_generation_schema": PREVIEW_INDEX_SCHEMA_VERSION,
        "preview_index_sqlite_schema": PREVIEW_SQLITE_SCHEMA_VERSION,
        "provider_registry_schema": provider_registry.schema_version,
        "provider_registry_version": provider_registry.policy_version,
        "capability_manifest_version": "eureka.product_capability_state.v0",
        "public_exposure": False,
        "public_live_fanout": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
    }


def build_portable_bundle(
    *,
    repo_root: str | Path,
    out_dir: str | Path,
    instance_schema_version: int,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    root = Path(out_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    version = version_payload(repo_root=repo, instance_schema_version=instance_schema_version)
    source_refs = _source_refs(repo)
    bundle_id = "local-preview-" + hashlib.sha256((version["commit"] + _now()).encode("utf-8")).hexdigest()[:16]
    manifest = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "created_at": _now(),
        "source_version": version,
        "source_refs": source_refs,
        "bootstrap_command": "python scripts/eureka.py --instance <instance> bootstrap --no-demo",
        "doctor_command": "python scripts/eureka.py --instance <instance> doctor",
        "test_command": "python scripts/eureka.py --instance <instance> test",
        "serve_command": "python scripts/eureka.py --instance <instance> serve --live",
        "backup_command": "python scripts/eureka.py --instance <instance> backup create",
        "restore_command": "python scripts/eureka.py --instance <instance> backup restore <backup> --target <target-instance>",
        "default_provider_registry": "control/policies/discovery_provider_registry.json",
        "default_local_policy": "loopback-only explicit local --live mode",
        "licenses_and_notices": ["repository license files are referenced from the source checkout"],
        "included_files": list(REQUIRED_BUNDLE_FILES),
        "excluded": [
            "API keys",
            "local instances",
            "private indexes",
            "raw observations",
            "provider result payloads",
            "AIDE local state",
            "public deployment state",
        ],
        "network_provider_calls": False,
        "public_exposure": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
    }
    _write_text(root / "README.md", _bundle_readme(manifest))
    _write_text(root / "launch.ps1", _launch_ps1())
    _write_text(root / "launch.sh", _launch_sh())
    _write_json(root / "bundle_manifest.json", manifest)
    checksums = _bundle_checksums(root, repo, source_refs)
    _write_json(root / "checksums.json", checksums)
    validation = validate_portable_bundle(root, repo_root=repo)
    return {
        "schema_version": "eureka.local_preview_bundle_create.v0",
        "status": "pass" if validation.get("status") == "pass" else "fail",
        "bundle_dir": str(root),
        "bundle_id": bundle_id,
        "manifest": str(root / "bundle_manifest.json"),
        "checksums": str(root / "checksums.json"),
        "validation": validation,
        "provider_result_payload_included": False,
        "credential_value_exposed": False,
        "private_instance_data_included": False,
        "public_exposure": False,
    }


def validate_portable_bundle(bundle_dir: str | Path, *, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(bundle_dir).resolve()
    errors: list[str] = []
    if not root.is_dir():
        errors.append(f"bundle directory not found: {root}")
        return _validation_payload(root, errors)
    for name in REQUIRED_BUNDLE_FILES:
        if not (root / name).is_file():
            errors.append(f"missing required bundle file: {name}")
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if any(part.casefold() in FORBIDDEN_BUNDLE_NAMES for part in relative_parts):
            errors.append(f"forbidden bundle path: {path}")
    manifest = _load_json_optional(root / "bundle_manifest.json")
    checksums = _load_json_optional(root / "checksums.json")
    if manifest.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        errors.append(f"manifest schema_version must be {BUNDLE_SCHEMA_VERSION}")
    if manifest.get("public_exposure") is not False:
        errors.append("manifest must keep public_exposure false")
    for key in ("reviewed_master_mutation", "public_index_mutation", "network_provider_calls"):
        if manifest.get(key) is not False:
            errors.append(f"manifest must keep {key} false")
    expected_files = checksums.get("bundle_files") if isinstance(checksums.get("bundle_files"), Mapping) else {}
    for relative, expected_hash in expected_files.items():
        path = root / str(relative)
        if not path.is_file():
            errors.append(f"checksum file missing: {relative}")
            continue
        actual = _sha256(path)
        if expected_hash != actual:
            errors.append(f"checksum mismatch: {relative}")
    if repo_root is not None:
        repo = Path(repo_root).resolve()
        source_refs = checksums.get("source_refs") if isinstance(checksums.get("source_refs"), Mapping) else {}
        for relative, expected_hash in source_refs.items():
            path = repo / str(relative)
            if not path.is_file():
                errors.append(f"source ref missing: {relative}")
                continue
            if _sha256(path) != expected_hash:
                errors.append(f"source ref checksum mismatch: {relative}")
    return _validation_payload(root, errors)


def _validation_payload(root: Path, errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "eureka.local_preview_bundle_validation.v0",
        "status": "pass" if not errors else "fail",
        "bundle_dir": str(root),
        "errors": errors,
        "provider_result_payload_included": False,
        "credential_value_exposed": False,
        "private_instance_data_included": False,
        "public_exposure": False,
    }


def _source_refs(repo: Path) -> list[dict[str, Any]]:
    refs = []
    for relative in SOURCE_REF_PATHS:
        path = repo / relative
        if path.is_file():
            refs.append({"path": relative, "sha256": _sha256(path), "bytes": path.stat().st_size})
    return refs


def _bundle_checksums(root: Path, repo: Path, source_refs: list[Mapping[str, Any]]) -> dict[str, Any]:
    bundle_files = {
        relative: _sha256(root / relative)
        for relative in REQUIRED_BUNDLE_FILES
        if relative != "checksums.json" and (root / relative).is_file()
    }
    return {
        "schema_version": "eureka.local_preview_bundle_checksums.v0",
        "bundle_files": bundle_files,
        "source_refs": {str(item["path"]): str(item["sha256"]) for item in source_refs},
        "repo_root_reference": str(repo),
        "credential_value_exposed": False,
        "provider_result_payload_included": False,
    }


def _bundle_readme(manifest: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Eureka Local Preview Bundle",
            "",
            "This bundle is a local-only source-checkout manifest for the Eureka preview.",
            "It does not include API keys, local instances, private indexes, raw observations, or provider result payloads.",
            "",
            "## Commands",
            "",
            f"- Bootstrap: `{manifest['bootstrap_command']}`",
            f"- Doctor: `{manifest['doctor_command']}`",
            f"- Test: `{manifest['test_command']}`",
            f"- Serve live UI: `{manifest['serve_command']}`",
            "",
            "Use `launch.ps1` or `launch.sh` from a source checkout by passing the checkout root and an explicit instance path.",
            "",
        ]
    )


def _launch_ps1() -> str:
    return "\n".join(
        [
            "param(",
            "  [string]$Repo = \".\",",
            "  [string]$Instance = \"..\\instances\\eureka-local-preview\",",
            "  [switch]$Live",
            ")",
            "$ErrorActionPreference = \"Stop\"",
            "$Script = Join-Path $Repo \"scripts/eureka.py\"",
            "python $Script --instance $Instance bootstrap --no-demo",
            "python $Script --instance $Instance doctor",
            "if ($Live) {",
            "  python $Script --instance $Instance serve --live",
            "} else {",
            "  python $Script --instance $Instance serve",
            "}",
            "",
        ]
    )


def _launch_sh() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env sh",
            "set -eu",
            "REPO=${1:-.}",
            "INSTANCE=${2:-../instances/eureka-local-preview}",
            "MODE=${3:-local}",
            "SCRIPT=\"$REPO/scripts/eureka.py\"",
            "python \"$SCRIPT\" --instance \"$INSTANCE\" bootstrap --no-demo",
            "python \"$SCRIPT\" --instance \"$INSTANCE\" doctor",
            "if [ \"$MODE\" = \"live\" ]; then",
            "  python \"$SCRIPT\" --instance \"$INSTANCE\" serve --live",
            "else",
            "  python \"$SCRIPT\" --instance \"$INSTANCE\" serve",
            "fi",
            "",
        ]
    )


def _git_commit(repo: Path) -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo), text=True, capture_output=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _load_json_optional(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(loaded) if isinstance(loaded, Mapping) else {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

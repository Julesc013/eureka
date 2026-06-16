"""External staging helpers for the local public-alpha bundle."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any
from urllib.parse import urljoin, urlparse

from runtime.local.staging_mvp import (
    MANIFEST_FILE,
    PUBLIC_INDEX_FILE,
    RUNTIME_CONFIG_FILE,
    bundle_status,
    validate_bundle,
)


TASK_ID = "EXTERNAL-STAGING-HOST-PROVISION-00-CONFIG"
CONFIG_SCHEMA_VERSION = 1
PLAN_SCHEMA_VERSION = "eureka.external_staging_plan.v0"
REPORT_SCHEMA_VERSION = "eureka.external_staging_report.v0"
DEPLOYMENT_MANIFEST_SCHEMA_VERSION = "eureka.external_staging_deployment_manifest.v0"

LOCAL_CONFIG_JSON = "external_staging_config.local.json"
LOCAL_CONFIG_EXAMPLE_JSON = "external_staging_config.local.example.json"
PLAN_JSON = "external_staging_plan.json"
REPORT_JSON = "external_staging_report.json"
REPORT_MD = "EXTERNAL_STAGING_REPORT.md"
DEPLOYMENT_MANIFEST_JSON = "deployment_manifest.json"
REMOTE_RUN_COMMAND_TXT = "remote_run_command.txt"
REMOTE_SMOKE_COMMANDS_TXT = "remote_smoke_commands.txt"
ROLLBACK_INSTRUCTIONS_TXT = "rollback_instructions.txt"
BUNDLE_PACKAGE_DIR = "staging_bundle"

DEFAULT_OUT = ".eureka/external-staging/public-alpha/latest"
DEFAULT_BIND_HOST = "127.0.0.1"
DEFAULT_SERVICE_PORT = 8765
DEFAULT_QUERY = "manual for Sound Blaster CT1740"
CONFIRM_APPLY_ENV = "EUREKA_STAGING_CONFIRM_APPLY"

SECRET_MARKERS = (
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY",
    "BEGIN PRIVATE KEY",
    "PRIVATE KEY",
    "api_key",
    "apikey",
    "sk-",
    "token=",
    "authorization:",
    "bearer ",
)
PRIVATE_FILE_MARKERS = (
    "local_review_ledger",
    "local_reviewed_records",
    "workbench",
    "live_metadata",
)
PUBLIC_ROUTE_PATHS = (
    "/",
    "/health",
    "/status",
    "/api/status",
    "/about",
    "/method",
    "/search?q=manual%20for%20Sound%20Blaster%20CT1740",
    "/api/search?q=manual%20for%20Sound%20Blaster%20CT1740",
)
BLOCKED_ROUTE_PROBES = (
    ("GET", "/workbench"),
    ("GET", "/workbench/api/status"),
    ("POST", "/workbench/api/review/accept"),
)
SAFETY_FALSE_FIELDS = (
    "live_metadata_enabled",
    "public_live_fanout",
    "workbench_exposed",
    "mutation_enabled",
    "downloads_enabled",
    "binary_verified_count",
    "download_safe_count",
    "execution_safe_count",
    "rights_cleared_count",
)
CONFIG_SAFETY_FALSE_FIELDS = (
    "live_metadata_enabled",
    "public_live_fanout",
    "workbench_enabled",
    "workbench_exposed",
    "mutation_enabled",
    "downloads_enabled",
)

ENV_FIELDS = (
    "HOST",
    "USER",
    "SSH_KEY",
    "SSH_PORT",
    "REMOTE_DIR",
    "BASE_URL",
    "SERVICE_PORT",
    "BIND_HOST",
    "EXPOSURE_APPROVED",
)


def init_config_template(out: str | Path) -> dict[str, Any]:
    payload = {
        "config_schema_version": CONFIG_SCHEMA_VERSION,
        "host": "",
        "user": "",
        "ssh_port": 22,
        "ssh_key_path": "",
        "remote_dir": "",
        "base_url": "",
        "service_port": DEFAULT_SERVICE_PORT,
        "bind_host": DEFAULT_BIND_HOST,
        "exposure_approved": False,
        "deployment_mode": "ssh",
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "workbench_enabled": False,
        "public_live_fanout": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
        "notes": "Local ignored example. Fill this in as external_staging_config.local.json; do not commit credentials.",
    }
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    _write_json(out, payload)
    return payload


def config_status(
    config: str | Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    source = env if env is not None else os.environ
    if config:
        config_path = Path(config)
        if not config_path.is_file():
            return _config_result(
                status="missing_config",
                source="local_config",
                errors=[],
                warnings=[f"config file is missing: {config_path}"],
            )
        try:
            payload = _read_json(config_path)
        except (OSError, json.JSONDecodeError) as exc:
            return _config_result(status="fail", source="local_config", errors=[f"config could not be read: {type(exc).__name__}"])
        errors, warnings = _validate_config_payload(payload, require_apply_fields=True)
        return _config_result(status="pass" if not errors else "fail", source="local_config", payload=payload, errors=errors, warnings=warnings)
    env_payload = _config_payload_from_env(source)
    if not _has_env_config(source):
        return _config_result(status="missing_config", source="none", errors=[], warnings=["no local config file or EUREKA_STAGING_* environment configuration found"])
    errors, warnings = _validate_config_payload(env_payload, require_apply_fields=True)
    return _config_result(status="pass" if not errors else "fail", source="env", payload=env_payload, errors=errors, warnings=warnings)


def render_config_status(payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"status: {payload.get('status')}",
            f"config_source: {payload.get('config_source')}",
            f"host_configured: {str(payload.get('host_configured')).lower()}",
            f"user_configured: {str(payload.get('user_configured')).lower()}",
            f"remote_dir_configured: {str(payload.get('remote_dir_configured')).lower()}",
            f"base_url_configured: {str(payload.get('base_url_configured')).lower()}",
            f"ssh_key_configured: {str(payload.get('ssh_key_configured')).lower()}",
            f"bind_host: {payload.get('bind_host') or DEFAULT_BIND_HOST}",
            f"service_port: {payload.get('service_port') or DEFAULT_SERVICE_PORT}",
            f"exposure_approved: {str(payload.get('exposure_approved')).lower()}",
            f"public_alpha_mode: {str(payload.get('public_alpha_mode')).lower()}",
            f"read_only: {str(payload.get('read_only')).lower()}",
            f"workbench_enabled: {str(payload.get('workbench_enabled')).lower()}",
            f"live_metadata_enabled: {str(payload.get('live_metadata_enabled')).lower()}",
            f"mutation_enabled: {str(payload.get('mutation_enabled')).lower()}",
            f"downloads_enabled: {str(payload.get('downloads_enabled')).lower()}",
            f"errors: {json.dumps(payload.get('errors') or [])}",
            f"warnings: {json.dumps(payload.get('warnings') or [])}",
        ]
    ) + "\n"


def read_external_config(
    env: Mapping[str, str] | None = None,
    *,
    overrides: Mapping[str, Any] | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    source = env if env is not None else os.environ
    file_config: dict[str, Any] = {}
    config_source = "none"
    config_state = "missing_config"
    config_errors: list[str] = []
    config_warnings: list[str] = []
    raw_config_path = str(config_path or "")

    if config_path:
        path = Path(config_path)
        if path.is_file():
            file_config = _read_json(path)
            config_errors, config_warnings = _validate_config_payload(file_config, require_apply_fields=True)
            config_source = "local_config"
            config_state = "pass" if not config_errors else "fail"
        else:
            config_source = "local_config"
            config_state = "missing_config"
            config_warnings.append(f"config file is missing: {path}")
    elif _has_env_config(source):
        file_config = _config_payload_from_env(source)
        config_errors, config_warnings = _validate_config_payload(file_config, require_apply_fields=True)
        config_source = "env"
        config_state = "pass" if not config_errors else "fail"

    opts = dict(overrides or {})

    def get(name: str, default: Any = "") -> str:
        value = opts.get(name)
        if value is None or str(value) == "":
            if name == "ssh_key":
                value = file_config.get("ssh_key_path", file_config.get("ssh_key", ""))
            else:
                value = file_config.get(name, "")
        if value is None or str(value) == "":
            env_name = "SSH_KEY" if name == "ssh_key" else name.upper()
            value = source.get(f"EUREKA_STAGING_{env_name}", default)
        return str(value or "").strip()

    def get_bool(name: str, default: bool = False) -> bool:
        value = opts.get(name)
        if value is None or str(value) == "":
            value = file_config.get(name)
        if value is None or str(value) == "":
            value = source.get(f"EUREKA_STAGING_{name.upper()}", str(default).lower())
        return _truthy(value)

    bind_host = get("bind_host", DEFAULT_BIND_HOST) or DEFAULT_BIND_HOST
    service_port = _int(get("service_port", str(DEFAULT_SERVICE_PORT)), DEFAULT_SERVICE_PORT)
    exposure = get_bool("exposure_approved", False)
    deployment_mode = get("deployment_mode", str(file_config.get("deployment_mode") or ""))
    if not deployment_mode:
        deployment_mode = "ssh" if get("host") or get("user") or get("remote_dir") else "manual"
    host = get("host")
    user = get("user")
    ssh_key_path = get("ssh_key")
    remote_dir = get("remote_dir")
    base_url = get("base_url")
    return {
        "config_source": config_source,
        "config_status": config_state,
        "config_path": raw_config_path,
        "config_errors": config_errors,
        "config_warnings": config_warnings,
        "deployment_mode": deployment_mode,
        "host": host,
        "user": user,
        "ssh_key_path": ssh_key_path,
        "ssh_key_configured": bool(ssh_key_path),
        "ssh_key_readable": bool(Path(ssh_key_path).is_file()) if ssh_key_path else False,
        "ssh_port": _int(get("ssh_port", "22"), 22),
        "remote_dir": remote_dir,
        "base_url": base_url,
        "service_port": service_port,
        "bind_host": bind_host,
        "exposure_approved": exposure,
        "host_configured": bool(host),
        "user_configured": bool(user),
        "remote_dir_configured": bool(remote_dir),
        "base_url_configured": bool(base_url),
        "public_alpha_mode": _config_bool(file_config, "public_alpha_mode", True),
        "read_only": _config_bool(file_config, "read_only", True),
        "live_metadata_enabled": _config_bool(file_config, "live_metadata_enabled", False),
        "workbench_enabled": _config_bool(file_config, "workbench_enabled", False),
        "workbench_exposed": _config_bool(file_config, "workbench_exposed", False),
        "public_live_fanout": _config_bool(file_config, "public_live_fanout", False),
        "mutation_enabled": _config_bool(file_config, "mutation_enabled", False),
        "downloads_enabled": _config_bool(file_config, "downloads_enabled", False),
        "secret_fields_redacted": True,
    }


def create_plan(
    *,
    bundle: str | Path,
    out_dir: str | Path,
    config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bundle_path = Path(bundle)
    errors = validate_bundle(bundle_path)
    if errors:
        raise ValueError("staging bundle is invalid: " + "; ".join(errors))
    status = bundle_status(bundle_path)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    cfg = dict(config or read_external_config())
    if cfg.get("config_status") == "fail":
        raise ValueError("external staging config is invalid: " + "; ".join(str(item) for item in cfg.get("config_errors") or []))
    deployment_mode = str(cfg.get("deployment_mode") or "")
    if deployment_mode not in {"ssh", "manual"}:
        deployment_mode = "ssh" if cfg.get("host_configured") and cfg.get("user_configured") and cfg.get("remote_dir_configured") else "manual"
    if cfg.get("config_status") == "missing_config" and not any(cfg.get(key) for key in ("host_configured", "user_configured", "remote_dir_configured", "base_url_configured")):
        deployment_mode = "manual"
    plan = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "plan_schema_version": PLAN_SCHEMA_VERSION,
        "config_source": str(cfg.get("config_source") or "none"),
        "config_status": str(cfg.get("config_status") or "missing_config"),
        "config_path": _safe_local_config_path(str(cfg.get("config_path") or "")),
        "config_warnings": [str(item) for item in cfg.get("config_warnings") or []],
        "staging_bundle_path": str(bundle_path),
        "staging_bundle_id": str(status.get("bundle_id") or ""),
        "bundle_manifest_digest": _file_sha256(bundle_path / MANIFEST_FILE),
        "public_index_digest": str(status.get("public_index_digest") or ""),
        "corpus_gate_status": str(status.get("corpus_gate_status") or ""),
        "reviewed_artifact_gate_count": int(status.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(status.get("artifact_verified_count") or 0),
        "public_artifact_identity_record_count": int(status.get("public_artifact_identity_record_count") or 0),
        "read_only": True,
        "public_alpha_mode": True,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "workbench_exposed": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
        "binary_verified_count": int(status.get("binary_verified_count") or 0),
        "download_safe_count": int(status.get("download_safe_count") or 0),
        "execution_safe_count": int(status.get("execution_safe_count") or 0),
        "rights_cleared_count": int(status.get("rights_cleared_count") or 0),
        "deployment_mode": deployment_mode,
        "host_configured": bool(cfg.get("host_configured")),
        "user_configured": bool(cfg.get("user_configured")),
        "base_url_configured": bool(cfg.get("base_url_configured")),
        "remote_dir_configured": bool(cfg.get("remote_dir_configured")),
        "ssh_key_configured": bool(cfg.get("ssh_key_configured")),
        "ssh_key_readable": bool(cfg.get("ssh_key_readable")),
        "ssh_port": int(cfg.get("ssh_port") or 22),
        "bind_host": str(cfg.get("bind_host") or DEFAULT_BIND_HOST),
        "service_port": int(cfg.get("service_port") or DEFAULT_SERVICE_PORT),
        "exposure_approved": bool(cfg.get("exposure_approved") is True),
        "host_redacted": _presence_redaction(cfg.get("host")),
        "user_redacted": _presence_redaction(cfg.get("user")),
        "remote_dir_redacted": _presence_redaction(cfg.get("remote_dir")),
        "base_url": _safe_base_url(str(cfg.get("base_url") or "")),
        "secret_fields_redacted": True,
        "generated_at": "not_recorded_deterministic_external_staging_plan",
    }
    _write_json(out_path / PLAN_JSON, plan)
    return plan


def validate_plan(plan: str | Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = _read_json(plan)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"plan could not be read: {type(exc).__name__}"]
    required = (
        "task_id",
        "plan_schema_version",
        "config_source",
        "config_status",
        "staging_bundle_id",
        "bundle_manifest_digest",
        "public_index_digest",
        "corpus_gate_status",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
        "public_artifact_identity_record_count",
        "read_only",
        "public_alpha_mode",
        "live_metadata_enabled",
        "public_live_fanout",
        "workbench_exposed",
        "mutation_enabled",
        "downloads_enabled",
        "deployment_mode",
        "host_configured",
        "user_configured",
        "base_url_configured",
        "remote_dir_configured",
        "bind_host",
        "service_port",
        "exposure_approved",
        "secret_fields_redacted",
    )
    for key in required:
        if key not in payload:
            errors.append(f"missing required field: {key}")
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if payload.get("config_source") not in {"none", "env", "local_config"}:
        errors.append("config_source must be none, env, or local_config")
    if payload.get("config_status") not in {"pass", "missing_config"}:
        errors.append("config_status must be pass or missing_config")
    if payload.get("deployment_mode") not in {"manual", "ssh"}:
        errors.append("deployment_mode must be manual or ssh")
    for key in ("read_only", "public_alpha_mode", "secret_fields_redacted"):
        if payload.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in SAFETY_FALSE_FIELDS:
        expected = 0 if key.endswith("_count") else False
        if payload.get(key) != expected:
            errors.append(f"{key} must be {expected!r}")
    if payload.get("corpus_gate_status") != "pass":
        errors.append("corpus_gate_status must be pass")
    if int(payload.get("reviewed_artifact_gate_count") or 0) < 25:
        errors.append("reviewed_artifact_gate_count must be at least 25")
    if int(payload.get("artifact_verified_count") or 0) < 25:
        errors.append("artifact_verified_count must be at least 25")
    if str(payload.get("bind_host") or "") not in {"127.0.0.1", "localhost", "::1"} and payload.get("exposure_approved") is not True:
        errors.append("non-loopback bind_host requires exposure_approved true")
    if payload.get("base_url") and not _base_url_allowed(str(payload.get("base_url") or ""), exposure_approved=bool(payload.get("exposure_approved") is True)):
        errors.append("non-local base_url requires exposure_approved true")
    if payload.get("deployment_mode") == "ssh" and payload.get("config_status") == "pass":
        for key in ("host_configured", "user_configured", "remote_dir_configured"):
            if payload.get(key) is not True:
                errors.append(f"{key} must be true for ssh deployment mode")
    errors.extend(_payload_secret_errors("external_staging_plan", payload))
    return _dedupe(errors)


def package_for_transfer(*, bundle: str | Path, out_dir: str | Path, plan: Mapping[str, Any] | None = None) -> dict[str, Any]:
    bundle_path = Path(bundle)
    errors = validate_bundle(bundle_path)
    if errors:
        raise ValueError("staging bundle is invalid: " + "; ".join(errors))
    status = bundle_status(bundle_path)
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    package_bundle_path = output / BUNDLE_PACKAGE_DIR
    if package_bundle_path.exists():
        shutil.rmtree(package_bundle_path)
    package_bundle_path.mkdir(parents=True)
    for item in sorted(bundle_path.iterdir()):
        if item.is_file():
            shutil.copy2(item, package_bundle_path / item.name)

    plan_payload = dict(plan or {})
    remote_dir = "<REMOTE_DIR>"
    if plan_payload.get("remote_dir_configured"):
        remote_dir = "<configured-remote-dir>"
    run_command = (
        "python scripts/run_eureka_local.py --host "
        f"{plan_payload.get('bind_host') or DEFAULT_BIND_HOST} --port {int(plan_payload.get('service_port') or DEFAULT_SERVICE_PORT)} "
        f"--public-alpha --staging-bundle {remote_dir}/staging_bundle"
    )
    base_url = str(plan_payload.get("base_url") or "").rstrip("/") or "<BASE_URL>"
    smoke_lines = [f"GET {base_url}{path}" for path in PUBLIC_ROUTE_PATHS]
    smoke_lines.extend(f"{method} {base_url}{path}" for method, path in BLOCKED_ROUTE_PROBES)
    manifest = {
        "schema_version": DEPLOYMENT_MANIFEST_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "staging_bundle_id": str(status.get("bundle_id") or ""),
        "bundle_manifest_digest": _file_sha256(bundle_path / MANIFEST_FILE),
        "public_index_digest": str(status.get("public_index_digest") or ""),
        "corpus_gate_status": str(status.get("corpus_gate_status") or ""),
        "reviewed_artifact_gate_count": int(status.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(status.get("artifact_verified_count") or 0),
        "read_only": True,
        "public_alpha_mode": True,
        "workbench_exposed": False,
        "live_metadata_enabled": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
        "files": sorted(path.name for path in package_bundle_path.iterdir() if path.is_file()),
        "secret_fields_redacted": True,
        "local_private_artifacts_included": False,
    }
    _write_json(output / DEPLOYMENT_MANIFEST_JSON, manifest)
    (output / REMOTE_RUN_COMMAND_TXT).write_text(run_command + "\n", encoding="utf-8")
    (output / REMOTE_SMOKE_COMMANDS_TXT).write_text("\n".join(smoke_lines) + "\n", encoding="utf-8")
    (output / ROLLBACK_INSTRUCTIONS_TXT).write_text(
        "Stop the external staging process, restore the previous staging_bundle directory, and restart the same read-only run command.\n",
        encoding="utf-8",
    )
    leakage_errors = package_leakage_errors(output)
    return {
        "schema_version": "eureka.external_staging_package_status.v0",
        "status": "pass" if not leakage_errors else "fail",
        "package": str(output),
        "staging_bundle_id": manifest["staging_bundle_id"],
        "files": [
            DEPLOYMENT_MANIFEST_JSON,
            REMOTE_RUN_COMMAND_TXT,
            REMOTE_SMOKE_COMMANDS_TXT,
            ROLLBACK_INSTRUCTIONS_TXT,
            BUNDLE_PACKAGE_DIR,
        ],
        "leakage_errors": leakage_errors,
    }


def package_leakage_errors(package_dir: str | Path) -> list[str]:
    errors: list[str] = []
    package_path = Path(package_dir)
    for path in package_path.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(package_path).as_posix()
        lowered_rel = rel.casefold()
        for marker in PRIVATE_FILE_MARKERS:
            if marker.casefold() in lowered_rel:
                errors.append(f"package contains private file marker {marker}: {rel}")
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        errors.extend(_payload_secret_errors(rel, body))
        if ".eureka" in body:
            errors.append(f"{rel} contains local .eureka path")
    return _dedupe(errors)


def deploy_from_plan(
    *,
    plan: str | Path,
    apply: bool = False,
    confirm_apply: bool = False,
    env: Mapping[str, str] | None = None,
    transfer_runner: Callable[[Mapping[str, Any], Mapping[str, Any], Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    plan_path = Path(plan)
    errors = validate_plan(plan_path)
    if errors:
        report = _base_report(_read_json_if_possible(plan_path), deployment_status="failed", smoke_status="not_run")
        report["blockers"].extend(errors)
        report["status"] = "FAIL"
        return _write_report_near_plan(plan_path, report)
    payload = _read_json(plan_path)
    if apply:
        confirmation = bool(confirm_apply or _truthy((env or os.environ).get(CONFIRM_APPLY_ENV, "")))
        if not confirmation:
            report = _base_report(payload, deployment_status="confirmation_required", smoke_status="not_run")
            report["apply_confirmation"] = False
            report["blockers"].append("explicit deploy --apply confirmation is required")
            report["warnings"].append("deploy --apply refused before contacting any host")
            return _write_report_near_plan(plan_path, report)
        apply_config = _apply_config_for_plan(payload, env=env)
        config_errors = apply_config.get("config_errors") or []
        if config_errors:
            report = _base_report(payload, deployment_status="missing_config", smoke_status="not_run")
            report["apply_confirmation"] = True
            report["blockers"].extend(str(item) for item in config_errors)
            report["warnings"].append("deploy --apply refused because external staging configuration is invalid")
            return _write_report_near_plan(plan_path, report)
        missing = _missing_apply_config(payload, apply_config)
        if missing:
            report = _base_report(payload, deployment_status="missing_config", smoke_status="not_run")
            report["apply_confirmation"] = True
            report["blockers"].extend(missing)
            report["warnings"].append("deploy --apply refused because external staging configuration is incomplete")
            return _write_report_near_plan(plan_path, report)
        package_dir = plan_path.parent / "package"
        if not package_dir.is_dir():
            report = _base_report(payload, deployment_status="failed", smoke_status="not_run")
            report["apply_confirmation"] = True
            report["blockers"].append(f"deployment package is missing: {package_dir}")
            return _write_report_near_plan(plan_path, report)
        runner = transfer_runner or _ssh_transfer_package
        transfer = dict(runner(payload, apply_config, package_dir))
        if transfer.get("status") == "pass":
            deployment_status = str(transfer.get("deployment_status") or "transfer_complete_manual_start_required")
            report = _base_report(payload, deployment_status=deployment_status, smoke_status="not_run")
            report["apply_confirmation"] = True
            report["remote_start_status"] = str(transfer.get("remote_start_status") or "manual_required")
            report["warnings"].extend(str(item) for item in transfer.get("warnings") or [])
        else:
            report = _base_report(payload, deployment_status="failed", smoke_status="not_run")
            report["apply_confirmation"] = True
            report["remote_start_status"] = str(transfer.get("remote_start_status") or "not_started")
            report["blockers"].extend(str(item) for item in transfer.get("errors") or ["external staging transfer failed"])
            report["warnings"].extend(str(item) for item in transfer.get("warnings") or [])
        return _write_report_near_plan(plan_path, report)
    report = _base_report(payload, deployment_status="dry_run_pass", smoke_status="not_run")
    report["warnings"].append("dry run only; no external host was contacted")
    if not payload.get("host_configured"):
        report["blockers"].append("external staging host is not configured")
    return _write_report_near_plan(plan_path, report)


def smoke_from_plan(
    *,
    plan: str | Path,
    probe: Callable[[str, str], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    plan_path = Path(plan)
    errors = validate_plan(plan_path)
    if errors:
        report = _base_report(_read_json_if_possible(plan_path), deployment_status="failed", smoke_status="fail")
        report["blockers"].extend(errors)
        report["status"] = "FAIL"
        return _write_report_near_plan(plan_path, report)
    payload = _read_json(plan_path)
    previous = _read_json_if_possible(_report_path_for_plan(plan_path))
    deployment_status = str(previous.get("deployment_status") or "not_configured")
    base_url = str(payload.get("base_url") or "").rstrip("/")
    if not base_url:
        report = _base_report(payload, deployment_status=deployment_status, smoke_status="blocked")
        _carry_deployment_fields(report, previous)
        report["warnings"].append("external staging smoke could not run without EUREKA_STAGING_BASE_URL or --base-url")
        return _write_report_near_plan(plan_path, report)

    route_results = []
    probe_func = probe or _http_probe
    for path in PUBLIC_ROUTE_PATHS:
        route_results.append(dict(probe_func("GET", urljoin(base_url + "/", path.lstrip("/")))))
    blocked_results = []
    for method, path in BLOCKED_ROUTE_PROBES:
        blocked_results.append(dict(probe_func(method, urljoin(base_url + "/", path.lstrip("/")))))
    status_payload = _status_payload(route_results)
    failures = _smoke_failures(route_results, blocked_results, status_payload)
    report = _base_report(payload, deployment_status=deployment_status, smoke_status="pass" if not failures else "fail")
    _carry_deployment_fields(report, previous)
    report["route_probe_results"] = route_results
    report["blocked_route_probe_results"] = blocked_results
    report["blockers"].extend(failures)
    if failures:
        report["status"] = "FAIL"
    return _write_report_near_plan(plan_path, report)


def validate_report(report: str | Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = _read_json(report)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"report could not be read: {type(exc).__name__}"]
    required = (
        "task_id",
        "status",
        "deployment_status",
        "smoke_status",
        "config_source",
        "config_status",
        "staging_bundle_id",
        "bundle_manifest_digest",
        "corpus_gate_status",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
        "public_artifact_identity_record_count",
        "host_configured",
        "user_configured",
        "base_url_configured",
        "bind_host",
        "service_port",
        "exposure_approved",
        "remote_dir_configured",
        "apply_confirmation",
        "remote_start_status",
        "route_probe_results",
        "blocked_route_probe_results",
        "safety_checks",
        "mutation_checks",
        "secret_redaction_checks",
        "warnings",
        "blockers",
        "next_recommended_task",
    )
    for key in required:
        if key not in payload:
            errors.append(f"missing required field: {key}")
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if payload.get("status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if payload.get("deployment_status") not in {"missing_config", "not_configured", "config_validated", "dry_run_pass", "confirmation_required", "deployed", "transfer_complete_manual_start_required", "failed"}:
        errors.append("deployment_status must be a known external staging deployment status")
    if payload.get("smoke_status") not in {"not_run", "blocked", "pass", "fail"}:
        errors.append("smoke_status must be not_run, blocked, pass, or fail")
    if payload.get("config_source") not in {"none", "env", "local_config"}:
        errors.append("config_source must be none, env, or local_config")
    if payload.get("config_status") not in {"pass", "missing_config"}:
        errors.append("config_status must be pass or missing_config")
    if payload.get("deployment_status") in {"deployed", "transfer_complete_manual_start_required"} and payload.get("host_configured") is not True:
        errors.append("report claims deployed without host_configured true")
    if payload.get("deployment_status") in {"deployed", "transfer_complete_manual_start_required"} and payload.get("apply_confirmation") is not True:
        errors.append("report claims deployment without apply confirmation")
    if payload.get("smoke_status") == "pass" and not payload.get("base_url_configured"):
        errors.append("report claims smoke pass without base_url_configured true")
    if payload.get("smoke_status") == "pass" and not payload.get("route_probe_results"):
        errors.append("report claims smoke pass without route probes")
    safety = payload.get("safety_checks") if isinstance(payload.get("safety_checks"), Mapping) else {}
    for key in ("workbench_exposed", "live_metadata_enabled", "mutation_enabled", "downloads_enabled"):
        if safety.get(key) is not False:
            errors.append(f"safety_checks.{key} must be false")
    for key in ("binary_verified_count", "download_safe_count", "execution_safe_count", "rights_cleared_count"):
        if int(payload.get(key) or 0) != 0:
            errors.append(f"{key} must remain 0")
    if payload.get("corpus_gate_status") != "pass":
        errors.append("corpus_gate_status must be pass")
    if int(payload.get("reviewed_artifact_gate_count") or 0) < 25:
        errors.append("reviewed_artifact_gate_count must be at least 25")
    errors.extend(_payload_secret_errors("external_staging_report", payload))
    return _dedupe(errors)


def render_status(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"status: {report.get('status')}",
            f"deployment_status: {report.get('deployment_status')}",
            f"smoke_status: {report.get('smoke_status')}",
            f"config_source: {report.get('config_source')}",
            f"config_status: {report.get('config_status')}",
            f"staging_bundle_id: {report.get('staging_bundle_id')}",
            f"host_configured: {str(report.get('host_configured')).lower()}",
            f"user_configured: {str(report.get('user_configured')).lower()}",
            f"base_url_configured: {str(report.get('base_url_configured')).lower()}",
            f"remote_dir_configured: {str(report.get('remote_dir_configured')).lower()}",
            f"ssh_key_configured: {str(report.get('ssh_key_configured')).lower()}",
            f"exposure_approved: {str(report.get('exposure_approved')).lower()}",
            f"bind_host: {report.get('bind_host')}",
            f"service_port: {report.get('service_port')}",
            f"apply_confirmation: {str(report.get('apply_confirmation')).lower()}",
            f"remote_start_status: {report.get('remote_start_status')}",
            f"corpus_gate_status: {report.get('corpus_gate_status')}",
            f"artifact_verified_count: {report.get('artifact_verified_count')}",
            f"read_only: {str((report.get('safety_checks') or {}).get('read_only')).lower()}",
            f"workbench_exposed: {str((report.get('safety_checks') or {}).get('workbench_exposed')).lower()}",
            f"live_metadata_enabled: {str((report.get('safety_checks') or {}).get('live_metadata_enabled')).lower()}",
            f"mutation_enabled: {str((report.get('safety_checks') or {}).get('mutation_enabled')).lower()}",
            f"blockers: {json.dumps(report.get('blockers') or [])}",
            f"next_recommended_task: {report.get('next_recommended_task')}",
        ]
    ) + "\n"


def render_report_markdown(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# External Staging Report",
            "",
            f"- Status: {report.get('status')}",
            f"- Deployment status: {report.get('deployment_status')}",
            f"- Smoke status: {report.get('smoke_status')}",
            f"- Config source: {report.get('config_source')}",
            f"- Config status: {report.get('config_status')}",
            f"- Staging bundle: {report.get('staging_bundle_id')}",
            f"- Host configured: {report.get('host_configured')}",
            f"- User configured: {report.get('user_configured')}",
            f"- Remote dir configured: {report.get('remote_dir_configured')}",
            f"- Base URL configured: {report.get('base_url_configured')}",
            f"- Exposure approved: {report.get('exposure_approved')}",
            f"- Apply confirmation: {report.get('apply_confirmation')}",
            f"- Remote start status: {report.get('remote_start_status')}",
            f"- Corpus gate status: {report.get('corpus_gate_status')}",
            f"- Artifact verified count: {report.get('artifact_verified_count')}",
            "",
            "## Blockers",
            "",
            *(f"- {item}" for item in report.get("blockers") or ["none"]),
            "",
            "## Safety",
            "",
            f"- Read only: {(report.get('safety_checks') or {}).get('read_only')}",
            f"- Workbench exposed: {(report.get('safety_checks') or {}).get('workbench_exposed')}",
            f"- Live metadata enabled: {(report.get('safety_checks') or {}).get('live_metadata_enabled')}",
            f"- Mutation enabled: {(report.get('safety_checks') or {}).get('mutation_enabled')}",
            "",
            "External staging is operational evidence only. It is not production hosting, release approval, or public launch.",
            "",
        ]
    )


def _base_report(plan: Mapping[str, Any], *, deployment_status: str, smoke_status: str) -> dict[str, Any]:
    blockers: list[str] = []
    if deployment_status in {"missing_config", "not_configured", "dry_run_pass"} and not plan.get("host_configured"):
        blockers.append("external staging host is not configured")
    if deployment_status == "confirmation_required":
        blockers.append("explicit apply confirmation is required")
    if smoke_status == "blocked" and not plan.get("base_url_configured"):
        blockers.append("staging base URL is not configured")
    safety = {
        "read_only": bool(plan.get("read_only") is True),
        "public_alpha_mode": bool(plan.get("public_alpha_mode") is True),
        "live_metadata_enabled": bool(plan.get("live_metadata_enabled") is True),
        "public_live_fanout": bool(plan.get("public_live_fanout") is True),
        "workbench_exposed": bool(plan.get("workbench_exposed") is True),
        "mutation_enabled": bool(plan.get("mutation_enabled") is True),
        "downloads_enabled": bool(plan.get("downloads_enabled") is True),
        "binary_verified_count": int(plan.get("binary_verified_count") or 0),
        "download_safe_count": int(plan.get("download_safe_count") or 0),
        "execution_safe_count": int(plan.get("execution_safe_count") or 0),
        "rights_cleared_count": int(plan.get("rights_cleared_count") or 0),
    }
    status = "PASS"
    if (
        deployment_status in {"missing_config", "not_configured", "dry_run_pass", "confirmation_required"}
        or smoke_status in {"not_run", "blocked"}
        or (deployment_status == "transfer_complete_manual_start_required" and smoke_status != "pass")
        or blockers
    ):
        status = "PASS_WITH_WARNINGS"
    if deployment_status == "failed" or smoke_status == "fail":
        status = "FAIL"
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": status,
        "deployment_status": deployment_status,
        "smoke_status": smoke_status,
        "config_source": str(plan.get("config_source") or "none"),
        "config_status": str(plan.get("config_status") or "missing_config"),
        "staging_bundle_id": str(plan.get("staging_bundle_id") or ""),
        "bundle_manifest_digest": str(plan.get("bundle_manifest_digest") or ""),
        "corpus_gate_status": str(plan.get("corpus_gate_status") or ""),
        "reviewed_artifact_gate_count": int(plan.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(plan.get("artifact_verified_count") or 0),
        "public_artifact_identity_record_count": int(plan.get("public_artifact_identity_record_count") or 0),
        "binary_verified_count": int(plan.get("binary_verified_count") or 0),
        "download_safe_count": int(plan.get("download_safe_count") or 0),
        "execution_safe_count": int(plan.get("execution_safe_count") or 0),
        "rights_cleared_count": int(plan.get("rights_cleared_count") or 0),
        "host_configured": bool(plan.get("host_configured") is True),
        "user_configured": bool(plan.get("user_configured") is True),
        "base_url_configured": bool(plan.get("base_url_configured") is True),
        "exposure_approved": bool(plan.get("exposure_approved") is True),
        "remote_dir_configured": bool(plan.get("remote_dir_configured") is True),
        "ssh_key_configured": bool(plan.get("ssh_key_configured") is True),
        "bind_host": str(plan.get("bind_host") or DEFAULT_BIND_HOST),
        "service_port": int(plan.get("service_port") or DEFAULT_SERVICE_PORT),
        "apply_confirmation": False,
        "remote_start_status": "not_started",
        "route_probe_results": [],
        "blocked_route_probe_results": [],
        "safety_checks": safety,
        "mutation_checks": {
            "public_routes_mutated_bundle": False,
            "blocked_workbench_mutated_anything": False,
            "external_staging_mutated_repo": False,
        },
        "secret_redaction_checks": {
            "secret_fields_redacted": True,
            "tokens_or_private_keys_present": False,
        },
        "warnings": [],
        "blockers": blockers,
        "next_recommended_task": "PUBLIC-ALPHA-RELEASE-CHECKS-00" if not plan.get("host_configured") else "EXTERNAL-STAGING-HOST-PROVISION-00-APPLY",
        "generated_at": "not_recorded_deterministic_external_staging_report",
    }


def _write_report_near_plan(plan_path: Path, report: Mapping[str, Any]) -> dict[str, Any]:
    out_dir = plan_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(report)
    payload["blockers"] = _dedupe([str(item) for item in payload.get("blockers") or []])
    payload["warnings"] = _dedupe([str(item) for item in payload.get("warnings") or []])
    _write_json(out_dir / REPORT_JSON, payload)
    (out_dir / REPORT_MD).write_text(render_report_markdown(payload), encoding="utf-8")
    return payload


def _carry_deployment_fields(report: dict[str, Any], previous: Mapping[str, Any]) -> None:
    if "apply_confirmation" in previous:
        report["apply_confirmation"] = bool(previous.get("apply_confirmation") is True)
    if previous.get("remote_start_status"):
        report["remote_start_status"] = str(previous.get("remote_start_status"))


def _report_path_for_plan(plan_path: Path) -> Path:
    return plan_path.parent / REPORT_JSON


def _missing_apply_config(plan: Mapping[str, Any], config: Mapping[str, Any]) -> list[str]:
    missing = []
    if config.get("deployment_mode") == "ssh" and config.get("host_configured") is not True:
        missing.append("host is not configured")
    if config.get("deployment_mode") == "ssh" and config.get("user_configured") is not True:
        missing.append("user is not configured")
    if config.get("deployment_mode") == "ssh" and config.get("remote_dir_configured") is not True:
        missing.append("remote dir is not configured")
    if not _base_url_allowed(str(config.get("base_url") or ""), exposure_approved=bool(config.get("exposure_approved") is True)):
        missing.append("non-local base URL requires exposure_approved true")
    bind_host = str(config.get("bind_host") or DEFAULT_BIND_HOST)
    if bind_host not in {"127.0.0.1", "localhost", "::1"} and config.get("exposure_approved") is not True:
        missing.append("non-loopback bind_host requires exposure_approved true")
    if plan.get("config_status") == "missing_config" and config.get("config_source") == "none":
        missing.append("authorized external staging config is missing")
    return missing


def _apply_config_for_plan(plan: Mapping[str, Any], *, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    config_path = str(plan.get("config_path") or "")
    if config_path:
        return read_external_config(env=env, config_path=config_path)
    return read_external_config(env=env)


def _ssh_transfer_package(plan: Mapping[str, Any], config: Mapping[str, Any], package_dir: Path) -> dict[str, Any]:
    ssh = shutil.which("ssh")
    scp = shutil.which("scp")
    if not ssh or not scp:
        return {"status": "fail", "errors": ["ssh and scp executables are required for apply"], "warnings": []}
    host = str(config.get("host") or "")
    user = str(config.get("user") or "")
    remote_dir = str(config.get("remote_dir") or "")
    port = str(int(config.get("ssh_port") or 22))
    key = str(config.get("ssh_key_path") or "")
    target = f"{user}@{host}"
    ssh_base = [ssh, "-p", port, "-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
    scp_base = [scp, "-P", port, "-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
    if key:
        ssh_base.extend(["-i", key])
        scp_base.extend(["-i", key])
    mkdir_cmd = [*ssh_base, target, "mkdir", "-p", remote_dir]
    mkdir = subprocess.run(mkdir_cmd, capture_output=True, text=True, timeout=30, check=False)
    if mkdir.returncode != 0:
        return {"status": "fail", "errors": [f"remote directory creation failed: {_redact_process_error(mkdir.stderr or mkdir.stdout)}"], "warnings": []}
    transfer_items = [str(path) for path in sorted(package_dir.iterdir())]
    scp_cmd = [*scp_base, "-r", *transfer_items, f"{target}:{remote_dir}/"]
    transfer = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=120, check=False)
    if transfer.returncode != 0:
        return {"status": "fail", "errors": [f"package transfer failed: {_redact_process_error(transfer.stderr or transfer.stdout)}"], "warnings": []}
    return {
        "status": "pass",
        "deployment_status": "transfer_complete_manual_start_required",
        "remote_start_status": "manual_required",
        "warnings": ["package transfer completed; starting the remote read-only server remains a manual operator action"],
    }


def _status_payload(route_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    for item in route_results:
        if str(item.get("url") or "").rstrip("/").endswith("/api/status") or str(item.get("path") or "") == "/api/status":
            try:
                loaded = json.loads(str(item.get("body") or "{}"))
            except json.JSONDecodeError:
                return {}
            return loaded if isinstance(loaded, dict) else {}
    return {}


def _smoke_failures(
    route_results: Sequence[Mapping[str, Any]],
    blocked_results: Sequence[Mapping[str, Any]],
    status_payload: Mapping[str, Any],
) -> list[str]:
    failures: list[str] = []
    for item in route_results:
        if int(item.get("status_code") or 0) != 200:
            failures.append(f"public route {item.get('url') or item.get('path')} returned {item.get('status_code')}")
    for item in blocked_results:
        if int(item.get("status_code") or 0) not in {403, 404}:
            failures.append(f"blocked Workbench route {item.get('url') or item.get('path')} returned {item.get('status_code')}")
    if status_payload:
        expected = {
            "read_only": True,
            "public_alpha_mode": True,
            "live_metadata_enabled": False,
            "public_live_fanout": False,
            "workbench_exposed": False,
            "mutation_enabled": False,
            "downloads_enabled": False,
        }
        for key, value in expected.items():
            if status_payload.get(key) is not value:
                failures.append(f"/api/status {key} expected {value!r}")
        for key in ("artifact_verified_count", "reviewed_artifact_gate_count"):
            if int(status_payload.get(key) or 0) < 25:
                failures.append(f"/api/status {key} must be at least 25")
        for key in ("binary_verified_count", "download_safe_count", "execution_safe_count", "rights_cleared_count"):
            if int(status_payload.get(key) or 0) != 0:
                failures.append(f"/api/status {key} must remain 0")
    else:
        failures.append("/api/status response was not valid JSON")
    return failures


def _http_probe(method: str, url: str) -> dict[str, Any]:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    conn = http.client.HTTPConnection(parsed.hostname or "", parsed.port or 80, timeout=8)
    try:
        conn.request(method, path)
        response = conn.getresponse()
        body = response.read().decode("utf-8", errors="replace")
        return {"method": method, "url": url, "status_code": response.status, "body": body}
    finally:
        conn.close()


def _payload_secret_errors(label: str, value: Any) -> list[str]:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=True)
    lowered = text.casefold()
    errors = []
    for marker in SECRET_MARKERS:
        if marker.casefold() in lowered:
            errors.append(f"{label} contains forbidden secret marker {marker}")
    return errors


def _config_result(
    *,
    status: str,
    source: str,
    payload: Mapping[str, Any] | None = None,
    errors: Sequence[str] | None = None,
    warnings: Sequence[str] | None = None,
) -> dict[str, Any]:
    cfg = dict(payload or {})
    return {
        "schema_version": "eureka.external_staging_config_status.v0",
        "status": status,
        "config_source": source,
        "host_configured": bool(str(cfg.get("host") or "").strip()),
        "user_configured": bool(str(cfg.get("user") or "").strip()),
        "remote_dir_configured": bool(str(cfg.get("remote_dir") or "").strip()),
        "base_url_configured": bool(str(cfg.get("base_url") or "").strip()),
        "ssh_key_configured": bool(str(cfg.get("ssh_key_path") or cfg.get("ssh_key") or "").strip()),
        "bind_host": str(cfg.get("bind_host") or DEFAULT_BIND_HOST),
        "service_port": _int(cfg.get("service_port"), DEFAULT_SERVICE_PORT),
        "exposure_approved": _config_bool(cfg, "exposure_approved", False),
        "deployment_mode": str(cfg.get("deployment_mode") or "ssh"),
        "public_alpha_mode": _config_bool(cfg, "public_alpha_mode", True),
        "read_only": _config_bool(cfg, "read_only", True),
        "live_metadata_enabled": _config_bool(cfg, "live_metadata_enabled", False),
        "workbench_enabled": _config_bool(cfg, "workbench_enabled", False),
        "public_live_fanout": _config_bool(cfg, "public_live_fanout", False),
        "mutation_enabled": _config_bool(cfg, "mutation_enabled", False),
        "downloads_enabled": _config_bool(cfg, "downloads_enabled", False),
        "secret_fields_redacted": True,
        "errors": list(errors or []),
        "warnings": list(warnings or []),
    }


def _validate_config_payload(payload: Mapping[str, Any], *, require_apply_fields: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if int(payload.get("config_schema_version") or 0) != CONFIG_SCHEMA_VERSION:
        errors.append(f"config_schema_version must be {CONFIG_SCHEMA_VERSION}")
    deployment_mode = str(payload.get("deployment_mode") or "ssh")
    if deployment_mode not in {"ssh", "manual"}:
        errors.append("deployment_mode must be ssh or manual")
    if payload.get("public_alpha_mode") is not True:
        errors.append("public_alpha_mode must be true")
    if payload.get("read_only") is not True:
        errors.append("read_only must be true")
    for key in CONFIG_SAFETY_FALSE_FIELDS:
        if payload.get(key, False) is True:
            errors.append(f"{key} must be false")
    bind_host = str(payload.get("bind_host") or DEFAULT_BIND_HOST)
    exposure = _config_bool(payload, "exposure_approved", False)
    if bind_host not in {"127.0.0.1", "localhost", "::1"} and not exposure:
        errors.append("non-loopback bind_host requires exposure_approved true")
    base_url = str(payload.get("base_url") or "")
    if base_url and not _base_url_allowed(base_url, exposure_approved=exposure):
        errors.append("non-local base_url requires exposure_approved true")
    if require_apply_fields and deployment_mode == "ssh":
        for key in ("host", "user", "remote_dir"):
            if not str(payload.get(key) or "").strip():
                errors.append(f"{key} is required for ssh deployment mode")
    ssh_key = str(payload.get("ssh_key_path") or payload.get("ssh_key") or "").strip()
    if ssh_key and not Path(ssh_key).is_file():
        errors.append("ssh_key_path is configured but unreadable")
    if not base_url:
        warnings.append("base_url is missing; smoke will remain blocked")
    errors.extend(_payload_secret_errors("external_staging_config_reportable_fields", _redacted_config_for_scan(payload)))
    return _dedupe(errors), _dedupe(warnings)


def _redacted_config_for_scan(payload: Mapping[str, Any]) -> dict[str, Any]:
    redacted = dict(payload)
    if redacted.get("ssh_key_path") or redacted.get("ssh_key"):
        redacted["ssh_key_path"] = "configured:redacted"
        redacted.pop("ssh_key", None)
    return redacted


def _config_payload_from_env(env: Mapping[str, str]) -> dict[str, Any]:
    return {
        "config_schema_version": CONFIG_SCHEMA_VERSION,
        "host": env.get("EUREKA_STAGING_HOST", ""),
        "user": env.get("EUREKA_STAGING_USER", ""),
        "ssh_port": _int(env.get("EUREKA_STAGING_SSH_PORT", "22"), 22),
        "ssh_key_path": env.get("EUREKA_STAGING_SSH_KEY", ""),
        "remote_dir": env.get("EUREKA_STAGING_REMOTE_DIR", ""),
        "base_url": env.get("EUREKA_STAGING_BASE_URL", ""),
        "service_port": _int(env.get("EUREKA_STAGING_SERVICE_PORT", str(DEFAULT_SERVICE_PORT)), DEFAULT_SERVICE_PORT),
        "bind_host": env.get("EUREKA_STAGING_BIND_HOST", DEFAULT_BIND_HOST),
        "exposure_approved": _truthy(env.get("EUREKA_STAGING_EXPOSURE_APPROVED", "")),
        "deployment_mode": "ssh",
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "workbench_enabled": False,
        "public_live_fanout": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
    }


def _has_env_config(env: Mapping[str, str]) -> bool:
    return any(str(env.get(f"EUREKA_STAGING_{field}") or "").strip() for field in ENV_FIELDS)


def _config_bool(payload: Mapping[str, Any], key: str, default: bool) -> bool:
    if key not in payload:
        return default
    value = payload.get(key)
    if isinstance(value, bool):
        return value
    return _truthy(value)


def _safe_local_config_path(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if any(marker.casefold() in text.casefold() for marker in SECRET_MARKERS):
        return ""
    return text


def _base_url_allowed(value: str, *, exposure_approved: bool) -> bool:
    text = str(value or "").strip()
    if not text:
        return True
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").casefold()
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True
    return bool(exposure_approved)


def _redact_process_error(value: str) -> str:
    text = value.strip().replace("\r", " ").replace("\n", " ")
    for marker in SECRET_MARKERS:
        text = text.replace(marker, "[redacted]")
    return text[:400]


def _presence_redaction(value: Any) -> str:
    return "configured:redacted" if str(value or "").strip() else ""


def _safe_base_url(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if any(marker.casefold() in text.casefold() for marker in SECRET_MARKERS):
        return ""
    if text.startswith("http://") or text.startswith("https://"):
        return text.rstrip("/")
    return ""


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _truthy(value: Any) -> bool:
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y", "approved"}


def _read_json(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _read_json_if_possible(path: str | Path) -> dict[str, Any]:
    try:
        return _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _file_sha256(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""


def _dedupe(values: Sequence[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

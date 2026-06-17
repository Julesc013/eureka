"""Local-machine public exposure planning for public-alpha.

This module records the decision to pursue a local-machine hosting path without
enabling network exposure. It is a planning/gating layer, not a tunnel, reverse
proxy, firewall, DNS, TLS, or launch implementation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from runtime.local.corpus_gate_closeout import DEFAULT_GATE_TARGET
from runtime.local.local_machine_staging_mvp import validate_report as validate_local_machine_staging_report
from runtime.local.public_alpha_ops_posture import compatibility_fields as public_alpha_ops_compatibility_fields
from runtime.local.public_alpha_ops_posture import validate_ops_posture as validate_public_alpha_ops_posture


TASK_ID = "LOCAL-MACHINE-PUBLIC-EXPOSURE-PLAN-00"
PLAN_SCHEMA_VERSION = "eureka.local_machine_public_exposure_plan.v0"
REPORT_SCHEMA_VERSION = "eureka.local_machine_public_exposure_report.v0"
DEFAULT_OUT = ".eureka/local-machine-public-exposure/public-alpha/latest"
PLAN_JSON = "local_machine_public_exposure_plan.json"
REPORT_JSON = "local_machine_public_exposure_report.json"
REPORT_MD = "LOCAL_MACHINE_PUBLIC_EXPOSURE_REPORT.md"
EXPOSURE_MODES = (
    "none",
    "loopback_only",
    "lan_only",
    "reverse_tunnel",
    "reverse_proxy",
    "router_port_forward",
    "direct_public_ip",
)
TLS_STATUSES = ("missing", "planned", "configured", "validated")
DOMAIN_STATUSES = ("missing", "planned", "configured", "validated")
AUTH_POSTURES = ("missing", "readonly_noauth_proposed", "readonly_noauth_approved", "auth_required")
OPS_POSTURES = ("missing", "planned", "configured", "validated")
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
SAFETY_ZERO_FIELDS = (
    "binary_verified_count",
    "download_safe_count",
    "execution_safe_count",
    "rights_cleared_count",
)
PLAN_REQUIRED_FIELDS = (
    "task_id",
    "plan_schema_version",
    "selected_hosting_path",
    "exposure_mode",
    "public_exposure_enabled",
    "local_machine_staging_status",
    "local_machine_host",
    "local_machine_port",
    "proposed_bind_host",
    "proposed_base_url",
    "proposed_public_url",
    "domain_status",
    "tls_status",
    "production_auth_or_noauth_posture",
    "rate_limit_posture",
    "logging_posture",
    "monitoring_posture",
    "restart_posture",
    "rollback_posture",
    "firewall_posture",
    "router_or_tunnel_posture",
    "privacy_posture",
    "takedown_or_report_issue_posture",
    "public_workbench_exposed",
    "public_mutation_enabled",
    "live_metadata_enabled",
    "public_live_fanout",
    "downloads_enabled",
    "install_emulation_enabled",
    "corpus_gate_status",
    "reviewed_artifact_gate_count",
    "artifact_verified_count",
    "binary_verified_count",
    "download_safe_count",
    "execution_safe_count",
    "rights_cleared_count",
    "external_staging_deferred",
    "remaining_blockers",
    "warnings",
    "next_recommended_task",
)


def build_plan(
    *,
    local_machine_staging_report: str | Path,
    release_check_report: str | Path,
    launch_gate_report: str | Path,
    out_dir: str | Path,
    exposure_mode: str = "loopback_only",
    public_base_url: str = "",
    domain: str = "",
    tls_status: str = "missing",
    production_auth_posture: str = "missing",
    rate_limit_posture: str = "missing",
    ops_posture: str | Path | Mapping[str, Any] | None = None,
    operator_approval_file: str | Path | None = None,
    allow_public_exposure_plan: bool = False,
) -> dict[str, Any]:
    staging_path = Path(local_machine_staging_report)
    release_path = Path(release_check_report)
    launch_path = Path(launch_gate_report)
    staging = _read_json(staging_path)
    release = _read_json(release_path)
    launch = _read_json(launch_path)
    staging_errors = validate_local_machine_staging_report(staging_path) if staging_path.is_file() else ["local-machine staging report missing"]
    mode = exposure_mode if exposure_mode in EXPOSURE_MODES else "loopback_only"
    host = str(staging.get("host") or "127.0.0.1")
    port = int(staging.get("port") or 8765)
    proposed_bind = _proposed_bind_host(mode, host)
    proposed_base = public_base_url or _default_base_url(mode, host, port)
    proposed_public = public_base_url if mode in {"lan_only", "reverse_tunnel", "reverse_proxy", "router_port_forward", "direct_public_ip"} else ""
    domain_status = _domain_status(domain, proposed_public)
    approval_status = _approval_file_status(operator_approval_file)
    ops_path, ops_payload, ops_validation, ops_compat = _public_alpha_ops_inputs(ops_posture)
    if not ops_validation.get("errors") and not ops_validation.get("ops_blockers"):
        production_auth_posture = str(ops_compat.get("production_auth_or_noauth_posture") or production_auth_posture)
        rate_limit_posture = str(ops_compat.get("rate_limit_posture") or rate_limit_posture)
        if ops_compat.get("operator_approval_file_status") == "present":
            approval_status = "present"

    base_plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "plan_schema_version": PLAN_SCHEMA_VERSION,
        "selected_hosting_path": "local_machine",
        "exposure_mode": mode,
        "public_exposure_enabled": False,
        "allow_public_exposure_plan": bool(allow_public_exposure_plan),
        "local_machine_staging_report_path": str(staging_path),
        "local_machine_staging_report_digest": _file_sha256(staging_path),
        "local_machine_staging_status": _local_machine_staging_status(staging, staging_errors),
        "local_machine_host": host,
        "local_machine_port": port,
        "proposed_bind_host": proposed_bind,
        "proposed_base_url": proposed_base,
        "proposed_public_url": proposed_public,
        "domain": domain,
        "domain_status": domain_status,
        "tls_status": tls_status,
        "production_auth_or_noauth_posture": production_auth_posture,
        "operator_approval_file_status": approval_status,
        "rate_limit_posture": rate_limit_posture,
        "logging_posture": str(ops_compat.get("logging_posture") or "missing"),
        "monitoring_posture": str(ops_compat.get("monitoring_posture") or "missing"),
        "restart_posture": str(ops_compat.get("restart_posture") or "missing"),
        "rollback_posture": str(ops_compat.get("rollback_posture") or "missing"),
        "firewall_posture": str(ops_compat.get("firewall_posture") or "missing"),
        "router_or_tunnel_posture": str(ops_compat.get("router_or_tunnel_posture") or "missing"),
        "privacy_posture": str(ops_compat.get("privacy_posture") or "missing"),
        "takedown_or_report_issue_posture": str(ops_compat.get("takedown_or_report_issue_posture") or "missing"),
        "public_alpha_ops_posture_path": str(ops_path) if ops_path else "",
        "public_alpha_ops_posture_digest": _file_sha256(ops_path) if ops_path else "",
        "public_alpha_ops_posture_status": str(ops_validation.get("plan_status") or ("not_provided" if not ops_posture else "missing")),
        "public_alpha_ops_posture_validation_errors": list(ops_validation.get("errors") or []),
        "public_alpha_ops_posture_ops_blockers": list(ops_validation.get("ops_blockers") or []),
        "public_workbench_exposed": False,
        "public_mutation_enabled": False,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "downloads_enabled": False,
        "install_emulation_enabled": False,
        "corpus_gate_status": str(staging.get("corpus_gate_status") or "unknown"),
        "reviewed_artifact_gate_count": int(staging.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(staging.get("artifact_verified_count") or 0),
        "binary_verified_count": int(staging.get("binary_verified_count") or 0),
        "download_safe_count": int(staging.get("download_safe_count") or 0),
        "execution_safe_count": int(staging.get("execution_safe_count") or 0),
        "rights_cleared_count": int(staging.get("rights_cleared_count") or 0),
        "release_check_report_path": str(release_path),
        "release_check_report_digest": _file_sha256(release_path),
        "release_check_status": str(release.get("status") or "unknown"),
        "release_status": str(release.get("release_status") or "unknown"),
        "full_discovery_status": str(release.get("full_discovery_status") or "not_run"),
        "release_promotion_status": str(release.get("release_promotion_status") or "not_run"),
        "launch_gate_report_path": str(launch_path),
        "launch_gate_report_digest": _file_sha256(launch_path),
        "launch_status": str(launch.get("launch_status") or "UNKNOWN"),
        "launch_approval_status": str(launch.get("public_launch_approval_status") or "missing"),
        "external_staging_status": str(launch.get("external_staging_report_status") or "unknown"),
        "external_staging_deferred": True,
        "local_machine_staging_validation_errors": staging_errors,
        "generated_at": "not_recorded_deterministic_local_machine_public_exposure_plan",
    }
    blockers = _plan_blockers(base_plan)
    warnings = ["public exposure is intentionally disabled; this is a plan only"]
    if base_plan["external_staging_deferred"]:
        warnings.append("external SSH staging is deferred for the selected local-machine hosting path")
    base_plan["remaining_blockers"] = blockers
    base_plan["warnings"] = _dedupe(warnings)
    base_plan["next_recommended_task"] = _next_task(blockers)
    return base_plan


def write_plan(plan: Mapping[str, Any], out_dir: str | Path) -> Path:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / PLAN_JSON
    _write_json(path, plan)
    return path


def validate_plan(plan: str | Path | Mapping[str, Any]) -> list[str]:
    try:
        payload = _load_payload(plan)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"plan could not be read: {type(exc).__name__}"]
    errors = [f"missing required field: {key}" for key in PLAN_REQUIRED_FIELDS if key not in payload]
    if errors:
        return errors
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if payload.get("selected_hosting_path") != "local_machine":
        errors.append("selected_hosting_path must be local_machine")
    if payload.get("exposure_mode") not in EXPOSURE_MODES:
        errors.append("exposure_mode is not recognized")
    if payload.get("public_exposure_enabled") is not False:
        errors.append("public_exposure_enabled must remain false in this task")
    if payload.get("local_machine_staging_status") != "pass":
        errors.append("local_machine_staging_status must be pass")
    if payload.get("corpus_gate_status") != "pass":
        errors.append("corpus_gate_status must be pass")
    if int(payload.get("reviewed_artifact_gate_count") or 0) < DEFAULT_GATE_TARGET:
        errors.append(f"reviewed_artifact_gate_count must be at least {DEFAULT_GATE_TARGET}")
    if int(payload.get("artifact_verified_count") or 0) < DEFAULT_GATE_TARGET:
        errors.append(f"artifact_verified_count must be at least {DEFAULT_GATE_TARGET}")
    errors.extend(_safe_false_errors(payload))
    for key in SAFETY_ZERO_FIELDS:
        if int(payload.get(key) or 0) != 0:
            errors.append(f"{key} must remain 0")
    errors.extend(_posture_errors(payload, source_label="plan"))
    if payload.get("external_staging_deferred") is not True:
        errors.append("external_staging_deferred must be true for selected local-machine path")
    if not payload.get("remaining_blockers"):
        errors.append("remaining_blockers must list unresolved launch blockers")
    errors.extend(_secret_errors(payload))
    return _dedupe(errors)


def build_report(plan: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    payload = _load_payload(plan)
    plan_errors = validate_plan(payload)
    blockers = _report_blockers(payload, plan_errors)
    categories = _blocker_categories(blockers)
    ops_status = _ops_posture_status(payload)
    report_status = "FAIL" if plan_errors else ("PASS_WITH_WARNINGS" if blockers else "PASS")
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": report_status,
        "selected_hosting_path": str(payload.get("selected_hosting_path") or ""),
        "exposure_mode": str(payload.get("exposure_mode") or ""),
        "public_exposure_enabled": bool(payload.get("public_exposure_enabled") is True),
        "local_machine_staging_status": str(payload.get("local_machine_staging_status") or "unknown"),
        "corpus_gate_status": str(payload.get("corpus_gate_status") or "unknown"),
        "reviewed_artifact_gate_count": int(payload.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(payload.get("artifact_verified_count") or 0),
        "public_readiness_status": "blocked" if blockers else "ready_for_approval",
        "tls_status": str(payload.get("tls_status") or "missing"),
        "domain_status": str(payload.get("domain_status") or "missing"),
        "production_auth_or_noauth_posture": str(payload.get("production_auth_or_noauth_posture") or "missing"),
        "rate_limit_posture": str(payload.get("rate_limit_posture") or "missing"),
        "ops_posture_status": ops_status,
        "release_check_status": str(payload.get("release_check_status") or "unknown"),
        "full_discovery_status": str(payload.get("full_discovery_status") or "not_run"),
        "release_promotion_status": str(payload.get("release_promotion_status") or "not_run"),
        "launch_approval_status": str(payload.get("launch_approval_status") or "missing"),
        "external_staging_status": str(payload.get("external_staging_status") or "unknown"),
        "external_staging_deferred": bool(payload.get("external_staging_deferred") is True),
        "public_workbench_exposed": bool(payload.get("public_workbench_exposed") is True),
        "public_mutation_enabled": bool(payload.get("public_mutation_enabled") is True),
        "live_metadata_enabled": bool(payload.get("live_metadata_enabled") is True),
        "public_live_fanout": bool(payload.get("public_live_fanout") is True),
        "downloads_enabled": bool(payload.get("downloads_enabled") is True),
        "install_emulation_enabled": bool(payload.get("install_emulation_enabled") is True),
        "binary_verified_count": int(payload.get("binary_verified_count") or 0),
        "download_safe_count": int(payload.get("download_safe_count") or 0),
        "execution_safe_count": int(payload.get("execution_safe_count") or 0),
        "rights_cleared_count": int(payload.get("rights_cleared_count") or 0),
        "blocker_categories": categories,
        "blockers": blockers,
        "warnings": _dedupe(list(payload.get("warnings") or []) + ["public launch remains blocked until exposure, ops, release, and approval gates clear"]),
        "next_recommended_task": _next_task(blockers),
        "plan_validation_errors": plan_errors,
        "generated_at": "not_recorded_deterministic_local_machine_public_exposure_report",
    }


def write_report(report: Mapping[str, Any], out_dir: str | Path) -> Path:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / REPORT_JSON
    _write_json(json_path, report)
    (output / REPORT_MD).write_text(render_markdown_report(report), encoding="utf-8")
    return json_path


def validate_report(report: str | Path | Mapping[str, Any]) -> list[str]:
    try:
        payload = _load_payload(report)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"report could not be read: {type(exc).__name__}"]
    required = (
        "task_id",
        "status",
        "selected_hosting_path",
        "exposure_mode",
        "public_exposure_enabled",
        "local_machine_staging_status",
        "corpus_gate_status",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
        "public_readiness_status",
        "tls_status",
        "domain_status",
        "production_auth_or_noauth_posture",
        "rate_limit_posture",
        "ops_posture_status",
        "release_check_status",
        "full_discovery_status",
        "release_promotion_status",
        "launch_approval_status",
        "external_staging_status",
        "external_staging_deferred",
        "blocker_categories",
        "blockers",
        "warnings",
        "next_recommended_task",
    )
    errors = [f"missing required field: {key}" for key in required if key not in payload]
    if errors:
        return errors
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if payload.get("status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if payload.get("selected_hosting_path") != "local_machine":
        errors.append("selected_hosting_path must be local_machine")
    if payload.get("public_exposure_enabled") is not False:
        errors.append("public_exposure_enabled must remain false")
    if payload.get("public_readiness_status") in {"ready", "launch_ready"}:
        errors.append("report must not claim launch readiness")
    errors.extend(_safe_false_errors(payload))
    for key in SAFETY_ZERO_FIELDS:
        if int(payload.get(key) or 0) != 0:
            errors.append(f"{key} must remain 0")
    errors.extend(_posture_errors(payload, source_label="report"))
    blocker_ids = {str(item.get("id")) for item in payload.get("blockers") or [] if isinstance(item, Mapping)}
    required_blockers = {
        "public_exposure_not_configured",
        "tls_domain_missing",
        "production_auth_or_noauth_posture_missing",
        "ops_posture_missing",
        "full_discovery_not_passed",
        "release_promotion_not_passed",
        "public_launch_approval_missing",
    }
    missing = sorted(required_blockers - blocker_ids)
    errors.extend(f"missing blocker: {blocker}" for blocker in missing)
    errors.extend(_secret_errors(payload))
    return _dedupe(errors)


def render_plan_status(plan: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"selected_hosting_path: {plan.get('selected_hosting_path')}",
            f"exposure_mode: {plan.get('exposure_mode')}",
            f"public_exposure_enabled: {str(plan.get('public_exposure_enabled')).lower()}",
            f"local_machine_staging_status: {plan.get('local_machine_staging_status')}",
            f"proposed_bind_host: {plan.get('proposed_bind_host')}",
            f"proposed_base_url: {plan.get('proposed_base_url')}",
            f"proposed_public_url: {plan.get('proposed_public_url')}",
            f"domain_status: {plan.get('domain_status')}",
            f"tls_status: {plan.get('tls_status')}",
            f"production_auth_or_noauth_posture: {plan.get('production_auth_or_noauth_posture')}",
            f"rate_limit_posture: {plan.get('rate_limit_posture')}",
            f"external_staging_deferred: {str(plan.get('external_staging_deferred')).lower()}",
            f"remaining_blockers: {len(plan.get('remaining_blockers') or [])}",
            f"next_recommended_task: {plan.get('next_recommended_task')}",
        ]
    ) + "\n"


def render_markdown_report(report: Mapping[str, Any]) -> str:
    blockers = [f"- [{item.get('category')}] {item.get('id')}: {item.get('message')}" for item in report.get("blockers") or [] if isinstance(item, Mapping)] or ["- none"]
    warnings = [f"- {item}" for item in report.get("warnings") or []] or ["- none"]
    return "\n".join(
        [
            "# Local-Machine Public Exposure Report",
            "",
            f"- Status: {report.get('status')}",
            f"- Selected hosting path: {report.get('selected_hosting_path')}",
            f"- Exposure mode: {report.get('exposure_mode')}",
            f"- Public exposure enabled: {str(report.get('public_exposure_enabled')).lower()}",
            f"- Public readiness: {report.get('public_readiness_status')}",
            f"- TLS: {report.get('tls_status')}",
            f"- Domain: {report.get('domain_status')}",
            f"- Auth/no-auth posture: {report.get('production_auth_or_noauth_posture')}",
            f"- Ops posture: {report.get('ops_posture_status')}",
            f"- External SSH staging deferred: {str(report.get('external_staging_deferred')).lower()}",
            "",
            "## Blockers",
            "",
            *blockers,
            "",
            "## Warnings",
            "",
            *warnings,
            "",
            "This report is a planning artifact only. It does not expose the service, configure DNS/TLS, approve no-auth, run full discovery, promote release state, or approve public launch.",
            "",
        ]
    )


def load_json(path: str | Path) -> dict[str, Any]:
    return _read_json(Path(path))


def _plan_blockers(plan: Mapping[str, Any]) -> list[dict[str, str]]:
    blockers = []
    if plan.get("public_exposure_enabled") is not True:
        blockers.append(_blocker("deployment_blockers", "public_exposure_not_configured", "public exposure is not configured"))
    if plan.get("tls_status") not in {"configured", "validated"} or plan.get("domain_status") not in {"configured", "validated"}:
        blockers.append(_blocker("deployment_blockers", "tls_domain_missing", "TLS/domain or approved tunnel URL is missing"))
    if plan.get("production_auth_or_noauth_posture") != "readonly_noauth_approved":
        blockers.append(_blocker("deployment_blockers", "production_auth_or_noauth_posture_missing", "production auth or approved read-only no-auth posture is missing"))
    if _ops_posture_status(plan) != "pass":
        blockers.append(_blocker("deployment_blockers", "ops_posture_missing", "rate limit, logging, monitoring, privacy, restart, rollback, and reporting posture is incomplete"))
    if plan.get("full_discovery_status") != "pass":
        blockers.append(_blocker("release_process_blockers", "full_discovery_not_passed", "full discovery has not passed"))
    if plan.get("release_promotion_status") != "pass":
        blockers.append(_blocker("release_process_blockers", "release_promotion_not_passed", "release promotion checks have not passed"))
    if plan.get("launch_approval_status") != "approved":
        blockers.append(_blocker("approval_blockers", "public_launch_approval_missing", "public launch approval is missing"))
    return blockers


def _report_blockers(plan: Mapping[str, Any], plan_errors: Sequence[str]) -> list[dict[str, str]]:
    blockers = list(plan.get("remaining_blockers") or [])
    for error in plan_errors:
        blockers.append(_blocker("safety_blockers", _slug(error), error, status="failed"))
    return [item for item in blockers if isinstance(item, Mapping)]


def _blocker(category: str, blocker_id: str, message: str, *, status: str = "blocked") -> dict[str, str]:
    return {"category": category, "id": blocker_id, "status": status, "message": message}


def _blocker_categories(blockers: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    categories = {
        "deployment_blockers": [],
        "release_process_blockers": [],
        "approval_blockers": [],
        "safety_blockers": [],
    }
    for blocker in blockers:
        category = str(blocker.get("category") or "safety_blockers")
        categories.setdefault(category, []).append(str(blocker.get("id") or "unknown"))
    return categories


def _safe_false_errors(payload: Mapping[str, Any]) -> list[str]:
    expectations = {
        "public_workbench_exposed": False,
        "public_mutation_enabled": False,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "downloads_enabled": False,
        "install_emulation_enabled": False,
    }
    return [f"{key} must be false" for key, expected in expectations.items() if payload.get(key) is not expected]


def _posture_errors(payload: Mapping[str, Any], *, source_label: str) -> list[str]:
    errors: list[str] = []
    if payload.get("tls_status") not in TLS_STATUSES:
        errors.append("tls_status is not recognized")
    if payload.get("domain_status") not in DOMAIN_STATUSES:
        errors.append("domain_status is not recognized")
    if payload.get("production_auth_or_noauth_posture") not in AUTH_POSTURES:
        errors.append("production_auth_or_noauth_posture is not recognized")
    for key in (
        "rate_limit_posture",
        "logging_posture",
        "monitoring_posture",
        "restart_posture",
        "rollback_posture",
        "firewall_posture",
        "router_or_tunnel_posture",
        "privacy_posture",
        "takedown_or_report_issue_posture",
    ):
        if key in payload and payload.get(key) not in OPS_POSTURES:
            errors.append(f"{key} is not recognized")
    if payload.get("tls_status") == "validated":
        errors.append(f"{source_label} claims TLS validated without evidence")
    if payload.get("domain_status") in {"configured", "validated"}:
        errors.append(f"{source_label} claims domain configured without evidence")
    if payload.get("production_auth_or_noauth_posture") == "readonly_noauth_approved" and payload.get("operator_approval_file_status") != "present":
        errors.append(f"{source_label} claims no-auth approved without evidence")
    return errors


def _ops_posture_status(payload: Mapping[str, Any]) -> str:
    keys = (
        "rate_limit_posture",
        "logging_posture",
        "monitoring_posture",
        "restart_posture",
        "rollback_posture",
        "firewall_posture",
        "router_or_tunnel_posture",
        "privacy_posture",
        "takedown_or_report_issue_posture",
    )
    values = [str(payload.get(key) or "missing") for key in keys]
    return "pass" if all(value in {"configured", "validated"} for value in values) else "missing"


def _next_task(blockers: Sequence[Mapping[str, Any]]) -> str:
    ids = {str(item.get("id") or "") for item in blockers}
    if "ops_posture_missing" in ids or "production_auth_or_noauth_posture_missing" in ids:
        return "PUBLIC-ALPHA-OPS-POSTURE-00"
    if "public_exposure_not_configured" in ids:
        return "LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00"
    if "full_discovery_not_passed" in ids or "release_promotion_not_passed" in ids:
        return "PUBLIC-ALPHA-FULL-DISCOVERY-RELEASE-CHECK-00"
    if "public_launch_approval_missing" in ids:
        return "PUBLIC-ALPHA-LAUNCH-APPROVAL-00"
    return "PUBLIC-ALPHA-LAUNCH-00"


def _local_machine_staging_status(staging: Mapping[str, Any], errors: Sequence[str]) -> str:
    if errors:
        return "fail"
    if staging.get("local_machine_staging_status") == "pass" and staging.get("public_exposure") is False:
        return "pass"
    return "unknown"


def _proposed_bind_host(mode: str, host: str) -> str:
    if mode in {"lan_only", "router_port_forward", "direct_public_ip"}:
        return "0.0.0.0"
    return host or "127.0.0.1"


def _default_base_url(mode: str, host: str, port: int) -> str:
    if mode in {"lan_only", "router_port_forward", "direct_public_ip"}:
        return f"http://<planned-host>:{port}"
    if mode in {"reverse_tunnel", "reverse_proxy"}:
        return "https://<planned-public-url>"
    return f"http://{host or '127.0.0.1'}:{port}"


def _domain_status(domain: str, public_url: str) -> str:
    if domain:
        return "planned"
    parsed = urlparse(public_url)
    if parsed.hostname and parsed.hostname not in {"127.0.0.1", "localhost"}:
        return "planned"
    return "missing"


def _approval_file_status(path: str | Path | None) -> str:
    if not path:
        return "not_provided"
    return "present" if Path(path).is_file() else "missing"


def _public_alpha_ops_inputs(
    source: str | Path | Mapping[str, Any] | None,
) -> tuple[Path | None, dict[str, Any], dict[str, Any], dict[str, Any]]:
    if source is None or source == "":
        return None, {}, {}, {}
    path = None if isinstance(source, Mapping) else Path(source)
    payload = dict(source) if isinstance(source, Mapping) else _read_json(path)  # type: ignore[arg-type]
    if not payload:
        return path, {}, {"errors": ["public-alpha ops posture missing"], "ops_blockers": []}, {}
    validation = validate_public_alpha_ops_posture(payload)
    if validation.get("errors") or validation.get("ops_blockers"):
        return path, payload, validation, {}
    return path, payload, validation, public_alpha_ops_compatibility_fields(payload)


def _load_payload(value: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return _read_json(Path(value))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _file_sha256(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""


def _secret_errors(value: Any) -> list[str]:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=True)
    lowered = text.casefold()
    return [f"payload contains forbidden secret marker: {marker}" for marker in SECRET_MARKERS if marker.casefold() in lowered]


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")[:80] or "item"


def _dedupe(values: Sequence[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

"""Public-alpha operations posture planning.

This module produces a local, machine-readable operations posture for the
read-only public alpha. It does not start a server, start a tunnel, enable
public exposure, mutate reviewed data, or approve launch.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


TASK_ID = "PUBLIC-ALPHA-OPS-POSTURE-00"
DECISION_ID = "QUEUE-OBJECTIVE-DECISION-00"
PLAN_SCHEMA_VERSION = "eureka.public_alpha_ops_posture.v0"
VALIDATION_SCHEMA_VERSION = "eureka.public_alpha_ops_posture_validation.v0"
PLAN_JSON = "ops_posture.json"
REPORT_MD = "OPS_POSTURE_REPORT.md"
DEFAULT_OUT = ".eureka/ops/public-alpha/latest"
DEFAULT_REPORT_CHANNEL = "https://github.com/Julesc013/eureka/issues"
DEFAULT_TAKEDOWN_CHANNEL = "https://github.com/Julesc013/eureka/issues"

EXPOSURE_MODES = (
    "none",
    "loopback_only",
    "lan_only",
    "reverse_tunnel",
    "reverse_proxy",
    "router_port_forward",
    "direct_public_ip",
)
AUTH_POSTURES = ("public_no_auth", "public_auth_required", "operator_decision_required")
OPS_COMPAT_STATUSES = ("missing", "planned", "configured", "validated")
PLAN_STATUSES = (
    "BLOCKED",
    "READY_FOR_EXPOSURE_PLAN",
    "READY_FOR_RELEASE_CHECK",
    "READY_FOR_APPROVAL",
    "READY",
)
SAFE_FALSE_FIELDS = (
    "public_mutation_enabled",
    "public_workbench_exposed",
    "live_metadata_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "accounts_enabled",
    "telemetry_enabled",
    "model_provider_calls_enabled",
    "public_live_fanout",
    "extraction_enabled",
    "production_readiness_claimed",
    "public_exposure_enabled",
    "tunnel_or_proxy_enabled",
)
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


def build_default_plan(
    *,
    operator: str = "",
    public_url: str = "",
    exposure_mode: str = "loopback_only",
    auth_posture: str = "public_no_auth",
    report_issue_channel: str = DEFAULT_REPORT_CHANNEL,
    takedown_channel: str = DEFAULT_TAKEDOWN_CHANNEL,
    bind_host: str = "127.0.0.1",
    bind_port: int = 8765,
    allow_public_exposure_plan: bool = False,
    generated_at: str | None = None,
    branch: str | None = None,
    head: str | None = None,
    worktree_status: str | None = None,
) -> dict[str, Any]:
    """Build the conservative public-alpha operations posture."""

    mode = exposure_mode if exposure_mode in EXPOSURE_MODES else "loopback_only"
    selected_auth = auth_posture if auth_posture in AUTH_POSTURES else "operator_decision_required"
    generated = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    repo_branch = branch if branch is not None else _git_stdout("git", "branch", "--show-current") or "unknown"
    repo_head = head if head is not None else _git_stdout("git", "rev-parse", "HEAD") or "unknown"
    repo_status = worktree_status if worktree_status is not None else _git_stdout("git", "status", "--short", "--branch") or "unknown"

    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "decision_id": DECISION_ID,
        "identity": {
            "task_id": TASK_ID,
            "generated_at": generated,
            "branch": repo_branch,
            "head": repo_head,
            "operator": operator or "local-operator",
            "mode": "public_alpha_ops_posture_plan",
            "worktree_status": repo_status,
        },
        "public_alpha_mode": True,
        "public_read_only": True,
        "public_mutation_enabled": False,
        "public_workbench_exposed": False,
        "live_metadata_enabled": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "accounts_enabled": False,
        "telemetry_enabled": False,
        "model_provider_calls_enabled": False,
        "public_live_fanout": False,
        "extraction_enabled": False,
        "safe_fixture_member_manifest_extraction_allowed": True,
        "production_readiness_claimed": False,
        "launch_approval_present": False,
        "public_exposure_enabled": False,
        "tunnel_or_proxy_enabled": False,
        "allow_public_exposure_plan": bool(allow_public_exposure_plan),
        "public_scope": {
            "read_only": True,
            "allowed_routes": [
                "/",
                "/health",
                "/status",
                "/api/status",
                "/about",
                "/method",
                "/search?q=",
                "/api/search?q=",
                "/record/{id}",
            ],
            "forbidden_routes": [
                "/workbench",
                "/api/workbench",
                "/review",
                "/api/review",
                "/admin",
                "/download",
                "/upload",
                "/mutate",
            ],
            "allowed_actions": ["read_status", "read_method", "search_reviewed_index", "read_record"],
            "forbidden_actions": [
                "public_mutation",
                "public_review",
                "public_workbench",
                "public_live_source_fanout",
                "download",
                "upload",
                "install",
                "emulate",
                "model_provider_truth",
            ],
        },
        "auth_posture": _auth_posture(selected_auth),
        "network_posture": {
            "exposure_mode": mode,
            "public_url": public_url,
            "tls_domain_status": _tls_domain_status(public_url),
            "tunnel_status": "not_started",
            "firewall_status": "loopback_only",
            "bind_host": bind_host,
            "bind_port": int(bind_port),
        },
        "safety_posture": {
            "no_mutation": True,
            "no_workbench": True,
            "no_live_fanout": True,
            "no_downloads": True,
            "no_uploads": True,
            "no_extraction": True,
            "no_ai_truth": True,
            "no_provider_truth": True,
        },
        "rate_limit_posture": {
            "enabled": True,
            "enforcement_location": "public_edge_or_tunnel_provider",
            "limits": {
                "requests_per_minute_per_ip": 60,
                "search_requests_per_minute_per_ip": 20,
            },
            "burst": {"requests_per_10_seconds_per_ip": 20},
            "failure_action": "return_429_or_provider_rate_limit_response",
            "compat_status": "configured",
        },
        "logging_posture": {
            "enabled": True,
            "redaction": "do_not_log_operator_tokens_private_paths_or_raw_private_data",
            "privacy_notes": "access logs and aggregate counts only; raw public query retention disabled by default",
            "retention": "short_window_or_provider_default_until_operator_sets_explicit_retention",
            "compat_status": "configured",
        },
        "monitoring_posture": {
            "health_checks": ["/health"],
            "status_checks": ["/status", "/api/status"],
            "route_smokes": [
                "/",
                "/about",
                "/method",
                "/search?q=manual%20for%20Sound%20Blaster%20CT1740",
                "/record/{id}",
            ],
            "alerting": "manual_operator_check_for_alpha",
            "first_monitoring_window_hours": 72,
            "compat_status": "configured",
        },
        "rollback_posture": {
            "stop_server_command": "Ctrl-C the local public-alpha server process",
            "stop_tunnel_command": "disable the selected tunnel/proxy route before stopping the local server",
            "disable_public_url_step": "remove or pause the tunnel/proxy public route",
            "restore_loopback_only_step": "rerun public-alpha server bound to 127.0.0.1 only",
            "rollback_owner": operator or "local-operator",
            "restart_posture": "manual_restart_for_alpha",
            "firewall_posture": "loopback_only_until_exposure_plan_selects_edge",
            "router_or_tunnel_posture": "no_tunnel_started_by_this_task",
            "privacy_posture": "no_accounts_no_public_telemetry_no_private_data_collection",
            "compat_status": "configured",
        },
        "incident_posture": {
            "report_issue_channel": report_issue_channel,
            "takedown_channel": takedown_channel,
            "abuse_channel": report_issue_channel,
            "emergency_disable_steps": [
                "disable the tunnel/proxy public route",
                "stop the local public-alpha server",
                "restore loopback-only configuration before restart",
            ],
            "compat_status": "configured" if report_issue_channel and takedown_channel else "missing",
        },
        "release_gate_inputs": {
            "expected_bundle": ".eureka/staging/public-alpha",
            "expected_rehearsal_report": ".eureka/rehearsal/public-alpha/latest/rehearsal_report.json",
            "expected_exposure_report": ".eureka/local-machine-public-exposure/public-alpha/latest/local_machine_public_exposure_report.json",
            "expected_full_discovery_report": "../eureka-test-runs/<run-id>/full_unittest_summary.json",
            "expected_release_promotion_report": ".eureka/release-promotion/public-alpha/latest/release_promotion_report.json",
            "expected_launch_approval": ".eureka/launch/public-alpha/approval/public_alpha_launch_approval.json",
        },
        "structure_guardrail": {
            "root_structure_accepted": True,
            "new_top_level_roots_created": False,
            "ops_home": ["runtime/local", "scripts", "docs/runbooks", "control/audits", ".eureka/ops"],
            "aide_control_boundary": "AIDE and control artifacts are guardrails/evidence, not product runtime truth.",
        },
        "compatibility": {},
        "blockers": [],
        "ops_blockers": [],
        "launch_blockers": [],
        "status": "BLOCKED",
        "next_recommended_task": "PUBLIC-ALPHA-OPS-POSTURE-00",
    }
    plan["compatibility"] = _compatibility_fields(plan)
    _refresh_status_fields(plan)
    return plan


def validate_ops_posture(plan: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    """Validate a posture plan and separate unsafe errors from launch blockers."""

    try:
        payload = _load_payload(plan)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "schema_version": VALIDATION_SCHEMA_VERSION,
            "status": "fail",
            "plan_status": "BLOCKED",
            "safe": False,
            "errors": [f"plan could not be read: {type(exc).__name__}"],
            "ops_blockers": [],
            "launch_blockers": [],
            "blockers": [],
            "next_recommended_task": "PUBLIC-ALPHA-OPS-POSTURE-00",
        }
    errors = _safety_errors(payload)
    ops_blockers = _ops_blockers(payload)
    launch_blockers = _launch_blockers(payload)
    plan_status = _status_for(errors, ops_blockers, launch_blockers, payload)
    return {
        "schema_version": VALIDATION_SCHEMA_VERSION,
        "status": "pass" if not errors else "fail",
        "plan_status": plan_status,
        "safe": not errors,
        "errors": errors,
        "ops_blockers": ops_blockers,
        "launch_blockers": launch_blockers,
        "blockers": ops_blockers + launch_blockers,
        "next_recommended_task": _next_task(plan_status, ops_blockers, launch_blockers),
    }


def status_summary(plan: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    payload = _load_payload(plan)
    validation = validate_ops_posture(payload)
    compat = _compatibility_fields(payload)
    return {
        "schema_version": "eureka.public_alpha_ops_posture_status.v0",
        "task_id": TASK_ID,
        "status": validation["plan_status"],
        "safe": validation["safe"],
        "public_read_only": bool(payload.get("public_read_only") is True),
        "public_mutation_enabled": bool(payload.get("public_mutation_enabled") is True),
        "public_workbench_exposed": bool(payload.get("public_workbench_exposed") is True),
        "live_metadata_enabled": bool(payload.get("live_metadata_enabled") is True),
        "downloads_enabled": bool(payload.get("downloads_enabled") is True),
        "uploads_enabled": bool(payload.get("uploads_enabled") is True),
        "public_exposure_enabled": bool(payload.get("public_exposure_enabled") is True),
        "auth_posture": str((payload.get("auth_posture") or {}).get("selected") or "missing") if isinstance(payload.get("auth_posture"), Mapping) else "missing",
        "rate_limit_posture": compat["rate_limit_posture"],
        "logging_posture": compat["logging_posture"],
        "monitoring_posture": compat["monitoring_posture"],
        "rollback_posture": compat["rollback_posture"],
        "report_takedown_posture": compat["takedown_or_report_issue_posture"],
        "errors": validation["errors"],
        "ops_blockers": validation["ops_blockers"],
        "launch_blockers": validation["launch_blockers"],
        "next_recommended_task": validation["next_recommended_task"],
    }


def write_plan(plan: Mapping[str, Any], out_dir: str | Path) -> Path:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / PLAN_JSON
    _write_json(path, plan)
    (output / REPORT_MD).write_text(render_markdown_report(plan), encoding="utf-8")
    return path


def render_status(summary: Mapping[str, Any]) -> str:
    ops_blockers = summary.get("ops_blockers") or []
    launch_blockers = summary.get("launch_blockers") or []
    lines = [
        f"status: {summary.get('status')}",
        f"safe: {str(summary.get('safe')).lower()}",
        f"public_read_only: {str(summary.get('public_read_only')).lower()}",
        f"public_mutation_enabled: {str(summary.get('public_mutation_enabled')).lower()}",
        f"public_workbench_exposed: {str(summary.get('public_workbench_exposed')).lower()}",
        f"live_metadata_enabled: {str(summary.get('live_metadata_enabled')).lower()}",
        f"downloads_enabled: {str(summary.get('downloads_enabled')).lower()}",
        f"uploads_enabled: {str(summary.get('uploads_enabled')).lower()}",
        f"public_exposure_enabled: {str(summary.get('public_exposure_enabled')).lower()}",
        f"auth_posture: {summary.get('auth_posture')}",
        f"ops_blockers: {len(ops_blockers)}",
        f"launch_blockers: {len(launch_blockers)}",
        f"next_recommended_task: {summary.get('next_recommended_task')}",
    ]
    if ops_blockers:
        lines.append("ops_blocker_ids: " + ", ".join(str(item.get("id")) for item in ops_blockers if isinstance(item, Mapping)))
    if launch_blockers:
        lines.append("launch_blocker_ids: " + ", ".join(str(item.get("id")) for item in launch_blockers if isinstance(item, Mapping)))
    return "\n".join(lines) + "\n"


def render_markdown_report(plan: Mapping[str, Any]) -> str:
    validation = validate_ops_posture(plan)
    summary = status_summary(plan)
    ops_blockers = _blocker_lines(validation["ops_blockers"])
    launch_blockers = _blocker_lines(validation["launch_blockers"])
    errors = [f"- {item}" for item in validation["errors"]] or ["- none"]
    return "\n".join(
        [
            "# Public Alpha Ops Posture",
            "",
            f"- Task: {TASK_ID}",
            f"- Status: {validation.get('plan_status')}",
            f"- Safe posture: {str(validation.get('safe')).lower()}",
            f"- Generated at: {(plan.get('identity') or {}).get('generated_at') if isinstance(plan.get('identity'), Mapping) else ''}",
            f"- Branch: {(plan.get('identity') or {}).get('branch') if isinstance(plan.get('identity'), Mapping) else ''}",
            f"- HEAD: {(plan.get('identity') or {}).get('head') if isinstance(plan.get('identity'), Mapping) else ''}",
            "",
            "## Public Scope",
            "",
            f"- Read-only: {str(summary.get('public_read_only')).lower()}",
            f"- Public mutation: {str(summary.get('public_mutation_enabled')).lower()}",
            f"- Workbench exposure: {str(summary.get('public_workbench_exposed')).lower()}",
            f"- Live metadata: {str(summary.get('live_metadata_enabled')).lower()}",
            f"- Downloads/uploads: {str(summary.get('downloads_enabled')).lower()} / {str(summary.get('uploads_enabled')).lower()}",
            f"- Public exposure enabled: {str(summary.get('public_exposure_enabled')).lower()}",
            "",
            "## Ops Posture",
            "",
            f"- Auth/no-auth: {summary.get('auth_posture')}",
            f"- Rate limits: {summary.get('rate_limit_posture')}",
            f"- Logging: {summary.get('logging_posture')}",
            f"- Monitoring: {summary.get('monitoring_posture')}",
            f"- Rollback: {summary.get('rollback_posture')}",
            f"- Report/takedown: {summary.get('report_takedown_posture')}",
            "",
            "## Validation Errors",
            "",
            *errors,
            "",
            "## Ops Blockers",
            "",
            *ops_blockers,
            "",
            "## Launch Blockers",
            "",
            *launch_blockers,
            "",
            f"Next recommended task: `{validation.get('next_recommended_task')}`",
            "",
            "This artifact does not expose the service publicly, start a tunnel or proxy, enable downloads, expose Workbench, run live metadata fanout, approve launch, or claim production readiness.",
            "",
        ]
    )


def load_json(path: str | Path) -> dict[str, Any]:
    return _read_json(Path(path))


def compatibility_fields(plan: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    return _compatibility_fields(_load_payload(plan))


def _refresh_status_fields(plan: dict[str, Any]) -> None:
    validation = validate_ops_posture(plan)
    plan["ops_blockers"] = validation["ops_blockers"]
    plan["launch_blockers"] = validation["launch_blockers"]
    plan["blockers"] = validation["blockers"]
    plan["status"] = validation["plan_status"]
    plan["next_recommended_task"] = validation["next_recommended_task"]
    plan["compatibility"] = _compatibility_fields(plan)


def _auth_posture(selected: str) -> dict[str, Any]:
    return {
        "selected": selected,
        "public_no_auth_approved": selected == "public_no_auth",
        "auth_required": selected == "public_auth_required",
        "workbench_auth_required": True,
        "operator_routes_publicly_blocked": True,
        "launch_approval_required": True,
        "launch_approval_present": False,
        "notes": "Read-only no-auth can be selected for public alpha ops; launch approval is still separate and missing.",
    }


def _compatibility_fields(plan: Mapping[str, Any]) -> dict[str, Any]:
    auth = plan.get("auth_posture") if isinstance(plan.get("auth_posture"), Mapping) else {}
    selected = str(auth.get("selected") or "operator_decision_required")
    if selected == "public_no_auth":
        production_auth = "readonly_noauth_approved"
        approval_status = "present"
    elif selected == "public_auth_required":
        production_auth = "auth_required"
        approval_status = "present"
    else:
        production_auth = "missing"
        approval_status = "not_provided"
    return {
        "production_auth_or_noauth_posture": production_auth,
        "operator_approval_file_status": approval_status,
        "rate_limit_posture": _compat_status(plan, "rate_limit_posture"),
        "logging_posture": _compat_status(plan, "logging_posture"),
        "monitoring_posture": _compat_status(plan, "monitoring_posture"),
        "restart_posture": _rollback_field_status(plan, "restart_posture"),
        "rollback_posture": _compat_status(plan, "rollback_posture"),
        "firewall_posture": _rollback_field_status(plan, "firewall_posture"),
        "router_or_tunnel_posture": _rollback_field_status(plan, "router_or_tunnel_posture"),
        "privacy_posture": _rollback_field_status(plan, "privacy_posture"),
        "takedown_or_report_issue_posture": _compat_status(plan, "incident_posture"),
        "public_workbench_exposed": bool(plan.get("public_workbench_exposed") is True),
        "public_mutation_enabled": bool(plan.get("public_mutation_enabled") is True),
        "live_metadata_enabled": bool(plan.get("live_metadata_enabled") is True),
        "public_live_fanout": not bool((plan.get("safety_posture") or {}).get("no_live_fanout") is True) if isinstance(plan.get("safety_posture"), Mapping) else False,
        "downloads_enabled": bool(plan.get("downloads_enabled") is True),
        "install_emulation_enabled": False,
    }


def _safety_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PLAN_SCHEMA_VERSION}")
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if payload.get("public_alpha_mode") is not True:
        errors.append("public_alpha_mode must be true")
    if payload.get("public_read_only") is not True:
        errors.append("public_read_only must be true")
    for key in SAFE_FALSE_FIELDS:
        if payload.get(key) is not False:
            errors.append(f"{key} must be false")
    if payload.get("launch_approval_present") is not False and payload.get("status") != "READY":
        errors.append("launch_approval_present must not be true before final approval")
    network = payload.get("network_posture") if isinstance(payload.get("network_posture"), Mapping) else {}
    if network.get("exposure_mode") not in EXPOSURE_MODES:
        errors.append("network_posture.exposure_mode is not recognized")
    if payload.get("public_exposure_enabled") is True:
        public_url = str(network.get("public_url") or "")
        tls_status = str(network.get("tls_domain_status") or "missing")
        if not public_url:
            errors.append("public exposure is enabled without public_url")
        if tls_status not in {"configured", "validated"}:
            errors.append("public exposure is enabled without TLS/domain or approved tunnel URL")
    if payload.get("status") == "READY" and payload.get("launch_approval_present") is not True:
        errors.append("launch approval is absent while status claims READY")
    errors.extend(_route_safety_errors(payload))
    errors.extend(_secret_errors(payload))
    return _dedupe(errors)


def _ops_blockers(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    auth = payload.get("auth_posture") if isinstance(payload.get("auth_posture"), Mapping) else {}
    if auth.get("selected") not in {"public_no_auth", "public_auth_required"}:
        blockers.append(_blocker("ops_blockers", "auth_or_noauth_posture_missing", "public read-only no-auth or auth-required posture is not selected"))
    if not bool(auth.get("workbench_auth_required")) or not bool(auth.get("operator_routes_publicly_blocked")):
        blockers.append(_blocker("ops_blockers", "operator_route_auth_posture_missing", "operator route auth/blocking posture is incomplete"))
    rollback = payload.get("rollback_posture") if isinstance(payload.get("rollback_posture"), Mapping) else {}
    required_rollback = ("stop_server_command", "stop_tunnel_command", "disable_public_url_step", "restore_loopback_only_step", "rollback_owner")
    if any(not _meaningful(rollback.get(key)) for key in required_rollback):
        blockers.append(_blocker("ops_blockers", "rollback_posture_missing", "rollback posture is missing required disable/restore steps"))
    incident = payload.get("incident_posture") if isinstance(payload.get("incident_posture"), Mapping) else {}
    if not _meaningful(incident.get("report_issue_channel")):
        blockers.append(_blocker("ops_blockers", "report_issue_channel_missing", "report issue channel is missing"))
    if not _meaningful(incident.get("takedown_channel")):
        blockers.append(_blocker("ops_blockers", "takedown_channel_missing", "takedown channel is missing"))
    if _compat_status(payload, "rate_limit_posture") not in {"configured", "validated"}:
        blockers.append(_blocker("ops_blockers", "rate_limit_posture_missing", "rate-limit posture is incomplete"))
    if _compat_status(payload, "logging_posture") not in {"configured", "validated"}:
        blockers.append(_blocker("ops_blockers", "logging_posture_missing", "logging/privacy redaction posture is incomplete"))
    if _compat_status(payload, "monitoring_posture") not in {"configured", "validated"}:
        blockers.append(_blocker("ops_blockers", "monitoring_posture_missing", "monitoring posture is incomplete"))
    if _compat_status(payload, "rollback_posture") not in {"configured", "validated"}:
        blockers.append(_blocker("ops_blockers", "rollback_posture_missing", "rollback posture is incomplete"))
    if _compat_status(payload, "incident_posture") not in {"configured", "validated"}:
        blockers.append(_blocker("ops_blockers", "report_takedown_posture_missing", "report/takedown posture is incomplete"))
    if _route_safety_errors(payload):
        blockers.append(_blocker("ops_blockers", "route_safety_posture_missing", "route safety posture is incomplete"))
    return _dedupe_blockers(blockers)


def _launch_blockers(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    network = payload.get("network_posture") if isinstance(payload.get("network_posture"), Mapping) else {}
    release_inputs = payload.get("release_gate_inputs") if isinstance(payload.get("release_gate_inputs"), Mapping) else {}
    blockers: list[dict[str, str]] = []
    if payload.get("public_exposure_enabled") is not True:
        blockers.append(_blocker("launch_blockers", "public_exposure_not_configured", "public exposure remains disabled"))
    if not _meaningful(network.get("public_url")):
        blockers.append(_blocker("launch_blockers", "public_url_missing", "public URL is not selected"))
    if network.get("tls_domain_status") not in {"configured", "validated"}:
        blockers.append(_blocker("launch_blockers", "tls_or_tunnel_https_not_validated", "TLS/domain or provider HTTPS is not validated"))
    if not _artifact_present(release_inputs.get("expected_full_discovery_report")):
        blockers.append(_blocker("launch_blockers", "full_discovery_report_missing", "full discovery report is missing"))
    if not _artifact_present(release_inputs.get("expected_release_promotion_report")):
        blockers.append(_blocker("launch_blockers", "release_promotion_report_missing", "release promotion report is missing"))
    if not _artifact_present(release_inputs.get("expected_launch_approval")) or payload.get("launch_approval_present") is not True:
        blockers.append(_blocker("launch_blockers", "public_launch_approval_missing", "manual public launch approval is missing"))
    return blockers


def _status_for(
    errors: Sequence[str],
    ops_blockers: Sequence[Mapping[str, str]],
    launch_blockers: Sequence[Mapping[str, str]],
    payload: Mapping[str, Any],
) -> str:
    if errors or ops_blockers:
        return "BLOCKED"
    ids = {str(item.get("id") or "") for item in launch_blockers}
    if "public_exposure_not_configured" in ids or "public_url_missing" in ids or "tls_or_tunnel_https_not_validated" in ids:
        return "READY_FOR_EXPOSURE_PLAN"
    if "full_discovery_report_missing" in ids or "release_promotion_report_missing" in ids:
        return "READY_FOR_RELEASE_CHECK"
    if "public_launch_approval_missing" in ids:
        return "READY_FOR_APPROVAL"
    if payload.get("launch_approval_present") is True and not launch_blockers:
        return "READY"
    return "BLOCKED"


def _next_task(status: str, ops_blockers: Sequence[Mapping[str, str]], launch_blockers: Sequence[Mapping[str, str]]) -> str:
    if status == "BLOCKED" and ops_blockers:
        return "PUBLIC-ALPHA-OPS-POSTURE-00"
    ids = {str(item.get("id") or "") for item in launch_blockers}
    if "public_exposure_not_configured" in ids or "public_url_missing" in ids or "tls_or_tunnel_https_not_validated" in ids:
        return "LOCAL-MACHINE-PUBLIC-TUNNEL-PLAN-00"
    if "full_discovery_report_missing" in ids or "release_promotion_report_missing" in ids:
        return "PUBLIC-ALPHA-FULL-DISCOVERY-RELEASE-CHECK-00"
    if "public_launch_approval_missing" in ids:
        return "PUBLIC-ALPHA-LAUNCH-APPROVAL-00"
    return "PUBLIC-ALPHA-LAUNCH-00"


def _route_safety_errors(payload: Mapping[str, Any]) -> list[str]:
    scope = payload.get("public_scope") if isinstance(payload.get("public_scope"), Mapping) else {}
    safety = payload.get("safety_posture") if isinstance(payload.get("safety_posture"), Mapping) else {}
    errors: list[str] = []
    if scope.get("read_only") is not True:
        errors.append("public_scope.read_only must be true")
    forbidden_routes = {str(item) for item in scope.get("forbidden_routes") or []}
    for route in ("/workbench", "/download", "/upload", "/mutate"):
        if route not in forbidden_routes:
            errors.append(f"forbidden route missing: {route}")
    for key in ("no_mutation", "no_workbench", "no_live_fanout", "no_downloads", "no_uploads", "no_ai_truth", "no_provider_truth"):
        if safety.get(key) is not True:
            errors.append(f"safety_posture.{key} must be true")
    return errors


def _compat_status(payload: Mapping[str, Any], key: str) -> str:
    section = payload.get(key)
    if isinstance(section, Mapping):
        status = str(section.get("compat_status") or "missing")
        return status if status in OPS_COMPAT_STATUSES else "missing"
    return "missing"


def _rollback_field_status(payload: Mapping[str, Any], key: str) -> str:
    rollback = payload.get("rollback_posture") if isinstance(payload.get("rollback_posture"), Mapping) else {}
    if _meaningful(rollback.get(key)):
        return "configured"
    return "missing"


def _tls_domain_status(public_url: str) -> str:
    if public_url.startswith("https://"):
        return "configured"
    if public_url:
        return "planned"
    return "missing"


def _blocker(category: str, blocker_id: str, message: str) -> dict[str, str]:
    return {"category": category, "id": blocker_id, "status": "blocked", "message": message}


def _blocker_lines(blockers: Sequence[Mapping[str, str]]) -> list[str]:
    return [f"- [{item.get('category')}] {item.get('id')}: {item.get('message')}" for item in blockers] or ["- none"]


def _artifact_present(value: Any) -> bool:
    path = str(value or "")
    if not path or "<" in path or ">" in path:
        return False
    return Path(path).is_file()


def _meaningful(value: Any) -> bool:
    text = str(value or "").strip()
    lowered = text.casefold()
    if not text:
        return False
    return not any(marker in lowered for marker in ("missing", "unresolved", "todo", "tbd"))


def _load_payload(value: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return _read_json(Path(value))


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _file_sha256(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""


def _git_stdout(*command: str) -> str:
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _secret_errors(value: Any) -> list[str]:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=True)
    lowered = text.casefold()
    return [f"payload contains forbidden secret marker: {marker}" for marker in SECRET_MARKERS if marker.casefold() in lowered]


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _dedupe_blockers(blockers: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for blocker in blockers:
        blocker_id = str(blocker.get("id") or "")
        if blocker_id not in seen:
            seen.add(blocker_id)
            result.append(dict(blocker))
    return result

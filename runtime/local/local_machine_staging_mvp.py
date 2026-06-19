"""Local-machine staging helpers for the public-alpha bundle.

This module is deliberately separate from external SSH staging. It proves that
the current computer can host the read-only public-alpha staging bundle on a
loopback address without treating that proof as public deployment.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.local.corpus_gate_closeout import DEFAULT_GATE_TARGET
from runtime.local.staging_package import MANIFEST_FILE, bundle_status, validate_bundle
from scripts.eureka_public_alpha_rehearsal import run_rehearsal


TASK_ID = "LOCAL-MACHINE-STAGING-PROVISION-00"
PLAN_SCHEMA_VERSION = "eureka.local_machine_staging_plan.v0"
REPORT_SCHEMA_VERSION = "eureka.local_machine_staging_report.v0"
DEFAULT_OUT = ".eureka/local-machine-staging/public-alpha/latest"
PLAN_JSON = "local_machine_staging_plan.json"
REPORT_JSON = "local_machine_staging_report.json"
REPORT_MD = "LOCAL_MACHINE_STAGING_REPORT.md"
DEFAULT_QUERY = "manual for Sound Blaster CT1740"
SAFE_ZERO_FIELDS = (
    "binary_verified_count",
    "download_safe_count",
    "execution_safe_count",
    "rights_cleared_count",
)
SECRET_MARKERS = (
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY",
    "BEGIN PRIVATE KEY",
    "PRIVATE KEY",
    "sk-",
    "authorization:",
    "bearer ",
)


def build_plan(bundle: str | Path, *, out_dir: str | Path, host: str = "127.0.0.1", port: int = 8765) -> dict[str, Any]:
    bundle_path = Path(bundle)
    status = bundle_status(bundle_path)
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "plan_schema_version": PLAN_SCHEMA_VERSION,
        "staging_bundle_path": str(bundle_path),
        "staging_bundle_id": str(status.get("bundle_id") or ""),
        "bundle_manifest_digest": _file_sha256(bundle_path / MANIFEST_FILE),
        "out_dir": str(out_dir),
        "host": str(host),
        "port": int(port),
        "bind_host": str(host),
        "public_exposure": not _is_loopback_host(str(host)),
        "public_alpha_mode": bool(status.get("public_alpha_mode") is True),
        "read_only": bool(status.get("read_only") is True),
        "live_metadata_enabled": bool(status.get("live_metadata_enabled") is True),
        "public_live_fanout": bool(status.get("public_live_fanout") is True),
        "workbench_exposed": bool(status.get("workbench_exposed") is True),
        "mutation_enabled": bool(status.get("mutation_enabled") is True),
        "downloads_enabled": bool(status.get("downloads_enabled") is True),
        "corpus_gate_status": str(status.get("corpus_gate_status") or "unknown"),
        "reviewed_artifact_gate_count": int(status.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(status.get("artifact_verified_count") or 0),
        "public_artifact_identity_record_count": int(status.get("public_artifact_identity_record_count") or 0),
        "binary_verified_count": int(status.get("binary_verified_count") or 0),
        "download_safe_count": int(status.get("download_safe_count") or 0),
        "execution_safe_count": int(status.get("execution_safe_count") or 0),
        "rights_cleared_count": int(status.get("rights_cleared_count") or 0),
        "validation_errors": validate_bundle(bundle_path),
        "generated_at": "not_recorded_deterministic_local_machine_staging_plan",
    }


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
    required = (
        "task_id",
        "staging_bundle_path",
        "staging_bundle_id",
        "bundle_manifest_digest",
        "host",
        "port",
        "bind_host",
        "public_exposure",
        "public_alpha_mode",
        "read_only",
        "live_metadata_enabled",
        "public_live_fanout",
        "workbench_exposed",
        "mutation_enabled",
        "downloads_enabled",
        "corpus_gate_status",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
    )
    errors = [f"missing required field: {key}" for key in required if key not in payload]
    if errors:
        return errors
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if not _is_loopback_host(str(payload.get("host") or "")):
        errors.append("host must be loopback for local-machine staging")
    if not _is_loopback_host(str(payload.get("bind_host") or "")):
        errors.append("bind_host must be loopback for local-machine staging")
    if payload.get("public_exposure") is not False:
        errors.append("public_exposure must be false")
    errors.extend(_safe_posture_errors(payload))
    if payload.get("corpus_gate_status") != "pass":
        errors.append("corpus_gate_status must be pass")
    if int(payload.get("reviewed_artifact_gate_count") or 0) < DEFAULT_GATE_TARGET:
        errors.append(f"reviewed_artifact_gate_count must be at least {DEFAULT_GATE_TARGET}")
    if int(payload.get("artifact_verified_count") or 0) < DEFAULT_GATE_TARGET:
        errors.append(f"artifact_verified_count must be at least {DEFAULT_GATE_TARGET}")
    for error in payload.get("validation_errors") or []:
        errors.append(f"bundle validation: {error}")
    errors.extend(_secret_errors(payload))
    return _dedupe(errors)


def smoke_local_machine(
    bundle: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    out_dir: str | Path,
    query: str = DEFAULT_QUERY,
) -> dict[str, Any]:
    bundle_path = Path(bundle)
    staging = bundle_status(bundle_path)
    local_failures: list[str] = []
    if not _is_loopback_host(host):
        local_failures.append("local-machine staging host must be loopback")
    if staging.get("status") != "pass":
        local_failures.extend(f"bundle validation: {error}" for error in validate_bundle(bundle_path))

    rehearsal: dict[str, Any] = {}
    if not local_failures:
        rehearsal = run_rehearsal(bundle_path, host=host, port=port, out=out_dir, query=query)
        local_failures.extend(str(item) for item in rehearsal.get("local_rehearsal_failures") or [])

    safety_checks = _safety_checks(rehearsal, staging)
    for check in safety_checks:
        if check.get("passed") is not True:
            local_failures.append(f"safety check failed: {check.get('name')}")
    mutation_checks = _mutation_checks(rehearsal)
    if mutation_checks.get("any_mutated") is True:
        local_failures.append("local-machine smoke mutated protected artifacts")

    warnings: list[str] = []
    if not local_failures:
        warnings.append("local-machine staging passed on loopback; external/public hosting remains unresolved")

    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": "FAIL" if local_failures else "PASS_WITH_WARNINGS",
        "local_machine_staging_status": "fail" if local_failures else "pass",
        "host": str(host),
        "port": int(rehearsal.get("server_port") or port),
        "bind_host": str(host),
        "public_exposure": False,
        "staging_bundle_path": str(bundle_path),
        "staging_bundle_id": str(staging.get("bundle_id") or ""),
        "bundle_manifest_digest": _file_sha256(bundle_path / MANIFEST_FILE),
        "corpus_gate_status": str(staging.get("corpus_gate_status") or "unknown"),
        "reviewed_artifact_gate_count": int(staging.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(staging.get("artifact_verified_count") or 0),
        "public_artifact_identity_record_count": int(staging.get("public_artifact_identity_record_count") or 0),
        "binary_verified_count": int(staging.get("binary_verified_count") or 0),
        "download_safe_count": int(staging.get("download_safe_count") or 0),
        "execution_safe_count": int(staging.get("execution_safe_count") or 0),
        "rights_cleared_count": int(staging.get("rights_cleared_count") or 0),
        "read_only": bool(rehearsal.get("read_only") is True if rehearsal else staging.get("read_only") is True),
        "public_alpha_mode": bool(rehearsal.get("public_alpha_mode") is True if rehearsal else staging.get("public_alpha_mode") is True),
        "live_metadata_enabled": bool(rehearsal.get("live_metadata_enabled") is True),
        "public_live_fanout": bool(rehearsal.get("public_live_fanout") is True),
        "workbench_exposed": bool(rehearsal.get("workbench_exposed") is True),
        "mutation_enabled": bool(rehearsal.get("mutation_enabled") is True),
        "downloads_enabled": bool(rehearsal.get("downloads_enabled") is True),
        "route_probe_results": _redact_routes(rehearsal.get("routes_probed") or []),
        "blocked_route_probe_results": _redact_routes(rehearsal.get("blocked_routes_probed") or []),
        "safety_checks": safety_checks,
        "mutation_checks": mutation_checks,
        "rehearsal_report_status": str(rehearsal.get("status") or "not_run"),
        "rehearsal_launch_blockers": list(rehearsal.get("launch_blockers") or []),
        "warnings": _dedupe(warnings),
        "blockers": _dedupe(local_failures),
        "next_recommended_task": "LOCAL-MACHINE-PUBLIC-EXPOSURE-PLAN-00" if not local_failures else "LOCAL-MACHINE-STAGING-PROVISION-00-FIX",
        "generated_at": "not_recorded_deterministic_local_machine_staging",
        "truth_promotion_performed": False,
        "verified_artifact_truth_created": False,
    }
    write_report(report, out_dir)
    return report


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
        "local_machine_staging_status",
        "host",
        "port",
        "public_exposure",
        "staging_bundle_id",
        "bundle_manifest_digest",
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
        "route_probe_results",
        "blocked_route_probe_results",
        "safety_checks",
        "mutation_checks",
        "warnings",
        "blockers",
        "next_recommended_task",
    )
    errors = [f"missing required field: {key}" for key in required if key not in payload]
    if errors:
        return errors
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if payload.get("status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if payload.get("local_machine_staging_status") not in {"pass", "fail"}:
        errors.append("local_machine_staging_status must be pass or fail")
    if not _is_loopback_host(str(payload.get("host") or "")):
        errors.append("host must be loopback")
    if payload.get("public_exposure") is not False:
        errors.append("public_exposure must be false")
    errors.extend(_safe_posture_errors(payload))
    if payload.get("corpus_gate_status") != "pass":
        errors.append("corpus_gate_status must be pass")
    if int(payload.get("reviewed_artifact_gate_count") or 0) < DEFAULT_GATE_TARGET:
        errors.append(f"reviewed_artifact_gate_count must be at least {DEFAULT_GATE_TARGET}")
    if int(payload.get("artifact_verified_count") or 0) < DEFAULT_GATE_TARGET:
        errors.append(f"artifact_verified_count must be at least {DEFAULT_GATE_TARGET}")
    for key in SAFE_ZERO_FIELDS:
        if int(payload.get(key) or 0) != 0:
            errors.append(f"{key} must remain 0")
    routes = payload.get("route_probe_results")
    blocked = payload.get("blocked_route_probe_results")
    if not isinstance(routes, list) or not routes:
        errors.append("route_probe_results must be a non-empty list")
    if not isinstance(blocked, list) or not blocked:
        errors.append("blocked_route_probe_results must be a non-empty list")
    for route in routes if isinstance(routes, list) else []:
        if not isinstance(route, Mapping):
            errors.append("route_probe_results entries must be objects")
            continue
        path = str(route.get("path") or "")
        code = int(route.get("status_code") or 0)
        if path.startswith("/workbench"):
            errors.append("route_probe_results must not include Workbench routes")
        elif path not in {"/record/__missing__", "/record/..%2F..%2Fprivate"} and code != 200:
            errors.append(f"public route {path} returned {code}")
    for route in blocked if isinstance(blocked, list) else []:
        if not isinstance(route, Mapping):
            errors.append("blocked_route_probe_results entries must be objects")
            continue
        if int(route.get("status_code") or 0) not in {403, 404}:
            errors.append(f"blocked route {route.get('path')} returned {route.get('status_code')}")
    checks = payload.get("safety_checks")
    if not isinstance(checks, list) or not checks:
        errors.append("safety_checks must be a non-empty list")
    else:
        for check in checks:
            if isinstance(check, Mapping) and check.get("passed") is not True:
                errors.append(f"safety check failed: {check.get('name')}")
    mutation = payload.get("mutation_checks") if isinstance(payload.get("mutation_checks"), Mapping) else {}
    if mutation.get("any_mutated") is not False:
        errors.append("mutation_checks.any_mutated must be false")
    if not payload.get("warnings") and payload.get("status") == "PASS_WITH_WARNINGS":
        errors.append("PASS_WITH_WARNINGS requires warnings")
    errors.extend(_secret_errors(payload))
    return _dedupe(errors)


def render_status(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"status: {report.get('status')}",
            f"local_machine_staging_status: {report.get('local_machine_staging_status')}",
            f"host: {report.get('host')}",
            f"port: {report.get('port')}",
            f"public_exposure: {str(report.get('public_exposure')).lower()}",
            f"staging_bundle_id: {report.get('staging_bundle_id')}",
            f"corpus_gate_status: {report.get('corpus_gate_status')}",
            f"reviewed_artifact_gate_count: {report.get('reviewed_artifact_gate_count')}",
            f"artifact_verified_count: {report.get('artifact_verified_count')}",
            f"read_only: {str(report.get('read_only')).lower()}",
            f"public_alpha_mode: {str(report.get('public_alpha_mode')).lower()}",
            f"live_metadata_enabled: {str(report.get('live_metadata_enabled')).lower()}",
            f"workbench_exposed: {str(report.get('workbench_exposed')).lower()}",
            f"mutation_enabled: {str(report.get('mutation_enabled')).lower()}",
            f"downloads_enabled: {str(report.get('downloads_enabled')).lower()}",
            f"route_probes: {len(report.get('route_probe_results') or [])}",
            f"blocked_route_probes: {len(report.get('blocked_route_probe_results') or [])}",
            f"blockers: {len(report.get('blockers') or [])}",
            f"next_recommended_task: {report.get('next_recommended_task')}",
        ]
    ) + "\n"


def render_markdown_report(report: Mapping[str, Any]) -> str:
    routes = report.get("route_probe_results") or []
    blocked = report.get("blocked_route_probe_results") or []
    warnings = [f"- {item}" for item in report.get("warnings") or []] or ["- none"]
    blockers = [f"- {item}" for item in report.get("blockers") or []] or ["- none"]
    return "\n".join(
        [
            "# Local-Machine Staging Report",
            "",
            f"- Status: {report.get('status')}",
            f"- Local-machine staging: {report.get('local_machine_staging_status')}",
            f"- Host: {report.get('host')}",
            f"- Port: {report.get('port')}",
            f"- Public exposure: {str(report.get('public_exposure')).lower()}",
            f"- Bundle ID: {report.get('staging_bundle_id')}",
            f"- Corpus gate: {report.get('corpus_gate_status')}",
            f"- Reviewed artifact gate count: {report.get('reviewed_artifact_gate_count')}",
            f"- Artifact verified count: {report.get('artifact_verified_count')}",
            f"- Public routes probed: {len(routes)}",
            f"- Blocked Workbench routes probed: {len(blocked)}",
            f"- Read only: {str(report.get('read_only')).lower()}",
            f"- Workbench exposed: {str(report.get('workbench_exposed')).lower()}",
            f"- Live metadata enabled: {str(report.get('live_metadata_enabled')).lower()}",
            f"- Public live fanout: {str(report.get('public_live_fanout')).lower()}",
            f"- Mutation enabled: {str(report.get('mutation_enabled')).lower()}",
            f"- Downloads enabled: {str(report.get('downloads_enabled')).lower()}",
            "",
            "## Warnings",
            "",
            *warnings,
            "",
            "## Blockers",
            "",
            *blockers,
            "",
            "This local-machine staging report proves loopback hosting on the current computer only. It is not external staging, production hosting, TLS/domain setup, release promotion, full discovery, public exposure, or launch approval.",
            "",
        ]
    )


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _safe_posture_errors(payload: Mapping[str, Any]) -> list[str]:
    expectations = {
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "workbench_exposed": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
    }
    return [f"{key} must be {str(expected).lower()}" for key, expected in expectations.items() if payload.get(key) is not expected]


def _safety_checks(rehearsal: Mapping[str, Any], staging: Mapping[str, Any]) -> list[dict[str, Any]]:
    bool_expectations = {
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "workbench_exposed": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
    }
    checks = []
    for key, expected in bool_expectations.items():
        actual = rehearsal.get(key) if key in rehearsal else staging.get(key)
        checks.append({"name": key, "expected": expected, "actual": actual, "passed": actual is expected})
    checks.append(
        {
            "name": "corpus_gate_pass",
            "expected": "pass",
            "actual": staging.get("corpus_gate_status"),
            "passed": staging.get("corpus_gate_status") == "pass",
        }
    )
    checks.append(
        {
            "name": "artifact_verified_gate_count",
            "expected": DEFAULT_GATE_TARGET,
            "actual": int(staging.get("artifact_verified_count") or 0),
            "passed": int(staging.get("artifact_verified_count") or 0) >= DEFAULT_GATE_TARGET,
        }
    )
    for key in SAFE_ZERO_FIELDS:
        checks.append({"name": key, "expected": 0, "actual": int(staging.get(key) or 0), "passed": int(staging.get(key) or 0) == 0})
    leakage = rehearsal.get("leakage_checks") if isinstance(rehearsal.get("leakage_checks"), Mapping) else {}
    checks.append({"name": "public_response_leakage", "expected": True, "actual": leakage.get("passed"), "passed": leakage.get("passed") is True})
    for check in rehearsal.get("safety_conflict_checks") or []:
        if isinstance(check, Mapping):
            checks.append({"name": f"safety_conflict_{check.get('name')}", "expected": True, "actual": check.get("passed"), "passed": check.get("passed") is True})
    return checks


def _mutation_checks(rehearsal: Mapping[str, Any]) -> dict[str, Any]:
    mutation = rehearsal.get("mutation_checks") if isinstance(rehearsal.get("mutation_checks"), Mapping) else {}
    per_artifact = mutation.get("per_artifact") if isinstance(mutation.get("per_artifact"), Mapping) else {}
    any_mutated = any(isinstance(item, Mapping) and item.get("mutated") is True for item in per_artifact.values())
    return {
        "any_mutated": bool(any_mutated),
        "public_routes_mutated_bundle": bool(mutation.get("public_routes_mutated_bundle") is True),
        "blocked_workbench_mutated_anything": bool(mutation.get("blocked_workbench_mutated_anything") is True),
        "search_mutated_anything": bool(mutation.get("search_mutated_anything") is True),
        "per_artifact": per_artifact,
    }


def _redact_routes(routes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    redacted = []
    for route in routes:
        path = str(route.get("path") or "")
        item = {
            "method": str(route.get("method") or "GET"),
            "path": path,
            "status_code": int(route.get("status_code") or 0),
            "content_type": str(route.get("content_type") or ""),
            "sample": _redact_text(str(route.get("sample") or ""))[:220],
            "body_sha256": str(route.get("body_sha256") or _sha256_text(str(route.get("body") or ""))),
        }
        redacted.append(item)
    return redacted


def _redact_text(value: str) -> str:
    result = value
    for marker in SECRET_MARKERS:
        result = result.replace(marker, "[redacted]")
    return result.replace("\\", "/")


def _load_payload(value: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return load_json(value)


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _file_sha256(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _secret_errors(value: Any) -> list[str]:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True) if not isinstance(value, str) else value
    lowered = text.casefold()
    return [f"payload contains forbidden secret marker: {marker}" for marker in SECRET_MARKERS if marker.casefold() in lowered]


def _is_loopback_host(host: str) -> bool:
    normalized = str(host or "").strip().casefold()
    return normalized in {"localhost", "::1"} or normalized.startswith("127.")


def _dedupe(values: Sequence[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

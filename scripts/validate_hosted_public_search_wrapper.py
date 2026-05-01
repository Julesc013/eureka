#!/usr/bin/env python3
"""Validate P54 Hosted Public Search Wrapper v0 without network access."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "hosted-public-search-wrapper-v0"
REPORT_PATH = AUDIT_ROOT / "hosted_public_search_wrapper_report.json"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "WRAPPER_SUMMARY.md",
    "HOSTED_MODE_REQUIREMENTS.md",
    "ROUTE_IMPLEMENTATION_STATUS.md",
    "ENVIRONMENT_VARIABLES.md",
    "SAFETY_DEFAULTS.md",
    "HEALTH_AND_STATUS_ENDPOINTS.md",
    "DEPLOYMENT_TEMPLATE_REVIEW.md",
    "LOCAL_REHEARSAL_RESULTS.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "OPERATOR_DEPLOYMENT_STEPS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "hosted_public_search_wrapper_report.json",
}

REQUIRED_REPORT_KEYS = {
    "report_id",
    "created_by_slice",
    "repo_head",
    "branch",
    "worktree_status",
    "wrapper_script",
    "check_script",
    "route_status",
    "env_defaults",
    "safety_defaults",
    "deployment_templates",
    "hosted_wrapper_implemented",
    "hosted_backend_implemented",
    "hosted_backend_deployed",
    "hosted_deployment_verified",
    "dynamic_backend_deployed",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "external_calls_enabled",
    "ai_runtime_enabled",
    "public_search_mode",
    "command_results",
    "local_rehearsal_results",
    "remaining_blockers",
    "operator_steps",
    "next_recommended_branch",
    "notes",
}

REQUIRED_ROUTES = {
    "/healthz",
    "/status",
    "/search",
    "/api/v1/status",
    "/api/v1/search",
    "/api/v1/query-plan",
    "/api/v1/sources",
    "/api/v1/source/{source_id}",
}

HARD_FALSE_KEYS = {
    "hosted_backend_deployed",
    "hosted_deployment_verified",
    "dynamic_backend_deployed",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "external_calls_enabled",
    "ai_runtime_enabled",
}

REQUIRED_DOCS = {
    "docs/operations/HOSTED_PUBLIC_SEARCH.md",
    "docs/operations/PUBLIC_SEARCH_HOSTING.md",
    "docs/operations/PUBLIC_SEARCH_ENVIRONMENT.md",
    "docs/operations/PUBLIC_SEARCH_ROLLBACK.md",
}

FORBIDDEN_CLAIMS = (
    "hosted backend is live",
    "hosted public search is live",
    "deployment success claimed",
    "deployment verified: true",
    "live_probes_enabled: true",
    "downloads_enabled: true",
    "uploads_enabled: true",
    "accounts_enabled: true",
    "telemetry_enabled: true",
    "production-ready",
    "production ready",
)


def validate_hosted_public_search_wrapper() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _validate_audit_pack(errors)
    report = _load_json(REPORT_PATH, errors)
    _validate_report(report, errors)
    _validate_scripts(errors)
    _validate_check_config(errors)
    _validate_templates(errors, warnings)
    _validate_docs(errors)
    _validate_inventories(errors)
    _validate_claims(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "hosted_public_search_wrapper_validator_v0",
        "report_id": _mapping(report).get("report_id"),
        "hosted_wrapper_implemented": _mapping(report).get("hosted_wrapper_implemented"),
        "hosted_backend_deployed": _mapping(report).get("hosted_backend_deployed"),
        "hosted_deployment_verified": _mapping(report).get("hosted_deployment_verified"),
        "public_search_mode": _mapping(report).get("public_search_mode"),
        "required_routes": sorted(REQUIRED_ROUTES),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_audit_pack(errors: list[str]) -> None:
    if not AUDIT_ROOT.is_dir():
        errors.append("P54 audit pack is missing.")
        return
    present = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - present)
    if missing:
        errors.append(f"P54 audit pack missing required files: {missing}.")


def _validate_report(report: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        errors.append("hosted_public_search_wrapper_report.json must be an object.")
        return
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append(f"P54 report missing required keys: {missing}.")
    if report.get("report_id") != "hosted_public_search_wrapper_v0":
        errors.append("report_id must be hosted_public_search_wrapper_v0.")
    if report.get("hosted_wrapper_implemented") is not True:
        errors.append("hosted_wrapper_implemented must be true.")
    if report.get("public_search_mode") != "local_index_only":
        errors.append("public_search_mode must be local_index_only.")
    for key in HARD_FALSE_KEYS:
        if report.get(key) is not False:
            errors.append(f"{key} must be false.")
    route_status = _mapping(report.get("route_status"))
    missing_routes = sorted(REQUIRED_ROUTES - set(route_status))
    if missing_routes:
        errors.append(f"route_status missing required routes: {missing_routes}.")
    if not isinstance(report.get("command_results"), list) or not report["command_results"]:
        errors.append("command_results must be a non-empty list.")
    rehearsal = _mapping(report.get("local_rehearsal_results"))
    if rehearsal.get("status") != "passed" or rehearsal.get("failed_checks") not in (0, "0"):
        errors.append("local_rehearsal_results must record passed checks.")


def _validate_scripts(errors: list[str]) -> None:
    for path in (
        ROOT / "scripts" / "run_hosted_public_search.py",
        ROOT / "scripts" / "check_hosted_public_search_wrapper.py",
    ):
        if not path.is_file():
            errors.append(f"{_rel(path)} is missing.")


def _validate_check_config(errors: list[str]) -> None:
    env = os.environ.copy()
    env.update(
        {
            "EUREKA_PUBLIC_MODE": "1",
            "EUREKA_SEARCH_MODE": "local_index_only",
            "EUREKA_ALLOW_LIVE_PROBES": "0",
            "EUREKA_ALLOW_DOWNLOADS": "0",
            "EUREKA_ALLOW_UPLOADS": "0",
            "EUREKA_ALLOW_LOCAL_PATHS": "0",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH": "0",
            "EUREKA_ALLOW_INSTALL_ACTIONS": "0",
            "EUREKA_ALLOW_TELEMETRY": "0",
            "EUREKA_MAX_QUERY_LEN": "160",
            "EUREKA_MAX_RESULTS": "20",
            "EUREKA_GLOBAL_TIMEOUT_MS": "5000",
            "EUREKA_OPERATOR_KILL_SWITCH": "0",
            "EUREKA_HOSTED_DEPLOYMENT_VERIFIED": "0",
            "EUREKA_DYNAMIC_BACKEND_DEPLOYED": "0",
        }
    )
    completed = subprocess.run(
        [sys.executable, "scripts/run_hosted_public_search.py", "--check-config"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        errors.append(
            "scripts/run_hosted_public_search.py --check-config failed under safe defaults: "
            + (completed.stdout + completed.stderr).strip()
        )


def _validate_templates(errors: list[str], warnings: list[str]) -> None:
    dockerfile = ROOT / "Dockerfile"
    dockerignore = ROOT / ".dockerignore"
    render = ROOT / "deploy" / "render" / "render.yaml"
    deploy_readme = ROOT / "deploy" / "README.md"
    for path in (dockerfile, dockerignore, render, deploy_readme):
        if not path.is_file():
            warnings.append(f"{_rel(path)} is not present; deployment template coverage is reduced.")
    if dockerfile.is_file():
        text = dockerfile.read_text(encoding="utf-8")
        for phrase in (
            "EUREKA_SEARCH_MODE=local_index_only",
            "EUREKA_ALLOW_LIVE_PROBES=0",
            "EUREKA_ALLOW_DOWNLOADS=0",
            "EUREKA_ALLOW_UPLOADS=0",
            "EUREKA_ALLOW_LOCAL_PATHS=0",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH=0",
            "scripts/run_hosted_public_search.py",
        ):
            if phrase not in text:
                errors.append(f"Dockerfile missing safe setting {phrase}.")
        _scan_template_for_secrets(dockerfile, text, errors)
    if render.is_file():
        text = render.read_text(encoding="utf-8")
        for phrase in (
            "EUREKA_SEARCH_MODE",
            "local_index_only",
            "EUREKA_ALLOW_LIVE_PROBES",
            'value: "0"',
            "healthCheckPath: /healthz",
        ):
            if phrase not in text:
                errors.append(f"deploy/render/render.yaml missing {phrase}.")
        _scan_template_for_secrets(render, text, errors)


def _scan_template_for_secrets(path: Path, text: str, errors: list[str]) -> None:
    lowered = text.casefold()
    for token in ("api_key", "auth_token", "password:", "private_key", "secret:"):
        if token in lowered:
            errors.append(f"{_rel(path)} appears to include secret-like token {token!r}.")


def _validate_docs(errors: list[str]) -> None:
    for relative in REQUIRED_DOCS:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"{relative} is missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in ("local_index_only", "not", "no live probes"):
            if phrase not in text:
                errors.append(f"{relative} missing hosted wrapper safety phrase {phrase!r}.")


def _validate_inventories(errors: list[str]) -> None:
    handoff = _load_json(ROOT / "control" / "inventory" / "publication" / "live_backend_handoff.json", errors)
    routes = _load_json(ROOT / "control" / "inventory" / "publication" / "public_search_routes.json", errors)
    targets = _load_json(ROOT / "control" / "inventory" / "publication" / "deployment_targets.json", errors)
    safety = _load_json(ROOT / "control" / "inventory" / "publication" / "public_search_safety.json", errors)

    handoff_map = _mapping(handoff)
    if handoff_map.get("hosted_public_search_wrapper_status") not in {"implemented_local_prototype", "deployment_ready_local"}:
        errors.append("live_backend_handoff must record hosted_public_search_wrapper_status for P54 wrapper readiness.")
    if handoff_map.get("hosted_backend_deployed") is not False:
        errors.append("live_backend_handoff must keep hosted_backend_deployed false.")
    if handoff_map.get("hosted_deployment_verified") is not False:
        errors.append("live_backend_handoff must keep hosted_deployment_verified false.")

    routes_map = _mapping(routes)
    if routes_map.get("hosted_public_search_wrapper_status") not in {"implemented_local_prototype", "deployment_ready_local"}:
        errors.append("public_search_routes must record hosted_public_search_wrapper_status for P54 wrapper readiness.")
    if routes_map.get("hosted_public_deployment_verified") is not False:
        errors.append("public_search_routes must keep hosted_public_deployment_verified false.")

    safety_map = _mapping(safety)
    if safety_map.get("hosted_public_search_wrapper_status") not in {"implemented_local_prototype", "deployment_ready_local"}:
        errors.append("public_search_safety must record hosted_public_search_wrapper_status for P54 wrapper readiness.")
    if safety_map.get("no_hosted_public_search_live") is not True:
        errors.append("public_search_safety must keep no_hosted_public_search_live true.")

    backend_target = None
    for target in _mapping(targets).get("targets", []):
        if isinstance(target, Mapping) and target.get("id") == "public_search_backend":
            backend_target = target
            break
    if not isinstance(backend_target, Mapping):
        errors.append("deployment_targets must include public_search_backend.")
    else:
        if backend_target.get("status") not in {"wrapper_ready_not_deployed", "not_deployed"}:
            errors.append("public_search_backend target status must remain wrapper_ready_not_deployed or not_deployed.")
        if backend_target.get("deployment_success_claimed") is not False:
            errors.append("public_search_backend must keep deployment_success_claimed false.")
        if backend_target.get("hosted_deployment_verified") is not False:
            errors.append("public_search_backend must keep hosted_deployment_verified false.")
        if backend_target.get("live_probes_enabled") is not False:
            errors.append("public_search_backend must keep live_probes_enabled false.")


def _validate_claims(errors: list[str]) -> None:
    texts: list[str] = []
    for root in (
        AUDIT_ROOT,
        ROOT / "docs" / "operations",
        ROOT / "deploy",
    ):
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if path.parent == AUDIT_ROOT:
                texts.append(path.read_text(encoding="utf-8"))
            elif path.parent == ROOT / "docs" / "operations" and path.name in {
                "HOSTED_PUBLIC_SEARCH.md",
                "PUBLIC_SEARCH_HOSTING.md",
                "PUBLIC_SEARCH_ENVIRONMENT.md",
                "PUBLIC_SEARCH_ROLLBACK.md",
            }:
                texts.append(path.read_text(encoding="utf-8"))
            elif path.parent == ROOT / "deploy" and path.name == "README.md":
                texts.append(path.read_text(encoding="utf-8"))
    combined = "\n".join(texts).casefold()
    for claim in FORBIDDEN_CLAIMS:
        if claim in combined:
            errors.append(f"forbidden product/deployment claim found: {claim}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)} is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)} is invalid JSON: {exc}.")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Hosted public search wrapper validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"public_search_mode: {report.get('public_search_mode')}",
        f"hosted_wrapper_implemented: {report.get('hosted_wrapper_implemented')}",
        f"hosted_backend_deployed: {report.get('hosted_backend_deployed')}",
        f"hosted_deployment_verified: {report.get('hosted_deployment_verified')}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_hosted_public_search_wrapper()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

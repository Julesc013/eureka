#!/usr/bin/env python3
"""Run a repeatable local public-alpha rehearsal from a staging bundle."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import time
from typing import Any, Mapping, Sequence, TextIO
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.public_alpha_mvp import PublicAlphaService
from runtime.local.search_index import load_index
from runtime.local.search_mvp import LocalSearchOptions, LocalSearchService
from runtime.local.staging_mvp import (
    MANIFEST_FILE,
    PUBLIC_INDEX_FILE,
    RUNTIME_CONFIG_FILE,
    bundle_id,
    bundle_status,
    public_index_path,
    validate_bundle,
)
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for, main as run_local_main


TASK_ID = "PUBLIC-ALPHA-REHEARSAL-00"
REPORT_SCHEMA_VERSION = "eureka.public_alpha_rehearsal_report.v0"
DEFAULT_QUERY = "manual for Sound Blaster CT1740"
DEFAULT_OUT = ".eureka/rehearsals/public-alpha/latest"
PUBLIC_ROUTE_PATHS = (
    "/",
    "/health",
    "/status",
    "/api/status",
    "/about",
    "/method",
)
REQUIRED_STATUS_STATES = ("candidate", "need", "near_miss", "policy_blocked", "unavailable")
PUBLIC_RESPONSE_FORBIDDEN_MARKERS = (
    ".eureka",
    "local_review_ledger",
    "local_reviewed_records",
    "local_search_index.json",
    "local_search_index.reviewed.json",
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "C:\\",
    "D:\\",
    "/Users/",
    "\\Users\\",
    "evals/hard_queries",
    "debug internals",
    "href=\"/workbench",
    "Accept candidate",
    "rebuild index",
    "download_url",
    "install_url",
    "emulate_url",
    "live metadata request",
)
LAUNCH_BLOCKERS = (
    "no real external staging host is configured",
    "production hosting is not configured",
    "TLS/domain setup is not configured",
    "production auth is not configured",
    "official reviewed-artifact gate is not completed",
    "verified artifact evidence has not been promoted",
    "public launch approval is not recorded",
    "full discovery and release promotion checks were not run in this local rehearsal",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run local public-alpha rehearsal and write reports.")
    run_parser.add_argument("--bundle", required=True)
    run_parser.add_argument("--host", default="127.0.0.1")
    run_parser.add_argument("--port", type=int, default=8765)
    run_parser.add_argument("--out", default=DEFAULT_OUT)
    run_parser.add_argument("--query", default=DEFAULT_QUERY)

    status_parser = subparsers.add_parser("status", help="Print a concise rehearsal report summary.")
    status_parser.add_argument("--report", required=True)

    validate_parser = subparsers.add_parser("validate-report", help="Validate a rehearsal JSON report.")
    validate_parser.add_argument("--report", required=True)
    validate_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "run":
        report = run_rehearsal(args.bundle, host=args.host, port=args.port, out=args.out, query=args.query)
        report_path = write_rehearsal_reports(report, args.out)
        print(f"Public alpha rehearsal report: {report_path}", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"bundle_id: {report.get('bundle_id', '')}", file=stdout)
        print(f"launch_blockers: {len(report.get('launch_blockers') or [])}", file=stdout)
        if report.get("status") == "FAIL":
            for blocker in report.get("local_rehearsal_failures") or []:
                print(f"- {blocker}", file=stderr)
            return 1
        return 0

    if args.command == "status":
        try:
            report = load_report(args.report)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read rehearsal report: {type(exc).__name__}", file=stderr)
            return 1
        print(render_status(report), end="", file=stdout)
        return 0

    if args.command == "validate-report":
        errors = validate_report(args.report)
        payload = {
            "schema_version": "eureka.public_alpha_rehearsal_validate_report.v0",
            "status": "pass" if not errors else "fail",
            "report": str(args.report),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Public alpha rehearsal report validation failed: {args.report}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Public alpha rehearsal report validation passed: {args.report}", file=stdout)
        return 0 if not errors else 1

    parser.error(f"unsupported command: {args.command}")
    return 2


def run_rehearsal(bundle: str | Path, *, host: str, port: int, out: str | Path, query: str = DEFAULT_QUERY) -> dict[str, Any]:
    bundle_path = Path(bundle)
    warnings: list[str] = []
    local_failures: list[str] = []
    validation_errors = validate_bundle(bundle_path)
    if validation_errors:
        local_failures.extend(f"bundle validation: {error}" for error in validation_errors)
    if not _is_loopback_host(host):
        local_failures.append("rehearsal server host must be loopback")

    manifest = _read_json(bundle_path / MANIFEST_FILE) if (bundle_path / MANIFEST_FILE).is_file() else {}
    public_index = _read_json(bundle_path / PUBLIC_INDEX_FILE) if (bundle_path / PUBLIC_INDEX_FILE).is_file() else {}
    status = bundle_status(bundle_path)
    before_hashes = _artifact_hashes(bundle_path)

    routes: list[dict[str, Any]] = []
    api_status: dict[str, Any] = {}
    api_search: dict[str, Any] = {}
    record_url = ""
    actual_port = int(port)
    restart_probe = {"status": "not_run", "path": "/api/status", "status_code": 0}

    if not local_failures:
        route_result = _run_route_probe(bundle_path, host=host, port=port, query=query)
        routes = route_result["routes"]
        api_status = route_result["api_status"]
        api_search = route_result["api_search"]
        record_url = route_result["record_url"]
        actual_port = int(route_result["server_port"])
        local_failures.extend(route_result["failures"])
        restart_probe = _restart_probe(bundle_path, host=host, port=port)
        if restart_probe.get("status") != "pass":
            local_failures.append("restart probe failed")

    after_hashes = _artifact_hashes(bundle_path)
    mutation_checks = _mutation_checks(before_hashes, after_hashes)
    for check in mutation_checks.values():
        if isinstance(check, Mapping) and check.get("mutated"):
            local_failures.append(f"{check.get('name')} mutated during rehearsal")

    leakage_checks = _leakage_checks(routes)
    if not leakage_checks["passed"]:
        local_failures.extend(leakage_checks["failures"])

    safety_conflict_checks = _safety_conflict_checks(bundle_path, host=host)
    for check in safety_conflict_checks:
        if not check.get("passed"):
            local_failures.append(f"safety conflict check failed: {check.get('name')}")

    search_checks = _search_checks(api_search, public_index)
    for check_name, passed in search_checks.items():
        if isinstance(passed, bool) and not passed:
            local_failures.append(f"search check failed: {check_name}")

    record_checks = _record_checks(routes, record_url)
    for check_name, passed in record_checks.items():
        if isinstance(passed, bool) and not passed:
            local_failures.append(f"record check failed: {check_name}")

    route_failures = _route_failures(routes)
    local_failures.extend(route_failures)

    rollback_or_restart_check = {
        "restart_command": (
            f"python scripts/run_eureka_local.py --host {host} --port {actual_port} "
            f"--public-alpha --staging-bundle <bundle>"
        ),
        "manual_rollback_method": "stop the server and restart with the previous --staging-bundle path",
        "restart_probe_passed": restart_probe.get("status") == "pass",
        "restart_probe": restart_probe,
    }
    if LAUNCH_BLOCKERS:
        warnings.append("local rehearsal passed only as local proof; actual public launch remains blocked")

    report_status = "FAIL" if local_failures else ("PASS_WITH_WARNINGS" if warnings or LAUNCH_BLOCKERS else "PASS")
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": report_status,
        "bundle_path": str(bundle_path),
        "bundle_id": str(status.get("bundle_id") or ""),
        "bundle_manifest_digest": _file_sha256(bundle_path / MANIFEST_FILE) if (bundle_path / MANIFEST_FILE).is_file() else "",
        "public_index_digest": str(status.get("public_index_digest") or manifest.get("public_index_digest") or ""),
        "document_count": int(status.get("document_count") or manifest.get("document_count") or 0),
        "status_counts": dict(status.get("status_counts") or manifest.get("status_counts") or {}),
        "reviewed_record_count": int(status.get("reviewed_record_count") or manifest.get("reviewed_record_count") or 0),
        "artifact_verified_count": int(status.get("artifact_verified_count") or manifest.get("artifact_verified_count") or 0),
        "server_host": host,
        "server_port": actual_port,
        "public_alpha_mode": bool(api_status.get("public_alpha_mode") is True) if api_status else bool(status.get("public_alpha_mode") is True),
        "read_only": bool(api_status.get("read_only") is True) if api_status else bool(status.get("read_only") is True),
        "live_metadata_enabled": bool(api_status.get("live_metadata_enabled") is True),
        "public_live_fanout": bool(api_status.get("public_live_fanout") is True),
        "workbench_exposed": bool(api_status.get("workbench_exposed") is True),
        "mutation_enabled": bool(manifest.get("mutation_enabled") is True),
        "downloads_enabled": bool(manifest.get("downloads_enabled") is True),
        "routes_probed": [item for item in routes if not str(item.get("path") or "").startswith("/workbench")],
        "blocked_routes_probed": [item for item in routes if str(item.get("path") or "").startswith("/workbench")],
        "mutation_checks": mutation_checks,
        "leakage_checks": leakage_checks,
        "safety_conflict_checks": safety_conflict_checks,
        "search_checks": search_checks,
        "record_checks": record_checks,
        "rollback_or_restart_check": rollback_or_restart_check,
        "launch_blockers": list(LAUNCH_BLOCKERS),
        "warnings": warnings,
        "local_rehearsal_failures": _dedupe(local_failures),
        "report_output": str(out),
        "generated_at": "not_recorded_deterministic_local_rehearsal",
        "truth_promotion_performed": False,
        "verified_artifact_truth_created": False,
    }


def write_rehearsal_reports(report: Mapping[str, Any], out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "rehearsal_report.json"
    markdown_path = out / "REHEARSAL_REPORT.md"
    json_path.write_bytes(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8") + b"\n")
    markdown_path.write_bytes(render_markdown_report(report).encode("utf-8"))
    return json_path


def validate_report(report_path: str | Path) -> list[str]:
    try:
        report = load_report(report_path)
    except OSError as exc:
        return [f"report could not be read: {type(exc).__name__}"]
    except json.JSONDecodeError as exc:
        return [f"report is invalid JSON: {exc.msg}"]
    errors: list[str] = []
    required_keys = (
        "task_id",
        "status",
        "bundle_path",
        "bundle_id",
        "public_index_digest",
        "document_count",
        "status_counts",
        "server_host",
        "server_port",
        "public_alpha_mode",
        "read_only",
        "live_metadata_enabled",
        "public_live_fanout",
        "workbench_exposed",
        "mutation_enabled",
        "downloads_enabled",
        "routes_probed",
        "blocked_routes_probed",
        "mutation_checks",
        "leakage_checks",
        "safety_conflict_checks",
        "search_checks",
        "record_checks",
        "rollback_or_restart_check",
        "launch_blockers",
        "warnings",
    )
    for key in required_keys:
        if key not in report:
            errors.append(f"missing required field: {key}")
    if errors:
        return errors
    if report.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if report.get("status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if report.get("public_alpha_mode") is not True:
        errors.append("public_alpha_mode must be true")
    if report.get("read_only") is not True:
        errors.append("read_only must be true")
    for false_key in ("live_metadata_enabled", "public_live_fanout", "workbench_exposed", "mutation_enabled", "downloads_enabled"):
        if report.get(false_key) is not False:
            errors.append(f"{false_key} must be false")
    if not isinstance(report.get("routes_probed"), list) or not report["routes_probed"]:
        errors.append("routes_probed must be a non-empty list")
    if not isinstance(report.get("blocked_routes_probed"), list) or not report["blocked_routes_probed"]:
        errors.append("blocked_routes_probed must be a non-empty list")
    mutation = report.get("mutation_checks") if isinstance(report.get("mutation_checks"), Mapping) else {}
    for key in ("public_routes_mutated_bundle", "blocked_workbench_mutated_anything", "search_mutated_anything"):
        if mutation.get(key) is not False:
            errors.append(f"mutation_checks.{key} must be false")
    leakage = report.get("leakage_checks") if isinstance(report.get("leakage_checks"), Mapping) else {}
    if leakage.get("passed") is not True:
        errors.append("leakage_checks.passed must be true")
    rollback = report.get("rollback_or_restart_check") if isinstance(report.get("rollback_or_restart_check"), Mapping) else {}
    if rollback.get("restart_probe_passed") is not True:
        errors.append("rollback_or_restart_check.restart_probe_passed must be true")
    if not report.get("launch_blockers"):
        errors.append("launch_blockers must record actual public launch blockers")
    return errors


def load_report(report_path: str | Path) -> dict[str, Any]:
    return json.loads(Path(report_path).read_text(encoding="utf-8"))


def render_status(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"status: {report.get('status')}",
            f"bundle_id: {report.get('bundle_id')}",
            f"document_count: {report.get('document_count')}",
            f"status_counts: {json.dumps(report.get('status_counts') or {}, sort_keys=True)}",
            f"reviewed_record_count: {report.get('reviewed_record_count')}",
            f"artifact_verified_count: {report.get('artifact_verified_count')}",
            f"read_only: {str(report.get('read_only')).lower()}",
            f"live_metadata_enabled: {str(report.get('live_metadata_enabled')).lower()}",
            f"workbench_exposed: {str(report.get('workbench_exposed')).lower()}",
            f"public_live_fanout: {str(report.get('public_live_fanout')).lower()}",
            f"routes_probed: {len(report.get('routes_probed') or [])}",
            f"blocked_routes_probed: {len(report.get('blocked_routes_probed') or [])}",
            f"launch_blockers: {len(report.get('launch_blockers') or [])}",
            f"local_rehearsal_failures: {len(report.get('local_rehearsal_failures') or [])}",
        ]
    ) + "\n"


def render_markdown_report(report: Mapping[str, Any]) -> str:
    route_count = len(report.get("routes_probed") or [])
    blocked_count = len(report.get("blocked_routes_probed") or [])
    launch_blockers = "\n".join(f"- {item}" for item in report.get("launch_blockers") or ["none"])
    failures = "\n".join(f"- {item}" for item in report.get("local_rehearsal_failures") or ["none"])
    return "\n".join(
        [
            "# Public Alpha Rehearsal Report",
            "",
            f"- Status: {report.get('status')}",
            f"- Bundle ID: {report.get('bundle_id')}",
            f"- Documents: {report.get('document_count')}",
            f"- Reviewed records: {report.get('reviewed_record_count')}",
            f"- Artifact verified count: {report.get('artifact_verified_count')}",
            f"- Public routes probed: {route_count}",
            f"- Blocked routes probed: {blocked_count}",
            f"- Read only: {str(report.get('read_only')).lower()}",
            f"- Live metadata enabled: {str(report.get('live_metadata_enabled')).lower()}",
            f"- Workbench exposed: {str(report.get('workbench_exposed')).lower()}",
            f"- Public live fanout: {str(report.get('public_live_fanout')).lower()}",
            "",
            "## Local Rehearsal Failures",
            "",
            failures,
            "",
            "## Actual Public Launch Blockers",
            "",
            launch_blockers,
            "",
            "## Restart And Rollback",
            "",
            f"- Restart probe passed: {str((report.get('rollback_or_restart_check') or {}).get('restart_probe_passed')).lower()}",
            "- Rollback method: stop the server and restart with the previous staging bundle path.",
            "",
            "This report is a local rehearsal artifact only. It is not a public launch approval.",
            "",
        ]
    )


def _run_route_probe(bundle: Path, *, host: str, port: int, query: str) -> dict[str, Any]:
    options = LocalSearchOptions(index="local", index_path=str(public_index_path(bundle)), metadata_fallback="none")
    service = LocalSearchService()
    public_alpha = PublicAlphaService(
        search_service=service,
        search_options=options,
        deployment_source="staging_bundle",
        bundle_id=bundle_id(bundle),
    )
    httpd = LocalSearchHTTPServer((host, int(port)), _handler_for(service, options, None, public_alpha))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    actual_port = int(httpd.server_address[1])
    failures: list[str] = []
    routes: list[dict[str, Any]] = []
    api_status: dict[str, Any] = {}
    api_search: dict[str, Any] = {}
    record_url = ""
    try:
        for path in PUBLIC_ROUTE_PATHS:
            routes.append(_probe(host, actual_port, "GET", path))
        search_path = f"/search?q={quote(query)}"
        api_search_path = f"/api/search?q={quote(query)}"
        routes.append(_probe(host, actual_port, "GET", search_path))
        api_search_probe = _probe(host, actual_port, "GET", api_search_path)
        routes.append(api_search_probe)
        try:
            api_search = json.loads(api_search_probe["body"])
            record_url = str((api_search.get("results") or [{}])[0].get("record_url") or "")
        except (json.JSONDecodeError, AttributeError, IndexError):
            failures.append("api search response could not be parsed")
        if record_url:
            routes.append(_probe(host, actual_port, "GET", record_url))
        else:
            failures.append("api search did not return record_url")
        routes.append(_probe(host, actual_port, "GET", "/record/__missing__"))
        routes.append(_probe(host, actual_port, "GET", "/record/..%2F..%2Fprivate"))
        routes.append(_probe(host, actual_port, "GET", "/workbench"))
        routes.append(_probe(host, actual_port, "GET", "/workbench/api/status"))
        routes.append(
            _probe(
                host,
                actual_port,
                "POST",
                "/workbench/api/review/accept",
                payload={"query": query, "reason": "public rehearsal must not mutate"},
            )
        )
        try:
            api_status = json.loads(next(item["body"] for item in routes if item["path"] == "/api/status"))
        except (StopIteration, json.JSONDecodeError):
            failures.append("api status response could not be parsed")
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()
    return {
        "routes": [_route_summary(item) for item in routes],
        "api_status": api_status,
        "api_search": api_search,
        "record_url": record_url,
        "server_port": actual_port,
        "failures": failures,
    }


def _restart_probe(bundle: Path, *, host: str, port: int) -> dict[str, Any]:
    options = LocalSearchOptions(index="local", index_path=str(public_index_path(bundle)), metadata_fallback="none")
    service = LocalSearchService()
    public_alpha = PublicAlphaService(
        search_service=service,
        search_options=options,
        deployment_source="staging_bundle",
        bundle_id=bundle_id(bundle),
    )
    httpd = LocalSearchHTTPServer((host, int(port)), _handler_for(service, options, None, public_alpha))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    actual_port = int(httpd.server_address[1])
    try:
        probe = _probe(host, actual_port, "GET", "/api/status")
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()
    return {
        "status": "pass" if probe["status_code"] == 200 else "fail",
        "path": "/api/status",
        "status_code": probe["status_code"],
        "server_port": actual_port,
    }


def _probe(host: str, port: int, method: str, path: str, *, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    for attempt in range(2):
        conn = http.client.HTTPConnection(host, port, timeout=8)
        try:
            body = None
            headers = {}
            if payload is not None:
                body = json.dumps(payload)
                headers["Content-Type"] = "application/json"
            conn.request(method, path, body=body, headers=headers)
            response = conn.getresponse()
            text = response.read().decode("utf-8", errors="replace")
            return {
                "method": method,
                "path": path,
                "status_code": response.status,
                "content_type": response.getheader("Content-Type") or "",
                "body": text,
            }
        except OSError as exc:
            if attempt == 0:
                time.sleep(0.05)
                continue
            return {
                "method": method,
                "path": path,
                "status_code": 0,
                "content_type": "",
                "body": f"probe failed: {type(exc).__name__}",
            }
        finally:
            conn.close()
    return {
        "method": method,
        "path": path,
        "status_code": 0,
        "content_type": "",
        "body": "probe failed",
    }


def _route_summary(item: Mapping[str, Any]) -> dict[str, Any]:
    body = str(item.get("body") or "")
    return {
        "method": item.get("method"),
        "path": item.get("path"),
        "status_code": item.get("status_code"),
        "content_type": item.get("content_type"),
        "sample": body[:220].replace("\n", " "),
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "body": body,
    }


def _route_failures(routes: Sequence[Mapping[str, Any]]) -> list[str]:
    failures = []
    for route in routes:
        path = str(route.get("path") or "")
        code = int(route.get("status_code") or 0)
        if path.startswith("/workbench"):
            if code not in {403, 404}:
                failures.append(f"{path} should be disabled with 403 or 404")
        elif path in {"/record/__missing__", "/record/..%2F..%2Fprivate"}:
            if code != 404:
                failures.append(f"{path} should return public-safe 404")
        elif code != 200:
            failures.append(f"{path} returned {code}")
    return failures


def _leakage_checks(routes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    failures = []
    body = "\n".join(str(item.get("body") or "") for item in routes)
    for marker in PUBLIC_RESPONSE_FORBIDDEN_MARKERS:
        if marker in body:
            failures.append(f"public response contains forbidden marker: {marker}")
    return {
        "passed": not failures,
        "forbidden_markers_checked": list(PUBLIC_RESPONSE_FORBIDDEN_MARKERS),
        "failures": failures,
        "workbench_token_leaked": any(marker in body for marker in ("local-dev-token", "X-Eureka-Workbench-Token")),
        "local_path_leaked": any(marker in body for marker in ("C:\\", "D:\\", "/Users/", "\\Users\\", ".eureka")),
        "unsafe_action_affordance_leaked": any(marker in body for marker in ("href=\"/workbench", "Accept candidate", "rebuild index")),
    }


def _safety_conflict_checks(bundle: Path, *, host: str) -> list[dict[str, Any]]:
    checks = [
        _run_fail_closed_check("live_metadata_mode", "--smoke", "--staging-bundle", str(bundle), "--metadata-fallback", "ia_live"),
        _run_fail_closed_check("allow_live_metadata", "--smoke", "--staging-bundle", str(bundle), "--allow-live-metadata"),
        _run_fail_closed_check(
            "workbench_enabled",
            "--smoke",
            "--staging-bundle",
            str(bundle),
            "--enable-workbench",
            "--workbench-token",
            "local-dev-token",
        ),
        _run_fail_closed_check("non_loopback_host", "--host", "0.0.0.0", "--smoke", "--staging-bundle", str(bundle)),
        _run_fail_closed_check("missing_bundle", "--smoke", "--staging-bundle", str(bundle / "__missing__")),
    ]
    checks.append(_invalid_runtime_config_check(bundle, host=host))
    return checks


def _run_fail_closed_check(name: str, *args: str) -> dict[str, Any]:
    stdout = _StringSink()
    stderr = _StringSink()
    code = run_local_main(list(args), stdout=stdout, stderr=stderr)
    return {
        "name": name,
        "expected_return_code": 2,
        "actual_return_code": code,
        "passed": code == 2,
        "stdout_sample": stdout.value[:220],
        "stderr_sample": stderr.value[:220],
    }


def _invalid_runtime_config_check(bundle: Path, *, host: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_bundle = Path(temp_dir) / "bundle"
        shutil.copytree(bundle, temp_bundle)
        config_path = temp_bundle / RUNTIME_CONFIG_FILE
        config = _read_json(config_path)
        config["live_metadata_enabled"] = True
        config_path.write_bytes(json.dumps(config, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8") + b"\n")
        errors = validate_bundle(temp_bundle)
    return {
        "name": "invalid_public_runtime_config",
        "passed": bool(errors),
        "errors": errors,
        "host": host,
    }


def _search_checks(api_search: Mapping[str, Any], public_index: Mapping[str, Any]) -> dict[str, Any]:
    results = [item for item in api_search.get("results") or [] if isinstance(item, Mapping)]
    first = results[0] if results else {}
    status_counts = dict(public_index.get("status_counts") or {})
    return {
        "sound_blaster_reviewed_first": first.get("review_state") == "accepted",
        "artifact_verified_false": first.get("artifact_verified") is False,
        "fallback_used_false": api_search.get("fallback_used") is False,
        "fallback_mode_none": api_search.get("fallback_mode") == "none",
        "status_vocabulary_visible": bool(api_search.get("status_summary")) or bool(status_counts),
        "staged_index_states_represented": all(status_counts.get(status, 0) > 0 for status in REQUIRED_STATUS_STATES),
        "represented_statuses": {status: int(status_counts.get(status, 0)) for status in REQUIRED_STATUS_STATES},
    }


def _record_checks(routes: Sequence[Mapping[str, Any]], record_url: str) -> dict[str, Any]:
    route_by_path = {str(item.get("path") or ""): item for item in routes}
    return {
        "record_link_present": bool(record_url),
        "record_link_public_safe": str(record_url).startswith("/record/") and ".." not in str(record_url),
        "record_route_200": int(route_by_path.get(record_url, {}).get("status_code") or 0) == 200,
        "missing_record_404": int(route_by_path.get("/record/__missing__", {}).get("status_code") or 0) == 404,
        "path_traversal_record_404": int(route_by_path.get("/record/..%2F..%2Fprivate", {}).get("status_code") or 0) == 404,
    }


def _artifact_hashes(bundle: Path) -> dict[str, dict[str, Any]]:
    paths = {
        "bundle_manifest": bundle / MANIFEST_FILE,
        "bundle_public_index": bundle / PUBLIC_INDEX_FILE,
        "bundle_runtime_config": bundle / RUNTIME_CONFIG_FILE,
        "local_review_ledger": REPO_ROOT / ".eureka" / "local_review_ledger.jsonl",
        "local_reviewed_records": REPO_ROOT / ".eureka" / "local_reviewed_records.jsonl",
        "local_reviewed_index": REPO_ROOT / ".eureka" / "local_search_index.reviewed.json",
    }
    return {
        name: {
            "name": name,
            "present": path.is_file(),
            "sha256": _file_sha256(path) if path.is_file() else "",
        }
        for name, path in paths.items()
    }


def _mutation_checks(before: Mapping[str, Mapping[str, Any]], after: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    per_artifact = {}
    for name, before_item in before.items():
        after_item = after.get(name, {})
        per_artifact[name] = {
            "name": name,
            "present_before": bool(before_item.get("present")),
            "present_after": bool(after_item.get("present")),
            "mutated": before_item.get("sha256") != after_item.get("sha256"),
        }
    return {
        "per_artifact": per_artifact,
        "public_routes_mutated_bundle": any(
            per_artifact[name]["mutated"]
            for name in ("bundle_manifest", "bundle_public_index", "bundle_runtime_config")
            if name in per_artifact
        ),
        "blocked_workbench_mutated_anything": any(item["mutated"] for item in per_artifact.values()),
        "search_mutated_anything": any(item["mutated"] for item in per_artifact.values()),
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _file_sha256(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""


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


class _StringSink:
    def __init__(self) -> None:
        self.value = ""

    def write(self, value: str) -> int:
        self.value += str(value)
        return len(value)

    def flush(self) -> None:
        return


if __name__ == "__main__":
    raise SystemExit(main())

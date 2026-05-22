#!/usr/bin/env python3
"""Run explicit read-only LAN-bind smoke for the Eureka local service."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = Path(__file__).resolve().parent
for item in (REPO_ROOT, SCRIPTS_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from eureka_lan_read_only_probe import run_probe, validate_base_url
from eureka_lan_shutdown_check import run_shutdown_check
from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_network import validate_service_host
from runtime.local_service import LocalServiceApp


LAN_HOSTS = {"0.0.0.0", "::"}
LAN_CLIENT_SIMULATION_HOST = "192.168.1.20"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bind-lan", action="store_true")
    parser.add_argument("--read-only", action="store_true")
    parser.add_argument("--base-url")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        result = run_lan_smoke(
            instance=Path(args.instance),
            host=args.host,
            port=args.port,
            bind_lan=args.bind_lan,
            read_only=args.read_only,
            base_url=args.base_url,
        )
    except ValueError as exc:
        result = fail_result("lan_smoke_rejected", str(exc), args.host, args.port)
        print(f"ERROR: {exc}", file=stderr)
        emit_result(result, args.json, args.output, stdout)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("lan_smoke_failed", str(exc), args.host, args.port)
        print(f"ERROR: {exc}", file=stderr)
        emit_result(result, args.json, args.output, stdout)
        return 1

    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") in {"pass", "pass_with_warnings"} else 1


def run_lan_smoke(
    *,
    instance: Path,
    host: str,
    port: int,
    bind_lan: bool,
    read_only: bool,
    base_url: str | None = None,
) -> dict[str, Any]:
    if host in LAN_HOSTS and not bind_lan:
        raise ValueError("LAN bind hosts require explicit --bind-lan")
    if not read_only:
        raise ValueError("LOCAL-12 LAN smoke requires --read-only")
    validate_service_host(host, bind_lan=bind_lan)
    ensure_instance(instance)

    process, startup = start_server_process(instance, host, port, bind_lan)
    actual_port = int(startup.get("port", port))
    smoke_base_url = validate_base_url(base_url or f"http://127.0.0.1:{actual_port}")
    probe_result: dict[str, Any] = {}
    lan_gate_result: dict[str, Any] = {}
    shutdown_result: dict[str, Any] = {}
    try:
        probe_result = run_probe(smoke_base_url)
        lan_gate_result = run_lan_client_gate_checks(instance)
    finally:
        stop_server_process(process)
        shutdown_result = run_shutdown_check(instance, actual_port)

    read_only_ok = bool(probe_result.get("read_only_routes_passed"))
    mutation_ok = bool(probe_result.get("mutation_routes_blocked") and lan_gate_result.get("lan_mutation_routes_blocked"))
    operator_localhost_only = bool(lan_gate_result.get("localhost_operator_mutations_remain_token_gated"))
    shutdown_ok = shutdown_result.get("status") == "pass"
    status = "pass_with_warnings" if read_only_ok and mutation_ok and operator_localhost_only and shutdown_ok else "fail"
    warnings = ["external client smoke was not performed; no second client device is claimed in this automated run"]
    if probe_result.get("status") == "fail":
        warnings.append("read-only probe reported a failure")
    if shutdown_result.get("status") != "pass":
        warnings.append("shutdown check reported a failure")
    return {
        "schema_version": "local_lan_smoke_result.v0",
        "task": "LOCAL-12",
        "status": status,
        "host": host,
        "port": int(port),
        "actual_port": actual_port,
        "base_url": smoke_base_url,
        "bind_lan_used": bool(bind_lan),
        "read_only_mode": True,
        "same_machine_lan_bind_smoke_passed": bool(read_only_ok and mutation_ok and operator_localhost_only and shutdown_ok),
        "external_client_smoke_performed": False,
        "external_client_smoke_status": "not_performed",
        "read_only_routes_passed": read_only_ok,
        "mutation_routes_blocked": mutation_ok,
        "operator_mutations_localhost_only": operator_localhost_only,
        "lan_gate_checks": lan_gate_result,
        "probe_result": probe_result,
        "shutdown_result": shutdown_result,
        "source_probe_executed": False,
        "workunit_execution_from_lan": False,
        "review_mutation_from_lan": False,
        "rebuild_mutation_from_lan": False,
        "external_internet_used": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": warnings,
        "limitations": ["same-machine LAN-bind smoke is not cross-device proof"],
    }


def run_lan_client_gate_checks(instance: Path) -> dict[str, Any]:
    runtime = open_local_appliance(instance, read_only=True)
    try:
        app = LocalServiceApp(runtime)
        checks = {
            "GET /api/v1/status": app.handle("GET", "/api/v1/status", client_host=LAN_CLIENT_SIMULATION_HOST).status_code,
            "POST /rebuild": app.handle("POST", "/rebuild", client_host=LAN_CLIENT_SIMULATION_HOST).status_code,
            "POST /review/nonexistent-local-12/decision": app.handle(
                "POST",
                "/review/nonexistent-local-12/decision",
                client_host=LAN_CLIENT_SIMULATION_HOST,
            ).status_code,
            "POST /workers/run": app.handle("POST", "/workers/run", client_host=LAN_CLIENT_SIMULATION_HOST).status_code,
            "GET /api/v1/source-probe": app.handle("GET", "/api/v1/source-probe", client_host=LAN_CLIENT_SIMULATION_HOST).status_code,
            "POST /rebuild loopback": app.handle("POST", "/rebuild", client_host="127.0.0.1").status_code,
        }
    finally:
        close_local_appliance(runtime)
    return {
        "schema_version": "local_lan_client_gate_check.v0",
        "client_scope": "lan",
        "client_host_redacted": "private-lan-simulated",
        "checks": checks,
        "lan_read_only_status_allowed": checks["GET /api/v1/status"] == 200,
        "lan_mutation_routes_blocked": checks["POST /rebuild"] == 403
        and checks["POST /review/nonexistent-local-12/decision"] == 403,
        "lan_workunit_execution_blocked": checks["POST /workers/run"] == 403,
        "lan_source_probe_routes_blocked": checks["GET /api/v1/source-probe"] == 403,
        "localhost_operator_mutations_remain_token_gated": checks["POST /rebuild loopback"] == 401,
        "review_mutation_from_lan": False,
        "rebuild_mutation_from_lan": False,
        "workunit_execution_from_lan": False,
        "source_probe_executed": False,
    }


def ensure_instance(instance: Path) -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or completed.stdout.strip() or "instance initialization failed")


def start_server_process(instance: Path, host: str, port: int, bind_lan: bool) -> tuple[subprocess.Popen[str], dict[str, Any]]:
    args = [
        sys.executable,
        "scripts/eureka_local_server.py",
        "--instance",
        str(instance),
        "--host",
        host,
        "--port",
        str(port),
        "--read-only",
        "--json-startup",
    ]
    if bind_lan:
        args.append("--bind-lan")
    process = subprocess.Popen(
        args,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    line = process.stdout.readline() if process.stdout else ""
    try:
        startup = json.loads(line)
    except json.JSONDecodeError as exc:
        stop_server_process(process)
        stderr = process.stderr.read() if process.stderr else ""
        raise ValueError(f"server startup did not emit JSON: {line or stderr}") from exc
    if startup.get("status") != "pass":
        stop_server_process(process)
        raise ValueError(str(startup.get("message") or startup.get("error") or "server startup failed"))
    return process, startup


def stop_server_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        close_process_pipes(process)
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    close_process_pipes(process)


def close_process_pipes(process: subprocess.Popen[str]) -> None:
    if process.stdout:
        process.stdout.close()
    if process.stderr:
        process.stderr.close()


def fail_result(code: str, message: str, host: str, port: int) -> dict[str, Any]:
    return {
        "schema_version": "local_lan_smoke_result.v0",
        "task": "LOCAL-12",
        "status": "fail",
        "error": code,
        "message": message,
        "host": host,
        "port": port,
        "bind_lan_used": False,
        "read_only_mode": False,
        "same_machine_lan_bind_smoke_passed": False,
        "external_client_smoke_performed": False,
        "external_client_smoke_status": "not_performed",
        "read_only_routes_passed": False,
        "mutation_routes_blocked": False,
        "operator_mutations_localhost_only": False,
        "external_internet_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    print(f"same_machine_lan_bind_smoke_passed: {result.get('same_machine_lan_bind_smoke_passed')}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

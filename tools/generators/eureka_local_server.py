#!/usr/bin/env python3
"""Run the read-only Eureka local HTTP service."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import LocalApplianceError
from runtime.local.service import LocalServiceError, create_local_http_server, validate_host_allowed


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit initialized local instance root.")
    parser.add_argument("--host", default="127.0.0.1", help="Loopback bind host.")
    parser.add_argument("--port", type=int, default=8765, help="Loopback bind port.")
    parser.add_argument("--read-only", action="store_true", help="Accepted for explicit read-only startup.")
    parser.add_argument("--bind-lan", action="store_true", help="Allow an explicit read-only bind to 0.0.0.0 or ::.")
    parser.add_argument("--operator-token", help="Optional in-memory operator token for LOCAL review mutations.")
    parser.add_argument("--write-mode", action="store_true", help="Rejected; the local service is read-only.")
    parser.add_argument("--json-startup", action="store_true", help="Print startup JSON after binding.")
    args = parser.parse_args(argv)

    if not args.instance:
        result = fail_result("missing_instance", "--instance is required", host=args.host, port=args.port)
        emit_startup(result, args.json_startup, stdout, stderr)
        return 2
    if args.write_mode:
        result = fail_result("write_mode_forbidden", "write mode is disabled for the local service", host=args.host, port=args.port)
        emit_startup(result, args.json_startup, stdout, stderr)
        return 2
    try:
        validate_host_allowed(args.host, bind_lan=args.bind_lan)
    except LocalServiceError as exc:
        result = fail_result("host_rejected", str(exc), host=args.host, port=args.port)
        emit_startup(result, args.json_startup, stdout, stderr)
        return 2

    handle = None
    try:
        handle = create_local_http_server(
            Path(args.instance),
            host=args.host,
            port=args.port,
            read_only=True,
            operator_token=args.operator_token,
            bind_lan=args.bind_lan,
        )
        lan_enabled = args.host in {"0.0.0.0", "::"} and args.bind_lan
        startup = {
            "schema_version": "local_http_server_startup.v0",
            "status": "pass",
            "instance": str(Path(args.instance)),
            "host": args.host,
            "port": handle.server_port,
            "base_url": f"http://{args.host}:{handle.server_port}",
            "read_only": True,
            "localhost_only": not lan_enabled,
            "write_routes_enabled": False,
            "operator_token_configured": bool(args.operator_token),
            "bind_lan": bool(args.bind_lan),
            "lan_enabled": lan_enabled,
            "lan_read_only": True,
            "lan_mutations_enabled": False,
            "deployment_performed": False,
            "source_probe_execution_enabled": False,
            "workunit_execution_enabled": False,
            "operator_gated_review_decisions_enabled": True,
            "operator_gated_rebuild_enabled": True,
            "review_decision_mutation_enabled": False,
            "index_rebuild_enabled": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
            "warnings": list(handle.warnings),
        }
        emit_startup(startup, args.json_startup, stdout, stderr)
        handle.httpd.serve_forever()
        return 0
    except KeyboardInterrupt:
        return 0
    except (LocalApplianceError, LocalServiceError, OSError, ValueError) as exc:
        result = fail_result("server_start_failed", str(exc), host=args.host, port=args.port)
        emit_startup(result, args.json_startup, stdout, stderr)
        return 2
    finally:
        if handle is not None:
            handle.close()


def fail_result(code: str, message: str, *, host: str, port: int) -> dict[str, Any]:
    return {
        "schema_version": "local_http_server_startup.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "host": host,
        "port": port,
        "read_only": True,
        "localhost_only": True,
        "write_routes_enabled": False,
        "bind_lan": False,
        "lan_enabled": False,
        "lan_read_only": True,
        "lan_mutations_enabled": False,
        "deployment_performed": False,
        "source_probe_execution_enabled": False,
        "workunit_execution_enabled": False,
        "review_decision_mutation_enabled": False,
        "index_rebuild_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit_startup(result: dict[str, Any], as_json: bool, stdout: TextIO, stderr: TextIO) -> None:
    if as_json:
        print(json.dumps(result, sort_keys=True), file=stdout, flush=True)
        return
    if result.get("status") == "pass":
        print(f"Eureka local service listening on {result['base_url']}", file=stdout, flush=True)
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}", file=stdout, flush=True)
    else:
        print(f"ERROR: {result.get('message', result.get('error'))}", file=stderr, flush=True)


if __name__ == "__main__":
    raise SystemExit(main())

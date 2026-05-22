#!/usr/bin/env python3
"""Check Eureka local service LAN binding policy without starting a server."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_network import build_firewall_warning, build_lan_warning, is_lan_bind_host, validate_service_host


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--bind-lan", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    result = check_lan_policy(args.host, bind_lan=args.bind_lan)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, sort_keys=True), file=stdout)
    else:
        stream = stdout if result["status"] == "pass" else stderr
        print(f"status: {result['status']}", file=stream)
        print(f"host_allowed: {result['host_allowed']}", file=stream)
        if result.get("message"):
            print(f"message: {result['message']}", file=stream)
    return 0


def check_lan_policy(host: str, bind_lan: bool = False) -> dict[str, Any]:
    warnings = [build_lan_warning(), build_firewall_warning()] if bind_lan and is_lan_bind_host(host) else []
    try:
        normalized = validate_service_host(host, bind_lan=bind_lan)
        allowed = True
        message = "host accepted by local network policy"
    except Exception as exc:
        normalized = str(host or "")
        allowed = False
        message = str(exc)
    return {
        "schema_version": "local_lan_policy_check.v0",
        "status": "pass",
        "host": host,
        "normalized_host": normalized,
        "bind_lan": bool(bind_lan),
        "host_allowed": allowed,
        "lan_bind_host": is_lan_bind_host(host),
        "lan_read_only": True,
        "lan_mutations_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "message": message,
        "warnings": warnings,
        "limitations": ["policy check only; no server start and no network call"],
    }


if __name__ == "__main__":
    raise SystemExit(main())

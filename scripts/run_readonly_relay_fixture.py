#!/usr/bin/env python3
"""Run or check the fixture-only localhost read-only relay."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.relay.profiles import load_relay_policy, load_relay_profile, validate_relay_profile  # noqa: E402
from runtime.relay.request_response import build_relay_status  # noqa: E402
from runtime.relay.security import validate_bind_host  # noqa: E402
from runtime.relay.server import create_readonly_relay_handler, run_loopback_server_once_or_until_interrupt  # noqa: E402
from runtime.relay.snapshot_store import load_snapshot_for_relay  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or serve an explicit fixture snapshot over a localhost-only read-only relay.")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    policy = load_relay_policy()
    host_errors = validate_bind_host(args.host, policy)
    if host_errors:
        raise ValueError("; ".join(host_errors))
    profile = load_relay_profile(args.profile)
    profile_errors = validate_relay_profile(profile, policy)
    if profile_errors:
        raise ValueError("; ".join(profile_errors))
    store = load_snapshot_for_relay(args.snapshot, policy)
    status = build_relay_status(store)
    status["host"] = args.host
    status["port"] = args.port
    status["server_starts_by_default"] = False
    if args.serve:
        handler = create_readonly_relay_handler(store, profile, policy)
        run_loopback_server_once_or_until_interrupt({"host": args.host, "port": args.port, "handler": handler}, policy)
        return 0
    if args.as_json or args.check:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print("Eureka relay fixture check: PASS")
        print(f"Snapshot: {status.get('snapshot_ref', '')}")
        print("Server not started. Use --serve explicitly to bind loopback.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


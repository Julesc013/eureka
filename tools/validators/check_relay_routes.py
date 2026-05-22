#!/usr/bin/env python3
"""Validate relay route tables and unsafe route/method blocking."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.relay.profiles import ensure_allowed_relay_output_path, load_relay_policy, load_relay_profile  # noqa: E402
from runtime.relay.routes import build_relay_route_table, validate_relay_route  # noqa: E402
from runtime.relay.security import validate_method_allowed, validate_no_write_route  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check fixture relay routes.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    policy = load_relay_policy()
    profile = load_relay_profile(args.profile)
    routes = build_relay_route_table(profile, policy)
    errors: list[str] = []
    for route in routes:
        errors.extend(validate_relay_route(route, policy))
    for method in ("POST", "PUT", "PATCH", "DELETE"):
        if not validate_method_allowed(method, policy):
            errors.append(f"unsafe method was not blocked: {method}")
    for unsafe in ("/admin", "/upload", "/download", "/execute"):
        if not validate_no_write_route(unsafe, policy):
            errors.append(f"unsafe route was not blocked: {unsafe}")
    report = {
        "schema_version": "relay_route_check.v0",
        "status": "pass" if not errors else "fail",
        "route_count": len(routes),
        "routes": routes,
        "unsafe_methods_blocked": not any(error.startswith("unsafe method") for error in errors),
        "unsafe_routes_blocked": not any(error.startswith("unsafe route") for error in errors),
        "errors": sorted(dict.fromkeys(errors)),
    }
    if errors:
        raise ValueError("; ".join(report["errors"]))
    if args.output and not args.check:
        output = ensure_allowed_relay_output_path(args.output, policy)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.as_json or args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"relay route check: PASS ({len(routes)} routes)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


#!/usr/bin/env python3
"""Smoke the public search UX MVP route matrix from examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_search import build_public_search_ux_mvp_bundle  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Use committed route examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")

    result = build_public_search_ux_mvp_bundle()
    required_routes = {"/", "/search", "/object/{id}", "/candidate/{id}", "/need/{id}", "/source/{id}", "/evidence/{id}", "/status"}
    observed_routes = {route["route"] for route in result["routes"]}
    checks = {
        "required_routes_present": required_routes.issubset(observed_routes),
        "all_routes_get": all(route["method"] == "GET" for route in result["routes"]),
        "all_routes_no_js": all(route["no_js_required"] is True for route in result["routes"]),
        "all_routes_read_only": all(route["public_read_only"] is True for route in result["routes"]),
        "all_routes_no_mutation": all(route["mutation_enabled"] is False for route in result["routes"]),
        "all_routes_no_live_source_call": all(route["live_source_call_enabled"] is False for route in result["routes"]),
    }
    failures = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema_version": "public_search_ux_mvp_route_smoke.v0",
        "task": "PUBLIC-SEARCH-UX-MVP-00",
        "status": "pass" if not failures else "fail",
        "routes": result["routes"],
        "checks": checks,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render relay fixture responses without starting a server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.relay.profiles import ensure_allowed_relay_input_path, ensure_allowed_relay_output_path, load_json, load_relay_policy, load_relay_profile  # noqa: E402
from runtime.relay.renderers import (  # noqa: E402
    render_relay_file_tree,
    render_relay_json_manifest,
    render_relay_lite_html,
    render_relay_native_fixture_json,
    render_relay_text,
)
from runtime.relay.request_response import build_relay_request, build_relay_response  # noqa: E402
from runtime.relay.snapshot_store import load_snapshot_for_relay  # noqa: E402
from runtime.relay.terminal import build_terminal_menu  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a relay fixture route in-process.")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--render-profile", required=True, choices=("text", "lite_html", "file_tree", "terminal", "native_fixture_json", "json_manifest"))
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    policy = load_relay_policy()
    profile = load_relay_profile(args.profile)
    store = load_snapshot_for_relay(args.snapshot, policy)
    route_path = _route_arg_to_path(args.route)
    request = build_relay_request("GET", route_path, {"format": args.render_profile}, profile, policy)
    response = build_relay_response(request, store, policy)
    response["render_profile"] = args.render_profile
    response["content_type"] = _content_type(args.render_profile)
    content = _render(response, args.render_profile, store, policy)
    if args.output and not args.check:
        output = ensure_allowed_relay_output_path(args.output, policy)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    if args.as_json:
        payload = dict(response)
        payload.pop("body", None)
        payload["content_preview"] = content[:240]
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(content, end="")
    return 0


def _route_arg_to_path(value: str) -> str:
    candidate = Path(value)
    if candidate.exists():
        payload = load_json(ensure_allowed_relay_input_path(candidate))
        return str(payload.get("route_path", "/status"))
    return value


def _render(response: dict, profile: str, store: dict, policy: dict) -> str:
    if profile == "lite_html":
        return render_relay_lite_html(response, policy)
    if profile == "file_tree":
        return render_relay_file_tree(response, policy)
    if profile == "json_manifest":
        return render_relay_json_manifest(response, policy)
    if profile == "native_fixture_json":
        return render_relay_native_fixture_json(response, policy)
    if profile == "terminal":
        body = response.get("body")
        if isinstance(body, dict) and "terminal_menu" in body:
            return str(body["terminal_menu"])
        return build_terminal_menu(store, policy)
    return render_relay_text(response, policy)


def _content_type(profile: str) -> str:
    if profile == "lite_html":
        return "text/html; charset=utf-8"
    if profile in {"json_manifest", "native_fixture_json"}:
        return "application/json; charset=utf-8"
    return "text/plain; charset=utf-8"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


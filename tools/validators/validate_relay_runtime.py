#!/usr/bin/env python3
"""Validate D-BUNDLE-02 relay runtime artifacts."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.relay.profiles import (  # noqa: E402
    detect_relay_boundary_violations,
    ensure_allowed_relay_output_path,
    load_json,
    load_relay_policy,
    validate_native_fixture_endpoint,
    validate_old_browser_profile,
    validate_relay_profile,
    validate_terminal_profile,
)
from runtime.relay.routes import build_relay_route_table, validate_relay_route  # noqa: E402
from runtime.relay.security import validate_bind_host, validate_method_allowed, validate_no_live_access, validate_no_write_route  # noqa: E402


CONTRACTS = [
    "contracts/relay/relay_profile.v0.json",
    "contracts/relay/relay_route.v0.json",
    "contracts/relay/relay_request.v0.json",
    "contracts/relay/relay_response.v0.json",
    "contracts/relay/relay_status.v0.json",
    "contracts/relay/relay_manifest.v0.json",
    "contracts/relay/relay_security_policy.v0.json",
    "contracts/relay/old_browser_profile.v0.json",
    "contracts/relay/terminal_profile.v0.json",
    "contracts/schema/control/fixtures/relay/native_fixture_endpoint.v0.json",
]
POLICIES = [
    "control/inventory/relay/relay_profile_policy.json",
    "control/inventory/relay/relay_route_policy.json",
    "control/inventory/relay/relay_security_policy.json",
    "control/inventory/relay/relay_loopback_policy.json",
    "control/inventory/relay/relay_read_only_policy.json",
    "control/inventory/relay/relay_render_policy.json",
    "control/inventory/relay/relay_old_browser_policy.json",
    "control/inventory/relay/relay_terminal_policy.json",
    "control/inventory/relay/relay_native_fixture_policy.json",
    "control/inventory/relay/relay_path_policy.json",
    "control/inventory/relay/relay_truth_policy.json",
    "control/inventory/relay/relay_no_live_access_policy.json",
]
EXAMPLES = [
    "examples/relay/profiles/localhost_readonly_profile_v0.json",
    "examples/relay/profiles/old_browser_html32_profile_v0.json",
    "examples/relay/profiles/terminal_text_profile_v0.json",
    "examples/relay/profiles/native_fixture_profile_v0.json",
    "examples/relay/profiles/policy_blocked_relay_profile_v0.json",
    "examples/relay/routes/status_route_v0.json",
    "examples/relay/routes/search_route_v0.json",
    "examples/relay/routes/object_route_v0.json",
    "examples/relay/routes/source_route_v0.json",
    "examples/relay/routes/need_route_v0.json",
    "examples/relay/routes/action_route_v0.json",
    "examples/relay/routes/manifest_route_v0.json",
    "examples/relay/routes/files_route_v0.json",
    "examples/relay/routes/terminal_route_v0.json",
    "examples/relay/routes/policy_blocked_route_v0.json",
    "examples/relay/responses/status_response_v0.json",
    "examples/relay/responses/manifest_response_v0.json",
    "examples/relay/native/native_fixture_endpoint_status_v0.json",
    "examples/relay/native/native_fixture_endpoint_search_v0.json",
    "examples/relay/native/native_fixture_endpoint_object_v0.json",
    "control/audits/d-bundle-02-localhost-readonly-relay-v0/d_bundle_02_report.json",
]
TEXT_EXAMPLES = [
    "examples/relay/responses/search_lite_html_response_v0.html",
    "examples/relay/responses/search_text_response_v0.txt",
    "examples/relay/responses/object_lite_html_response_v0.html",
    "examples/relay/responses/object_text_response_v0.txt",
    "examples/relay/responses/terminal_menu_response_v0.txt",
    "examples/relay/responses/policy_blocked_response_v0.txt",
]
MODULES = [
    "runtime.relay.profiles",
    "runtime.relay.routes",
    "runtime.relay.request_response",
    "runtime.relay.snapshot_store",
    "runtime.relay.renderers",
    "runtime.relay.security",
    "runtime.relay.server",
    "runtime.relay.terminal",
    "runtime.relay.summaries",
]
SCRIPTS = [
    "scripts/run_readonly_relay_fixture.py",
    "scripts/check_relay_routes.py",
    "scripts/render_relay_fixture.py",
    "scripts/validate_relay_runtime.py",
    "scripts/summarize_relay_runtime.py",
]
DOCS = [
    "docs/reference/RELAY_PROFILE_CONTRACT.md",
    "docs/reference/RELAY_ROUTE_CONTRACT.md",
    "docs/reference/RELAY_RESPONSE_CONTRACT.md",
    "docs/reference/RELAY_STATUS_CONTRACT.md",
    "docs/reference/RELAY_MANIFEST_CONTRACT.md",
    "docs/reference/OLD_BROWSER_PROFILE_CONTRACT.md",
    "docs/reference/TERMINAL_PROFILE_CONTRACT.md",
    "docs/architecture/LOCALHOST_RELAY_MODEL.md",
    "docs/architecture/RELAY_RENDERING_MODEL.md",
    "docs/operations/RELAY_READ_ONLY_SECURITY_POLICY.md",
    "docs/operations/RELAY_OLD_BROWSER_COMPATIBILITY.md",
    "docs/operations/RELAY_TERMINAL_TEXT_MODE.md",
    "docs/operations/RELAY_NATIVE_FIXTURE_ENDPOINTS.md",
    "docs/operations/RELAY_NO_LIVE_ACCESS_POLICY.md",
]
AUDIT_DIR = "control/audits/d-bundle-02-localhost-readonly-relay-v0"
AUDIT_FILES = [
    "README.md",
    "d_bundle_02_report.json",
    "relay_profile_summary.md",
    "relay_route_summary.md",
    "relay_security_report.md",
    "relay_old_browser_report.md",
    "relay_terminal_report.md",
    "relay_native_fixture_report.md",
    "relay_no_live_access_report.md",
    "relay_no_public_binding_report.md",
    "c_bundle_01_readiness_recommendation.md",
    "validation.md",
    "generated/sample_relay_status.json",
    "generated/sample_relay_manifest.json",
    "generated/sample_relay_search_text.txt",
    "generated/sample_relay_search_lite.html",
    "generated/sample_relay_terminal_menu.txt",
    "generated/sample_relay_native_fixture_response.json",
    "generated/sample_relay_summary.md",
]
FORBIDDEN_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib\.request|http\.client|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)


def main() -> int:
    policy = load_relay_policy()
    payloads = _json_files(CONTRACTS + POLICIES + EXAMPLES)
    for rel in TEXT_EXAMPLES:
        if not (REPO_ROOT / rel).exists():
            raise AssertionError(f"missing required text/html example: {rel}")
    for module in MODULES:
        importlib.import_module(module)
    _validate_payloads(payloads, policy)
    _validate_required_files(SCRIPTS + DOCS + [f"{AUDIT_DIR}/{item}" for item in AUDIT_FILES])
    _assert_forbidden_outputs_rejected(policy)
    _assert_unsafe_routes_and_hosts_blocked(policy)
    _assert_no_forbidden_imports()
    _run_scripts()
    for private_root in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (REPO_ROOT / private_root).exists():
            raise AssertionError(f"local private root exists: {private_root}")
    print("validate_relay_runtime: PASS")
    return 0


def _json_files(paths: Iterable[str]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for rel in paths:
        path = REPO_ROOT / rel
        if not path.exists():
            raise AssertionError(f"missing required file: {rel}")
        payloads.append(load_json(path))
    return payloads


def _validate_payloads(payloads: Iterable[Mapping[str, Any]], policy: Mapping[str, Any]) -> None:
    errors: list[str] = []
    for payload in payloads:
        schema = payload.get("schema_version")
        if schema == "relay_profile.v0":
            errors.extend(validate_relay_profile(payload, policy))
        elif schema == "relay_route.v0":
            errors.extend(validate_relay_route(payload, policy))
        elif schema == "old_browser_profile.v0":
            errors.extend(validate_old_browser_profile(payload, policy))
        elif schema == "terminal_profile.v0":
            errors.extend(validate_terminal_profile(payload, policy))
        elif schema == "native_fixture_endpoint.v0":
            errors.extend(validate_native_fixture_endpoint(payload, policy))
        errors.extend(detect_relay_boundary_violations(payload))
    if errors:
        raise AssertionError("; ".join(sorted(dict.fromkeys(errors))))


def _validate_required_files(paths: Iterable[str]) -> None:
    for rel in paths:
        if not (REPO_ROOT / rel).exists():
            raise AssertionError(f"missing required file: {rel}")


def _assert_forbidden_outputs_rejected(policy: Mapping[str, Any]) -> None:
    for rel in ("site/dist/relay.html", "site/dist/data/public_index/relay.json", "runtime/relay/generated.json", "contracts/relay/generated.json"):
        try:
            ensure_allowed_relay_output_path(rel, policy)
        except ValueError:
            continue
        raise AssertionError(f"forbidden output root was accepted: {rel}")


def _assert_unsafe_routes_and_hosts_blocked(policy: Mapping[str, Any]) -> None:
    if not validate_bind_host("0.0.0.0", policy):
        raise AssertionError("0.0.0.0 bind was not rejected")
    if not validate_bind_host("*", policy):
        raise AssertionError("wildcard public bind was not rejected")
    for method in ("POST", "PUT", "PATCH", "DELETE"):
        if not validate_method_allowed(method, policy):
            raise AssertionError(f"{method} was not rejected")
    for route in ("/admin", "/upload", "/download", "/execute"):
        if not validate_no_write_route(route, policy):
            raise AssertionError(f"{route} was not rejected")
    errors = validate_no_live_access(policy)
    if errors:
        raise AssertionError("; ".join(errors))


def _assert_no_forbidden_imports() -> None:
    for rel in SCRIPTS + [f"runtime/relay/{name}.py" for name in ("profiles", "routes", "request_response", "snapshot_store", "renderers", "security", "server", "terminal", "summaries")]:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        if FORBIDDEN_IMPORT_RE.search(text):
            raise AssertionError(f"forbidden outbound/network/browser/provider import appears in {rel}")


def _run(args: list[str], expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)
    if expect_success and result.returncode:
        raise AssertionError(f"{' '.join(args)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


def _run_scripts() -> None:
    _run([sys.executable, "scripts/check_relay_routes.py", "--profile", "examples/relay/profiles/localhost_readonly_profile_v0.json", "--check"])
    _run(
        [
            sys.executable,
            "scripts/render_relay_fixture.py",
            "--snapshot",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--profile",
            "examples/relay/profiles/localhost_readonly_profile_v0.json",
            "--route",
            "/search",
            "--render-profile",
            "text",
            "--check",
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/run_readonly_relay_fixture.py",
            "--snapshot",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--profile",
            "examples/relay/profiles/localhost_readonly_profile_v0.json",
            "--check",
        ]
    )
    _run([sys.executable, "scripts/summarize_relay_runtime.py", "--input", "examples/relay", "--check"])
    blocked = _run(
        [
            sys.executable,
            "scripts/run_readonly_relay_fixture.py",
            "--snapshot",
            "examples/snapshots/fixtures/search_snapshot_input_v0.json",
            "--profile",
            "examples/relay/profiles/localhost_readonly_profile_v0.json",
            "--host",
            "0.0.0.0",
            "--check",
        ],
        expect_success=False,
    )
    if blocked.returncode == 0:
        raise AssertionError("server script accepted public bind host")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _run(
            [
                sys.executable,
                "scripts/render_relay_fixture.py",
                "--snapshot",
                "examples/snapshots/fixtures/search_snapshot_input_v0.json",
                "--profile",
                "examples/relay/profiles/localhost_readonly_profile_v0.json",
                "--route",
                "/terminal",
                "--render-profile",
                "terminal",
                "--output",
                str(tmp_path / "terminal.txt"),
            ]
        )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"validate_relay_runtime: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)


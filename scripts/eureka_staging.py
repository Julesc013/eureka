#!/usr/bin/env python3
"""Package and rehearse a local public-alpha staging bundle."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
from pathlib import Path
import sys
import threading
from typing import Any, Mapping, Sequence, TextIO
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.public_alpha_mvp import PublicAlphaService
from runtime.local.search_mvp import LocalSearchOptions, LocalSearchService
from runtime.local.staging_mvp import (
    MANIFEST_FILE,
    PUBLIC_INDEX_FILE,
    RUNTIME_CONFIG_FILE,
    bundle_id,
    bundle_status,
    package_bundle,
    public_index_path,
    render_status_text,
    validate_bundle,
)
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for


DEFAULT_BUNDLE_PATH = ".eureka/staging/public-alpha"
DEFAULT_QUERY = "manual for Sound Blaster CT1740"
REQUIRED_SMOKE_PATHS = (
    "/",
    "/health",
    "/status",
    "/api/status",
    "/about",
    "/method",
)
FORBIDDEN_PUBLIC_RESPONSE_MARKERS = (
    ".eureka",
    "local_review_ledger",
    "local_reviewed_records",
    "local_search_index",
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "C:\\",
    "D:\\",
    "/Users/",
    "\\Users\\",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    package_parser = subparsers.add_parser("package", help="Create a public-safe staging bundle.")
    package_parser.add_argument("--index", required=True, help="Reviewed local index to package.")
    package_parser.add_argument("--corpus-gate-closeout", default="", help="Optional public-safe corpus gate closeout directory.")
    package_parser.add_argument("--out", default=DEFAULT_BUNDLE_PATH, help="Output bundle directory.")
    package_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a staging bundle.")
    validate_parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH)
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print staging bundle status.")
    status_parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH)
    status_parser.add_argument("--json", action="store_true")

    smoke_parser = subparsers.add_parser("smoke", help="Run a local public-alpha route smoke from a bundle.")
    smoke_parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH)
    smoke_parser.add_argument("--host", default="127.0.0.1")
    smoke_parser.add_argument("--port", type=int, default=8765)
    smoke_parser.add_argument("--query", default=DEFAULT_QUERY)
    smoke_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "package":
        try:
            status = package_bundle(args.index, args.out, corpus_gate_closeout=args.corpus_gate_closeout or None)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"Staging package failed: {exc}", file=stderr)
            return 1
        if args.json:
            print(json.dumps(status, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"Packaged Eureka public-alpha staging bundle: {args.out}", file=stdout)
            _print_status(status, stdout)
        return 0 if status.get("status") == "pass" else 1

    if args.command == "validate":
        errors = validate_bundle(args.bundle)
        payload = {
            "schema_version": "eureka.local_staging_validate.v0",
            "status": "pass" if not errors else "fail",
            "bundle": str(args.bundle),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Staging bundle validation failed: {args.bundle}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Staging bundle validation passed: {args.bundle}", file=stdout)
        return 0 if not errors else 1

    if args.command == "status":
        status = bundle_status(args.bundle)
        if args.json:
            print(json.dumps(status, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"bundle: {args.bundle}", file=stdout)
            print(render_status_text(status), end="", file=stdout)
        return 0 if status.get("status") == "pass" else 1

    if args.command == "smoke":
        payload = smoke_bundle(args.bundle, host=args.host, port=args.port, query=args.query)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        else:
            print(f"status: {payload['status']}", file=stdout)
            print(f"bundle_id: {payload.get('bundle_id', '')}", file=stdout)
            print(f"base_url: {payload.get('base_url', '')}", file=stdout)
            print(f"route_count: {len(payload.get('routes') or [])}", file=stdout)
            print(f"workbench_disabled: {str(payload.get('workbench_disabled')).lower()}", file=stdout)
            print(f"read_only: {str(payload.get('read_only')).lower()}", file=stdout)
            print(f"live_metadata_enabled: {str(payload.get('live_metadata_enabled')).lower()}", file=stdout)
            print(f"hashes_unchanged: {str(payload.get('hashes_unchanged')).lower()}", file=stdout)
            print(f"errors: {json.dumps(payload.get('errors') or [])}", file=stdout)
        return 0 if payload.get("status") == "pass" else 1

    parser.error(f"unsupported command: {args.command}")
    return 2


def smoke_bundle(bundle: str | Path, *, host: str, port: int, query: str) -> dict[str, Any]:
    errors = validate_bundle(bundle)
    if errors:
        return _smoke_payload(bundle, host, port, "fail", errors=errors)
    if not _is_loopback_host(host):
        return _smoke_payload(bundle, host, port, "fail", errors=["staging smoke requires a loopback host"])

    index_path = public_index_path(bundle)
    before_hash = _sha256(index_path)
    options = LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none")
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
        route_results = []
        for path in REQUIRED_SMOKE_PATHS:
            route_results.append(_probe(host, actual_port, "GET", path))
        search_path = f"/search?q={quote(query)}"
        api_search_path = f"/api/search?q={quote(query)}"
        route_results.append(_probe(host, actual_port, "GET", search_path))
        api_search = _probe(host, actual_port, "GET", api_search_path)
        route_results.append(api_search)
        record_url = ""
        try:
            api_payload = json.loads(api_search["body"])
            record_url = str((api_payload.get("results") or [{}])[0].get("record_url") or "")
        except (json.JSONDecodeError, AttributeError, IndexError):
            api_payload = {}
        if record_url:
            route_results.append(_probe(host, actual_port, "GET", record_url))
        route_results.append(_probe(host, actual_port, "GET", "/workbench"))
        route_results.append(_probe(host, actual_port, "GET", "/workbench/api/status"))
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()

    after_hash = _sha256(index_path)
    status_payload = {}
    try:
        status_payload = json.loads(next(item["body"] for item in route_results if item["path"] == "/api/status"))
    except (StopIteration, json.JSONDecodeError):
        pass
    response_bodies = "\n".join(str(item.get("body") or "") for item in route_results)
    smoke_errors: list[str] = []
    for item in route_results:
        if item["path"].startswith("/workbench"):
            if item["status_code"] != 404:
                smoke_errors.append(f"{item['path']} should be disabled with 404")
        elif item["status_code"] != 200:
            smoke_errors.append(f"{item['path']} returned {item['status_code']}")
    if bool(status_payload.get("read_only")) is not True:
        smoke_errors.append("/api/status did not report read_only true")
    if bool(status_payload.get("live_metadata_enabled")) is True:
        smoke_errors.append("/api/status exposed live metadata")
    if bool(status_payload.get("workbench_exposed")) is True:
        smoke_errors.append("/api/status exposed Workbench")
    if bool(status_payload.get("public_live_fanout")) is True:
        smoke_errors.append("/api/status exposed public live fanout")
    if before_hash != after_hash:
        smoke_errors.append("public bundle index mutated during smoke")
    for marker in FORBIDDEN_PUBLIC_RESPONSE_MARKERS:
        if marker in response_bodies:
            smoke_errors.append(f"public response contains forbidden marker {marker}")

    return _smoke_payload(
        bundle,
        host,
        actual_port,
        "pass" if not smoke_errors else "fail",
        errors=smoke_errors,
        routes=[_route_summary(item) for item in route_results],
        record_url=record_url,
        read_only=bool(status_payload.get("read_only")),
        live_metadata_enabled=bool(status_payload.get("live_metadata_enabled")),
        workbench_disabled=all(item["status_code"] == 404 for item in route_results if item["path"].startswith("/workbench")),
        public_live_fanout=bool(status_payload.get("public_live_fanout")),
        hashes_unchanged=before_hash == after_hash,
    )


def _probe(host: str, port: int, method: str, path: str) -> dict[str, Any]:
    conn = http.client.HTTPConnection(host, port, timeout=8)
    try:
        conn.request(method, path)
        response = conn.getresponse()
        body = response.read().decode("utf-8", errors="replace")
        return {
            "method": method,
            "path": path,
            "status_code": response.status,
            "content_type": response.getheader("Content-Type") or "",
            "body": body,
        }
    finally:
        conn.close()


def _smoke_payload(
    bundle: str | Path,
    host: str,
    port: int,
    status: str,
    *,
    errors: Sequence[str],
    routes: Sequence[Mapping[str, Any]] = (),
    record_url: str = "",
    read_only: bool = False,
    live_metadata_enabled: bool = False,
    workbench_disabled: bool = False,
    public_live_fanout: bool = False,
    hashes_unchanged: bool = False,
) -> dict[str, Any]:
    return {
        "schema_version": "eureka.local_staging_smoke.v0",
        "status": status,
        "bundle": str(bundle),
        "bundle_id": bundle_id(bundle) if Path(bundle).is_dir() else "",
        "base_url": f"http://{host}:{port}",
        "read_only": read_only,
        "live_metadata_enabled": live_metadata_enabled,
        "workbench_disabled": workbench_disabled,
        "public_live_fanout": public_live_fanout,
        "hashes_unchanged": hashes_unchanged,
        "record_url": record_url,
        "routes": list(routes),
        "errors": list(errors),
    }


def _route_summary(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "method": item.get("method"),
        "path": item.get("path"),
        "status_code": item.get("status_code"),
        "content_type": item.get("content_type"),
        "sample": str(item.get("body") or "")[:160].replace("\n", " "),
    }


def _print_status(status: Mapping[str, Any], stdout: TextIO) -> None:
    print(f"bundle_id: {status.get('bundle_id')}", file=stdout)
    print(f"document_count: {status.get('document_count')}", file=stdout)
    print(f"status_counts: {json.dumps(status.get('status_counts') or {}, sort_keys=True)}", file=stdout)
    print(f"reviewed_record_count: {status.get('reviewed_record_count')}", file=stdout)
    print(f"artifact_verified_count: {status.get('artifact_verified_count')}", file=stdout)
    print(f"corpus_gate_status: {status.get('corpus_gate_status')}", file=stdout)
    print(f"reviewed_artifact_gate_count: {status.get('reviewed_artifact_gate_count')}", file=stdout)
    print(f"public_artifact_identity_record_count: {status.get('public_artifact_identity_record_count')}", file=stdout)
    print(f"binary_verified_count: {status.get('binary_verified_count')}", file=stdout)
    print(f"download_safe_count: {status.get('download_safe_count')}", file=stdout)
    print(f"execution_safe_count: {status.get('execution_safe_count')}", file=stdout)
    print(f"rights_cleared_count: {status.get('rights_cleared_count')}", file=stdout)
    print(f"read_only: {str(status.get('read_only')).lower()}", file=stdout)
    print(f"live_metadata_enabled: {str(status.get('live_metadata_enabled')).lower()}", file=stdout)
    print(f"workbench_exposed: {str(status.get('workbench_exposed')).lower()}", file=stdout)
    print(f"public_index_digest: {status.get('public_index_digest')}", file=stdout)


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _is_loopback_host(host: str) -> bool:
    normalized = str(host or "").strip().casefold()
    return normalized in {"localhost", "::1"} or normalized.startswith("127.")


if __name__ == "__main__":
    raise SystemExit(main())

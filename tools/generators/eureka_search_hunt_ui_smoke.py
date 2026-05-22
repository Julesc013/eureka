#!/usr/bin/env python3
"""Smoke test read-only Search Hunt workbench pages."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
FORBIDDEN_HOSTS = {"0.0.0.0", "::", "", "*"}
MISSING_HUNT_ID = "nonexistent-hunt-ui-smoke"
HTML_MARKERS = {
    "/hunts": (
        "Search Hunts",
        "Search Hunt Sessions are local investigation state",
        "Unavailable next actions",
    ),
    f"/hunt/{MISSING_HUNT_ID}": (
        "Search Hunt not found",
        "created_implicitly",
        "Missing hunt IDs are never created implicitly",
    ),
}
FORBIDDEN_HTML = (
    "<script",
    "javascript:",
    "method=\"post\"",
    "formmethod=\"post\"",
    "src=\"http://",
    "src=\"https://",
    "href=\"http://",
    "href=\"https://",
    "production ready",
    "public launch ready",
    "rights cleared",
    "malware safe",
    "exhaustive search performed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--instance", help="Optional initialized instance used to seed one sample hunt.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        base_url = validate_base_url(args.base_url)
        if args.instance:
            seed_sample_hunt(Path(args.instance))
        result = run_smoke(base_url)
    except ValueError as exc:
        result = fail_result("base_url_rejected", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("hunt_ui_smoke_failed", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def run_smoke(base_url: str) -> dict[str, Any]:
    html_routes = {
        "/hunts": fetch_html(base_url, "/hunts"),
        f"/hunt/{MISSING_HUNT_ID}": fetch_html(base_url, f"/hunt/{MISSING_HUNT_ID}", expected_statuses=(404,)),
    }
    api_list = fetch_json(base_url, "/api/v1/hunts")
    api_missing = fetch_json(base_url, f"/api/v1/hunt/{MISSING_HUNT_ID}", expected_statuses=(404,))
    detail_html: dict[str, Any] | None = None
    detail_api: dict[str, Any] | None = None
    hunt_id = first_hunt_id(api_list.get("payload"))
    if hunt_id:
        detail_html = fetch_html(base_url, f"/hunt/{hunt_id}", expected_markers=("Search Hunt Session", "Transition history", "Checked layers"))
        detail_api = fetch_json(base_url, f"/api/v1/hunt/{hunt_id}")
        html_routes["/hunt/<hunt_id>"] = detail_html
    html_ok = all(route.get("ok") for route in html_routes.values())
    api_ok = bool(api_list.get("ok") and api_missing.get("ok") and (detail_api is None or detail_api.get("ok")))
    return {
        "schema_version": "search_hunt_ui_smoke_result.v0",
        "status": "pass" if html_ok and api_ok else "fail",
        "base_url": base_url,
        "html_routes": html_routes,
        "api_routes": {
            "/api/v1/hunts": api_list,
            f"/api/v1/hunt/{MISSING_HUNT_ID}": api_missing,
            "/api/v1/hunt/<hunt_id>": detail_api or {"ok": True, "skipped": "no hunt present"},
        },
        "hunt_list_page_passed": bool(html_routes["/hunts"].get("ok")),
        "hunt_detail_page_passed": bool(detail_html.get("ok")) if detail_html else bool(hunt_id is None),
        "hunt_json_routes_passed": api_ok,
        "hunt_not_found_state_passed": bool(html_routes[f"/hunt/{MISSING_HUNT_ID}"].get("ok") and api_missing.get("ok")),
        "non_claim_banner_present": "Local appliance prototype" in str(html_routes["/hunts"].get("body_excerpt", "")),
        "mutation_controls_found": any(route.get("mutation_controls_found") for route in html_routes.values()),
        "external_assets_found": any(route.get("external_assets_found") for route in html_routes.values()),
        "forbidden_claims_found": any(route.get("forbidden_claims_found") for route in html_routes.values()),
        "hunt_creation_performed": False,
        "hunt_transition_performed": False,
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": ["loopback-only smoke; external clients are not used"],
    }


def seed_sample_hunt(instance: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "eureka_search_hunt.py"),
            "--instance",
            str(instance),
            "create",
            "--query",
            "sampleproject",
            "--idempotency-key",
            "hunt-ui-smoke-sample",
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or "sample hunt creation failed")


def fetch_html(
    base_url: str,
    path: str,
    *,
    expected_statuses: tuple[int, ...] = (200,),
    expected_markers: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    result = fetch(base_url, path, "text/html")
    body = str(result.get("body", ""))
    markers = expected_markers or HTML_MARKERS.get(path, ())
    lowered = body.lower()
    post_form = any(item in lowered for item in ("method=\"post\"", "formmethod=\"post\""))
    safe_operator_controls = (
        post_form
        and "operator state controls" in lowered
        and "operator token" in lowered
        and "lan clients cannot use command routes" in lowered
        and "workunit_creation_enabled" in lowered
        and "source_probe_execution_enabled" in lowered
        and "model_provider_enabled" in lowered
    )
    mutation = any(item in lowered for item in ("create hunt", "transition hunt", "create workunit")) or (post_form and not safe_operator_controls)
    external = any(item in lowered for item in ("src=\"http://", "src=\"https://", "href=\"http://", "href=\"https://"))
    forbidden_claim = any(item in lowered for item in FORBIDDEN_HTML if item not in {"<script", "javascript:", "method=\"post\"", "formmethod=\"post\"", "src=\"http://", "src=\"https://", "href=\"http://", "href=\"https://"})
    result.update(
        {
            "ok": int(result.get("status_code", 0)) in expected_statuses
            and "text/html" in str(result.get("content_type", ""))
            and all(marker in body for marker in markers)
            and not mutation
            and not external
            and not forbidden_claim,
            "mutation_controls_found": mutation,
            "external_assets_found": external,
            "forbidden_claims_found": forbidden_claim,
            "body_excerpt": body[:500],
        }
    )
    result.pop("body", None)
    return result


def fetch_json(base_url: str, path: str, *, expected_statuses: tuple[int, ...] = (200,)) -> dict[str, Any]:
    result = fetch(base_url, path, "application/json")
    payload = parse_json(str(result.get("body", "")))
    result.update(
        {
            "payload": payload,
            "ok": int(result.get("status_code", 0)) in expected_statuses
            and "application/json" in str(result.get("content_type", ""))
            and isinstance(payload, dict),
        }
    )
    result.pop("body", None)
    return result


def fetch(base_url: str, path: str, accept: str) -> dict[str, Any]:
    request = Request(build_url(base_url, path), method="GET", headers={"Accept": accept})
    try:
        with urlopen(request, timeout=5) as response:
            return {
                "url": build_url(base_url, path),
                "status_code": int(response.getcode()),
                "content_type": str(response.headers.get("Content-Type", "")),
                "body": response.read().decode("utf-8"),
            }
    except HTTPError as exc:
        return {
            "url": build_url(base_url, path),
            "status_code": int(exc.code),
            "content_type": str(exc.headers.get("Content-Type", "")),
            "body": exc.read().decode("utf-8"),
        }
    except URLError as exc:
        return {"url": build_url(base_url, path), "status_code": 0, "content_type": "", "body": "", "error": str(exc)}


def first_hunt_id(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    hunts = payload.get("hunts")
    if not isinstance(hunts, list) or not hunts:
        return ""
    first = hunts[0]
    return str(first.get("id", "")) if isinstance(first, dict) else ""


def validate_base_url(base_url: str) -> str:
    split = urlsplit(base_url)
    if split.scheme != "http":
        raise ValueError("only http loopback URLs are supported")
    host = (split.hostname or "").lower()
    if host in FORBIDDEN_HOSTS or host not in ALLOWED_HOSTS:
        raise ValueError("base-url must use 127.0.0.1 or localhost")
    if not split.port:
        raise ValueError("base-url must include an explicit port")
    return urlunsplit((split.scheme, split.netloc, split.path.rstrip("/"), "", ""))


def build_url(base_url: str, path: str) -> str:
    return urlunsplit(("http", urlsplit(base_url).netloc, path, "", ""))


def parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def fail_result(code: str, message: str, base_url: str) -> dict[str, Any]:
    return {
        "schema_version": "search_hunt_ui_smoke_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "base_url": base_url,
        "external_network_used": False,
        "source_probe_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

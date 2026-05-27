from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO
from urllib.parse import urlencode

from runtime.gateway.public_api import (
    build_demo_public_alpha_readonly_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WebServerConfig, WorkbenchWsgiApp


REPO_ROOT = Path(__file__).resolve().parents[2]
UNSAFE_FALSE_FIELDS = (
    "mutation_enabled",
    "live_source_actions_enabled",
    "download_enabled",
    "upload_enabled",
    "install_enabled",
    "execution_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "master_index_mutated",
    "data_public_index_mutated",
)


def validate_public_alpha_readonly() -> dict[str, Any]:
    errors: list[str] = []
    api = build_demo_public_alpha_readonly_api()

    status = api.status({}).body
    _check_envelope("status", status, errors)
    if status.get("public_alpha_readonly_implemented") is not True:
        errors.append("status.public_alpha_readonly_implemented must be true")

    search_response = api.search({"q": ["sampleproject"]})
    search = search_response.body
    _check_envelope("search", search, errors)
    if search_response.status_code != 200:
        errors.append("sample search must return HTTP 200")
    if search.get("result_count") != 1:
        errors.append("sample search must return one reviewed snapshot record")
    if search.get("relay_query_response", {}).get("read_only") is not True:
        errors.append("search relay_query_response.read_only must be true")

    absence = api.search({"q": ["not present in reviewed snapshot"]}).body
    if absence.get("result_count") != 0:
        errors.append("unknown search must return zero results")
    if not absence.get("absence_summaries"):
        errors.append("unknown search must include absence summaries")
    if not absence.get("known_needs"):
        errors.append("unknown search must include known needs")

    blocked = api.search({"q": ["sampleproject"], "download": ["1"]}).body
    if blocked.get("error", {}).get("code") != "downloads_disabled":
        errors.append("download query parameter must be blocked")
    if blocked.get("download_enabled") is not False:
        errors.append("blocked response must keep download_enabled=false")

    object_packet = api.object("sampleproject").body
    _check_envelope("object", object_packet, errors)
    if "private_notes" in object_packet.get("record", {}):
        errors.append("object packet must not include private_notes")
    if not object_packet.get("source_summaries"):
        errors.append("object packet must include source summaries")
    if not object_packet.get("evidence_summaries"):
        errors.append("object packet must include evidence summaries")

    source = api.source_summary("source-summary-sampleproject-001").body
    evidence = api.evidence_summary("evidence-summary-sampleproject-001").body
    if source.get("source_summary", {}).get("raw_response_included") is not False:
        errors.append("source summary must not include raw responses")
    if evidence.get("evidence_summary", {}).get("raw_evidence_blob_included") is not False:
        errors.append("evidence summary must not include raw evidence blobs")

    route_errors = _validate_routes()
    errors.extend(route_errors)

    return {
        "schema_version": "public_alpha_readonly_validation.v0",
        "task": "PUBLIC-ALPHA-READONLY-00",
        "status": "valid" if not errors else "invalid",
        "mode": "reviewed_snapshot_read_only",
        "snapshot_id": status.get("snapshot", {}).get("snapshot_id"),
        "relay_id": status.get("relay", {}).get("relay_id"),
        "result_count": search.get("result_count"),
        "absence_summary_count": len(absence.get("absence_summaries", [])),
        "known_need_count": len(absence.get("known_needs", [])),
        "errors": errors,
    }


def _check_envelope(label: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "ok": True,
        "mode": "reviewed_snapshot_read_only",
        "read_only": True,
        "reviewed_index_only": True,
        "snapshot_backed": True,
        "relay_backed": True,
    }
    for key, value in expected.items():
        if payload.get(key) is not value:
            errors.append(f"{label}.{key} must be {value!r}")
    for field in UNSAFE_FALSE_FIELDS:
        if payload.get(field) is not False:
            errors.append(f"{label}.{field} must be false")


def _validate_routes() -> list[str]:
    errors: list[str] = []
    app = WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        search_public_api=build_demo_search_public_api(),
        public_alpha_readonly_api=build_demo_public_alpha_readonly_api(),
        default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        server_config=WebServerConfig.public_alpha(),
    )
    for path, query, expected_status in (
        ("/api/v1/alpha/status", {}, "200 OK"),
        ("/api/v1/alpha/search", {"q": "sampleproject"}, "200 OK"),
        ("/api/v1/alpha/object/sampleproject", {}, "200 OK"),
        ("/api/v1/alpha/needs", {}, "200 OK"),
        ("/alpha", {"q": "sampleproject"}, "200 OK"),
        ("/alpha/object", {"id": "sampleproject"}, "200 OK"),
    ):
        status, _headers, _body = _request(app, path, query)
        if status != expected_status:
            errors.append(f"{path} expected {expected_status}, got {status}")
    status, _headers, body = _request(
        app,
        "/api/v1/alpha/search",
        {"q": "sampleproject", "download": "1"},
    )
    if status != "400 Bad Request":
        errors.append("download-block route expected 400 Bad Request")
    else:
        payload = json.loads(body)
        if payload.get("error", {}).get("code") != "downloads_disabled":
            errors.append("download-block route must return downloads_disabled")
    return errors


def _request(
    app: WorkbenchWsgiApp,
    path: str,
    query: Mapping[str, str],
) -> tuple[str, dict[str, str], str]:
    captured: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = headers

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": "GET",
                "PATH_INFO": path,
                "QUERY_STRING": urlencode(query),
                "wsgi.input": BytesIO(b""),
            },
            start_response,
        )
    )
    return str(captured["status"]), dict(captured["headers"]), body.decode("utf-8")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PUBLIC-ALPHA-READONLY-00.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_alpha_readonly()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(f"public alpha read-only validation: {report['status']}\n")
        for error in report["errors"]:
            output.write(f"ERROR: {error}\n")
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
